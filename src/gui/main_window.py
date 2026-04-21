import sys
import json
import collections
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QComboBox, QPushButton, QLabel, QTextEdit, 
    QLineEdit, QSpinBox, QDoubleSpinBox, QMessageBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QPalette

from src.core.serial_manager import SerialManager
from src.core.threads import ReaderThread, AutoBaudThread, RepeaterThread
from src.utils.logger import DataLogger

HYPRLAND_STYLE = """
QMainWindow {
    background-color: #1e1e2e; /* Catppuccin Macchiato Base */
    color: #cdd6f4;
}
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "Fira Code", monospace;
    font-size: 10pt;
}
QGroupBox {
    border: 2px solid #89b4fa; /* Blue neon border */
    border-radius: 8px;
    margin-top: 10px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px;
    color: #89b4fa;
}
QPushButton {
    background-color: #313244;
    border: 1px solid #89b4fa;
    border-radius: 4px;
    padding: 6px 12px;
    color: #89b4fa;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QPushButton:pressed {
    background-color: #74c7ec;
    border: 1px solid #74c7ec;
}
QPushButton:disabled {
    background-color: #313244;
    border: 1px solid #585b70;
    color: #585b70;
}
QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
    background-color: #181825;
    border: 1px solid #585b70;
    border-radius: 4px;
    padding: 4px;
    color: #cdd6f4;
}
QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #f38ba8; /* Pink neon on focus */
}
QTextEdit {
    background-color: #11111b;
    border: 2px solid #cba6f7; /* Mauve neon */
    border-radius: 8px;
    padding: 5px;
    color: #a6e3a1; /* Green text for terminal */
    font-family: "Consolas", "Courier New", monospace;
}
QLabel {
    color: #bac2de;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oh-My-Port 🚀")
        self.resize(800, 600)
        self.setStyleSheet(HYPRLAND_STYLE)

        self.serial_manager = SerialManager()
        self.logger = DataLogger()
        self.reader_thread = None
        self.auto_baud_thread = None
        self.repeater_thread = None

        # --- Real-time display buffer ---
        # Data from the reader thread is accumulated here (thread-safe deque).
        # A QTimer flushes it to the UI at a fixed ~30fps to avoid per-byte redraws.
        self._display_buffer = collections.deque()
        self._flush_timer = QTimer(self)
        self._flush_timer.setInterval(33)  # ~30fps
        self._flush_timer.timeout.connect(self._flush_display_buffer)

        self.setup_ui()
        self.scan_ports()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Top Panel: Connection ---
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QHBoxLayout()

        self.cb_ports = QComboBox()
        self.cb_ports.setMinimumWidth(150)
        btn_scan = QPushButton("Scan Ports")
        btn_scan.clicked.connect(self.scan_ports)

        self.cb_baud = QComboBox()
        self.cb_baud.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.cb_baud.setCurrentText("115200")

        self.btn_auto_baud = QPushButton("Auto Detect Baud")
        self.btn_auto_baud.clicked.connect(self.auto_detect_baud)

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.toggle_connection)

        conn_layout.addWidget(QLabel("Port:"))
        conn_layout.addWidget(self.cb_ports)
        conn_layout.addWidget(btn_scan)
        conn_layout.addWidget(QLabel("Baud Rate:"))
        conn_layout.addWidget(self.cb_baud)
        conn_layout.addWidget(self.btn_auto_baud)
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addStretch()
        conn_group.setLayout(conn_layout)

        # --- Middle Panel: Terminal ---
        terminal_group = QGroupBox("Terminal (Listen Mode)")
        term_layout = QVBoxLayout()
        self.text_terminal = QTextEdit()
        self.text_terminal.setReadOnly(True)
        
        term_ctrl_layout = QHBoxLayout()
        self.chk_hex_view = QCheckBox("Hex View")
        btn_clear = QPushButton("Clear Terminal")
        btn_clear.clicked.connect(self.text_terminal.clear)
        term_ctrl_layout.addWidget(self.chk_hex_view)
        term_ctrl_layout.addWidget(btn_clear)
        term_ctrl_layout.addStretch()

        term_layout.addWidget(self.text_terminal)
        term_layout.addLayout(term_ctrl_layout)
        terminal_group.setLayout(term_layout)

        # --- Bottom Panel: Send ---
        send_group = QGroupBox("Send Mode")
        send_layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.line_input = QLineEdit()
        self.line_input.setPlaceholderText("Enter data to send...")
        
        self.cb_format = QComboBox()
        self.cb_format.addItems(["Text (\\r\\n)", "Text (Raw)", "JSON"])

        self.btn_send = QPushButton("Send")
        self.btn_send.clicked.connect(self.send_data)
        self.btn_send.setEnabled(False)

        input_layout.addWidget(self.line_input)
        input_layout.addWidget(self.cb_format)
        input_layout.addWidget(self.btn_send)

        repeat_layout = QHBoxLayout()
        repeat_layout.addWidget(QLabel("Repeat N Times:"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(1, 100000)
        self.spin_n.setValue(1)
        repeat_layout.addWidget(self.spin_n)

        repeat_layout.addWidget(QLabel("Frequency (Hz):"))
        self.spin_freq = QDoubleSpinBox()
        self.spin_freq.setRange(0.1, 1000.0)
        self.spin_freq.setValue(1.0)
        repeat_layout.addWidget(self.spin_freq)

        self.btn_burst = QPushButton("Burst Send")
        self.btn_burst.clicked.connect(self.burst_send)
        self.btn_burst.setEnabled(False)
        repeat_layout.addWidget(self.btn_burst)
        repeat_layout.addStretch()

        send_layout.addLayout(input_layout)
        send_layout.addLayout(repeat_layout)
        send_group.setLayout(send_layout)

        main_layout.addWidget(conn_group)
        main_layout.addWidget(terminal_group)
        main_layout.addWidget(send_group)

    def log_terminal(self, msg, color="#a6e3a1"):
        """Append message to terminal UI"""
        self.text_terminal.setTextColor(QColor(color))
        self.text_terminal.insertPlainText(msg)
        self.text_terminal.moveCursor(self.text_terminal.textCursor().MoveOperation.End)

    def scan_ports(self):
        self.cb_ports.clear()
        ports = self.serial_manager.get_available_ports()
        if ports:
            self.cb_ports.addItems(ports)
        else:
            self.cb_ports.addItem("None")

    def toggle_connection(self):
        if self.serial_manager.is_connected():
            self.disconnect_port()
        else:
            self.connect_port()

    def connect_port(self):
        port = self.cb_ports.currentText()
        if port == "None" or not port:
            QMessageBox.warning(self, "Error", "No port selected!")
            return

        baud = int(self.cb_baud.currentText())
        success, msg = self.serial_manager.connect(port, baud)
        if success:
            self.btn_connect.setText("Disconnect")
            self.btn_connect.setStyleSheet("background-color: #f38ba8; color: #1e1e2e;")
            self.btn_send.setEnabled(True)
            self.btn_burst.setEnabled(True)
            self.log_terminal(f"\n[System] Connected to {port} @ {baud} baud\n", "#89dceb")
            
            # Start reader thread
            self.reader_thread = ReaderThread(self.serial_manager)
            self.reader_thread.data_received.connect(self.on_data_received)
            self.reader_thread.error_occurred.connect(self.on_reader_error)
            self.reader_thread.start()
            self._flush_timer.start()
        else:
            QMessageBox.critical(self, "Connection Error", msg)

    def disconnect_port(self):
        self._flush_timer.stop()
        self._display_buffer.clear()

        if self.reader_thread:
            self.reader_thread.stop()
            self.reader_thread = None

        if self.repeater_thread:
            self.repeater_thread.stop()
            self.repeater_thread = None

        self.serial_manager.disconnect()
        self.btn_connect.setText("Connect")
        self.btn_connect.setStyleSheet("")
        self.btn_send.setEnabled(False)
        self.btn_burst.setEnabled(False)
        self.log_terminal("\n[System] Disconnected\n", "#f38ba8")

    @pyqtSlot(bytes)
    def on_data_received(self, data):
        """Called from the reader thread via Qt signal. Buffers data instead of
        updating the widget directly, so the UI is never overwhelmed."""
        self.logger.log(data, direction="RX")
        
        if self.chk_hex_view.isChecked():
            display_text = data.hex(' ') + " "
        else:
            try:
                display_text = data.decode('utf-8', errors='replace')
            except Exception:
                display_text = str(data)

        # Push to deque; _flush_display_buffer() will pick it up on the next timer tick
        self._display_buffer.append(display_text)

    def _flush_display_buffer(self):
        """Called by QTimer every ~33ms. Batches all pending text into a single
        widget update, keeping the UI smooth regardless of incoming data rate."""
        if not self._display_buffer:
            return

        # Collect everything currently in the buffer atomically
        chunks = []
        while self._display_buffer:
            chunks.append(self._display_buffer.popleft())

        combined = "".join(chunks)
        self.log_terminal(combined, "#a6e3a1")

    @pyqtSlot(str)
    def on_reader_error(self, err):
        self.log_terminal(f"\n[Reader Error] {err}\n", "#f38ba8")
        self.disconnect_port()

    def auto_detect_baud(self):
        port = self.cb_ports.currentText()
        if port == "None" or not port:
            QMessageBox.warning(self, "Error", "Select a port first!")
            return

        if self.serial_manager.is_connected():
            self.disconnect_port()

        self.btn_auto_baud.setEnabled(False)
        self.btn_connect.setEnabled(False)
        
        self.auto_baud_thread = AutoBaudThread(self.serial_manager, port)
        self.auto_baud_thread.log_msg.connect(lambda msg: self.log_terminal(f"\n[Auto-Baud] {msg}", "#f9e2af"))
        self.auto_baud_thread.baud_found.connect(self.on_baud_found)
        self.auto_baud_thread.finished_scan.connect(self.on_auto_baud_finished)
        self.auto_baud_thread.start()

    @pyqtSlot(int)
    def on_baud_found(self, baud):
        self.cb_baud.setCurrentText(str(baud))

    @pyqtSlot()
    def on_auto_baud_finished(self):
        self.btn_auto_baud.setEnabled(True)
        self.btn_connect.setEnabled(True)
        self.auto_baud_thread = None

    def _prepare_data(self):
        text = self.line_input.text()
        fmt = self.cb_format.currentText()
        
        if fmt == "JSON":
            try:
                # Validate JSON
                parsed = json.loads(text)
                text = json.dumps(parsed) + "\r\n"
            except json.JSONDecodeError:
                QMessageBox.warning(self, "JSON Error", "Invalid JSON format!")
                return None
        elif fmt == "Text (\\r\\n)":
            text += "\r\n"
            
        return text

    def send_data(self):
        text = self._prepare_data()
        if text is None: return

        if self.serial_manager.write(text):
            self.logger.log(text, direction="TX")
            self.log_terminal(f"\n[TX] {text.strip()}\n", "#f5c2e7")
        else:
            QMessageBox.critical(self, "Error", "Failed to send data.")

    def burst_send(self):
        text = self._prepare_data()
        if text is None: return

        n = self.spin_n.value()
        freq = self.spin_freq.value()

        self.btn_burst.setEnabled(False)
        self.repeater_thread = RepeaterThread(self.serial_manager, text, n, freq)
        self.repeater_thread.send_tick.connect(lambda: self.log_terminal(".", "#f5c2e7"))
        self.repeater_thread.finished.connect(self.on_burst_finished)
        self.repeater_thread.start()

    @pyqtSlot()
    def on_burst_finished(self):
        self.log_terminal("\n[System] Burst send complete.\n", "#89dceb")
        self.btn_burst.setEnabled(True)
        self.repeater_thread = None

    def closeEvent(self, event):
        """Handle window close event to cleanly stop background threads."""
        self.disconnect_port()
        self.logger.stop()
        event.accept()

import time
from PyQt6.QtCore import QThread, pyqtSignal
from src.core.serial_manager import SerialManager

# How long to sleep (seconds) when no bytes are available.
# Short enough to be responsive, long enough to not spin at 100% CPU.
_POLL_INTERVAL = 0.005  # 5ms


class ReaderThread(QThread):
    data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)

    def __init__(self, serial_manager: SerialManager):
        super().__init__()
        self.serial_manager = serial_manager
        self.running = True

    def run(self):
        while self.running:
            if not self.serial_manager.is_connected():
                time.sleep(0.05)
                continue
            try:
                waiting = self.serial_manager.in_waiting
                if waiting > 0:
                    # Read exactly what's available – zero blocking wait
                    data = self.serial_manager.read(waiting)
                    if data:
                        self.data_received.emit(data)
                else:
                    # Nothing waiting; yield CPU briefly
                    time.sleep(_POLL_INTERVAL)
            except Exception as e:
                self.error_occurred.emit(str(e))
                time.sleep(1)

    def stop(self):
        self.running = False
        self.wait()




class AutoBaudThread(QThread):
    baud_found = pyqtSignal(int)
    log_msg = pyqtSignal(str)
    finished_scan = pyqtSignal()

    def __init__(self, serial_manager: SerialManager, port: str):
        super().__init__()
        self.serial_manager = serial_manager
        self.port = port
        self.running = True
        self.standard_bauds = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]

    def run(self):
        self.log_msg.emit(f"Starting auto-baud detection on {self.port}...")
        found = False
        for baud in self.standard_bauds:
            if not self.running:
                break
            self.log_msg.emit(f"Testing {baud}...")
            
            # Temporarily disconnect if connected
            self.serial_manager.disconnect()
            success, msg = self.serial_manager.connect(self.port, baud, timeout=1.0)
            if not success:
                self.log_msg.emit(f"Failed to open port at {baud}.")
                continue
            
            # Read a chunk of data
            data = self.serial_manager.read(256)
            if data:
                # Check if it looks like valid ASCII/JSON without garbage
                try:
                    text = data.decode('utf-8')
                    # Basic heuristic: mostly printable characters
                    printable = sum(1 for c in text if c.isprintable() or c in '\r\n\t')
                    if len(text) > 0 and (printable / len(text)) > 0.9:
                        self.log_msg.emit(f"Valid data detected at {baud}!")
                        self.baud_found.emit(baud)
                        found = True
                        break
                except UnicodeDecodeError:
                    pass
            
            time.sleep(0.1)

        if not found and self.running:
            self.log_msg.emit("Auto-baud detection failed. Please select manually.")
        
        self.serial_manager.disconnect()
        self.finished_scan.emit()

    def stop(self):
        self.running = False
        self.wait()


class RepeaterThread(QThread):
    send_tick = pyqtSignal()
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, serial_manager: SerialManager, data: str, count: int, freq_hz: float):
        super().__init__()
        self.serial_manager = serial_manager
        self.data = data
        self.count = count
        self.freq_hz = freq_hz
        self.running = True

    def run(self):
        delay = 1.0 / self.freq_hz if self.freq_hz > 0 else 0
        for i in range(self.count):
            if not self.running:
                break
            
            success = self.serial_manager.write(self.data)
            if success:
                self.send_tick.emit()
            else:
                self.error_occurred.emit("Failed to send data.")
                break
            
            if delay > 0:
                time.sleep(delay)
                
        self.finished.emit()

    def stop(self):
        self.running = False
        self.wait()

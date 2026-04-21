import serial
import serial.tools.list_ports

class SerialManager:
    def __init__(self):
        self.port = None
        self.baudrate = 9600
        self.serial_instance = None

    def get_available_ports(self):
        """Returns a list of available COM ports."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect(self, port, baudrate, timeout=0.05):
        """Connects to a given port and baudrate."""
        if self.serial_instance and self.serial_instance.is_open:
            self.disconnect()
        
        try:
            self.serial_instance = serial.Serial(port, baudrate, timeout=timeout)
            self.port = port
            self.baudrate = baudrate
            return True, "Connected successfully"
        except serial.SerialException as e:
            return False, str(e)

    def disconnect(self):
        """Disconnects from the current port."""
        if self.serial_instance and self.serial_instance.is_open:
            self.serial_instance.close()
            self.serial_instance = None
            self.port = None
            return True
        return False

    def is_connected(self):
        return self.serial_instance is not None and self.serial_instance.is_open

    def write(self, data):
        """Writes data to the serial port."""
        if self.is_connected():
            if isinstance(data, str):
                data = data.encode('utf-8')
            try:
                self.serial_instance.write(data)
                return True
            except serial.SerialException:
                return False
        return False

    @property
    def in_waiting(self):
        """Returns the number of bytes currently in the receive buffer."""
        if self.is_connected():
            try:
                return self.serial_instance.in_waiting
            except serial.SerialException:
                return 0
        return 0

    def read(self, size=4096):
        """Reads up to `size` bytes from the serial port (non-blocking)."""
        if self.is_connected():
            try:
                return self.serial_instance.read(size)
            except serial.SerialException:
                return None
        return None

    def readline(self):
        """Reads a line from the serial port."""
        if self.is_connected():
            try:
                return self.serial_instance.readline()
            except serial.SerialException:
                return None
        return None

import os
import time
import threading
import queue

class DataLogger:
    def __init__(self):
        self.doc_dir = os.path.expanduser('~/Documents/oh-my-port')
        os.makedirs(self.doc_dir, exist_ok=True)
        
        # Create a unique filename for each run
        filename = time.strftime('log_%Y%m%d_%H%M%S.txt')
        self.filepath = os.path.join(self.doc_dir, filename)
        
        self.log_queue = queue.Queue()
        self.running = True
        self.worker_thread = threading.Thread(target=self._log_worker, daemon=True)
        self.worker_thread.start()

    def _log_worker(self):
        """Background thread that writes to the file to prevent UI lag."""
        with open(self.filepath, 'a', encoding='utf-8') as f:
            while self.running or not self.log_queue.empty():
                try:
                    log_line = self.log_queue.get(timeout=0.1)
                    f.write(log_line)
                    f.flush()  # Ensure data is written to disk immediately
                except queue.Empty:
                    continue

    def log(self, data, direction="RX", format="text"):
        """
        Queues data to be logged.
        direction: "RX" or "TX"
        format: "text", "hex", etc.
        """
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        if isinstance(data, bytes):
            try:
                text_data = data.decode('utf-8', errors='replace')
            except Exception:
                text_data = data.hex()
        else:
            text_data = str(data)
        
        # Simple format: [TIMESTAMP] [RX/TX] Data
        log_line = f"[{timestamp}] [{direction}] {text_data}\n"
        self.log_queue.put(log_line)

    def stop(self):
        """Signals the logging thread to finish remaining items and exit."""
        self.running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)

    def set_filename(self, filename):
        pass # Ignored since we generate unique names

    def clear(self):
        pass # Not applicable for per-run files

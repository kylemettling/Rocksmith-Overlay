import socket
import time
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    filename='rocksmith_overlay.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RockSnifferReader:
    def __init__(self, host="localhost", port=9938, retry_interval=5, max_retries=5):
        self.host = host
        self.port = port
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.sock = None

    def connect(self):
        """Attempt to connect to RockSniffer with retries."""
        retries = 0
        while retries < self.max_retries:
            try:
                self.sock = socket.create_connection((self.host, self.port), timeout=10)
                logger.info(f"Connected to RockSniffer at {self.host}:{self.port}")
                return True
            except (ConnectionError, socket.timeout) as e:
                retries += 1
                logger.error(f"Connection failed: {e}. Retrying ({retries}/{self.max_retries}) in {self.retry_interval}s...")
                time.sleep(self.retry_interval)
        logger.critical("Failed to connect to RockSniffer after max retries.")
        return False

    def read_data(self):
        """Read and parse data from RockSniffer."""
        if not self.sock and not self.connect():
            return None

        try:
            data = self.sock.recv(1024).decode('utf-8')
            if not data:
                logger.warning("No data received, connection may have closed.")
                self.close()
                return None
            logger.info(f"Received raw data: {data}")
            parsed_data = json.loads(data)  # Assuming RockSniffer sends JSON
            return parsed_data
        except (socket.error, json.JSONDecodeError, ConnectionError) as e:
            logger.error(f"Error reading RockSniffer data: {e}")
            self.close()
            return None
        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            self.close()
            return None

    def close(self):
        """Close the socket connection."""
        if self.sock:
            self.sock.close()
            logger.info("Socket closed.")
            self.sock = None

    def __del__(self):
        """Ensure socket is closed on object destruction."""
        self.close()

# Example usage for testing
if __name__ == "__main__":
    reader = RockSnifferReader()
    while True:
        data = reader.read_data()
        if data:
            print(f"Processed data: {data}")
        else:
            print("Failed to read data, retrying...")
        time.sleep(1)  # Adjust polling interval
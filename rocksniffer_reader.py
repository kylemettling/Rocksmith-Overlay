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
        if not self.sock and not self.connect():
            return {"song": "N/A", "artist": "N/A", "album": "N/A", "hitrate": 0.0}

        try:
            data = self.sock.recv(1024).decode('utf-8')
            if not data:
                logger.warning("No data received, connection may have closed.")
                self.close()
                return {"song": "N/A", "artist": "N/A", "album": "N/A", "hitrate": 0.0}

            logger.info(f"Received raw data: {data}")
            parsed_data = json.loads(data)
            # Validate expected fields (adjust based on RockSniffer output)
            return {
                "song": parsed_data.get("song", "N/A"),
                "artist": parsed_data.get("artist", "N/A"),
                "album": parsed_data.get("album", "N/A"),
                "hitrate": float(parsed_data.get("hitrate", 0.0))
            }
        except (socket.error, json.JSONDecodeError, ConnectionError) as e:
            logger.error(f"Error reading RockSniffer data: {e}")
            self.close()
            return {"song": "N/A", "artist": "N/A", "album": "N/A", "hitrate": 0.0}
        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            self.close()
            return {"song": "N/A", "artist": "N/A", "album": "N/A", "hitrate": 0.0}

    def close(self):
        if self.sock:
            self.sock.close()
            logger.info("Socket closed.")
            self.sock = None

    def __del__(self):
        self.close()

if __name__ == "__main__":
    reader = RockSnifferReader()
    while True:
        data = reader.read_data()
        print(f"Processed data: {data}")
        time.sleep(1)
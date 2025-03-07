import time
import logging
from rocksniffer_reader import RockSnifferReader

# Global data to share with Flask
overlay_data = {"song": "N/A", "artist": "N/A", "album": "N/A", "hitrate": 0.0}

logging.basicConfig(
    level=logging.INFO,
    filename='rocksmith_overlay.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RocksmithOverlay:
    def __init__(self, host="localhost", port=9938):
        self.reader = RockSnifferReader(host=host, port=port)

    def run(self):
        global overlay_data
        while True:
            try:
                data = self.reader.read_data()
                if data:
                    overlay_data.update(data)  # Update global data
                    logger.info(f"Overlay updated with data: {data}")
                else:
                    logger.warning("No data received from RockSniffer.")
            except Exception as e:
                logger.error(f"Error in overlay loop: {e}")
            time.sleep(1)

    def stop(self):
        self.reader.close()
        logger.info("RocksmithOverlay stopped.")

if __name__ == "__main__":
    overlay = RocksmithOverlay()
    try:
        overlay.run()
    except KeyboardInterrupt:
        overlay.stop()
import time
import logging
from rocksniffer_reader import RockSnifferReader
# from overlay import Overlay  # Uncomment if defined

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
        # self.overlay = Overlay()  # Uncomment and adjust

    def run(self):
        while True:
            try:
                data = self.reader.read_data()
                logger.info(f"Overlay received data: {data}")
                # Update overlay with data (uncomment and adjust based on your overlay implementation)
                # if self.overlay:
                #     self.overlay.update_song(data.get("song", "N/A"))
                #     self.overlay.update_artist(data.get("artist", "N/A"))
                #     self.overlay.update_album(data.get("album", "N/A"))
                #     self.overlay.update_hitrate(data.get("hitrate", 0.0))
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
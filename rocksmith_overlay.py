import time
import logging
from rocksniffer_reader import RockSnifferReader

# Global data to share with Flask
overlay_data = {
    "song": "N/A",
    "artist": "N/A",
    "album": "N/A",
    "theory": "N/A",
    "trivia": "N/A",
    "hitrate": 0.0,
    "hitrate_history": [],
    "streak": "N/A",
    "highest_streak": "N/A",
    "live_ai": False
}

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
        self.live_ai = False
        self.hitrate_history = []

    def run(self):
        global overlay_data
        while True:
            try:
                data = self.reader.read_data()
                if data:
                    # Update hitrate history
                    hitrate = float(data.get("hitrate", 0.0))
                    self.hitrate_history.append(hitrate)
                    self.hitrate_history = self.hitrate_history[-10:]  # Keep last 10 values

                    overlay_data.update({
                        "song": data.get("song", "N/A"),
                        "artist": data.get("artist", "N/A"),
                        "album": data.get("album", "N/A"),
                        "theory": data.get("theory", "N/A"),
                        "trivia": data.get("trivia", "N/A"),
                        "hitrate": hitrate,
                        "hitrate_history": self.hitrate_history,
                        "streak": data.get("streak", "N/A"),
                        "highest_streak": data.get("highest_streak", "N/A"),
                        "live_ai": self.live_ai
                    })
                    logger.info(f"Overlay updated with data: {overlay_data}")
                else:
                    logger.warning("No data received from RockSniffer.")
            except Exception as e:
                logger.error(f"Error in overlay loop: {e}")
            time.sleep(1)

    def toggle_live_ai(self):
        self.live_ai = not self.live_ai
        overlay_data["live_ai"] = self.live_ai
        logger.info(f"Live AI toggled to: {self.live_ai}")
        return self.live_ai

    def stop(self):
        self.reader.close()
        logger.info("RocksmithOverlay stopped.")

if __name__ == "__main__":
    overlay = RocksmithOverlay()
    try:
        overlay.run()
    except KeyboardInterrupt:
        overlay.stop()
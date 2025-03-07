from flask import Flask, render_template
import threading
import logging
from rocksmith_overlay import RocksmithOverlay, overlay_data

logging.basicConfig(
    level=logging.INFO,
    filename='rocksmith_overlay.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
overlay = RocksmithOverlay(host="localhost", port=9938)

@app.route('/')
def index():
    return render_template('overlay.html', data=overlay_data)

def start_overlay():
    overlay.run()

if __name__ == "__main__":
    overlay_thread = threading.Thread(target=start_overlay, daemon=True)
    overlay_thread.start()
    logger.info("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)
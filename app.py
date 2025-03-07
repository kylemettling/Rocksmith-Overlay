import sys
import logging
from flask import Flask, render_template, jsonify
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl
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

@app.route('/data')
def get_data():
    return jsonify(overlay_data)

@app.route('/toggle_live_ai', methods=['POST'])
def toggle_live_ai():
    overlay.toggle_live_ai()
    return jsonify({"live_ai": overlay_data["live_ai"]})

def start_overlay():
    overlay.run()

class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Hide title bar, keep on top
        self.setAttribute(Qt.WA_TranslucentBackground)  # Transparent background
        self.setGeometry(50, 50, 600, 400)  # Initial position and size

        self.browser = QWebEngineView(self)
        self.browser.setUrl(QUrl("http://localhost:5000"))  # Load Flask-served page
        self.setCentralWidget(self.browser)

        self.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Rocksmith Overlay")
    parser.add_argument('--standalone', action='store_true', help="Run in standalone window mode")
    args = parser.parse_args()

    overlay_thread = threading.Thread(target=start_overlay, daemon=True)
    overlay_thread.start()

    if args.standalone:
        app = QApplication(sys.argv)
        window = OverlayWindow()
        sys.exit(app.exec_())
    else:
        logger.info("Starting Flask app...")
        app.run(debug=True, host='0.0.0.0', port=5000)
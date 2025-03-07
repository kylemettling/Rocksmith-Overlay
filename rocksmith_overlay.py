from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QUrl, QPoint
from PyQt5.QtWebEngineWidgets import QWebEngineView
import requests
import time
import logging
import sys
import socket  # For checking port usage
from threading import Thread
from flask import Flask, render_template

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class OverlayWindow(QMainWindow):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.init_ui()

    def init_ui(self):
        # Set window flags for a frameless, always-on-top overlay
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        print("OverlayWindow initialized with transparent background.")

        # Add a web view to load the flask app
        self.browser = QWebEngineView(self)
        self.setGeometry(100, 100, 800, 800)  # Moved to (100, 100) to ensure visibility
        self.browser.setGeometry(0, 0, 800, 800)  # Match the window size
        self.setAttribute(Qt.WA_TranslucentBackground)
        print("QWebEngineView created with transparent background.")

        # Ensure the browser itself is transparent and doesn’t steal focus
        self.browser.setAttribute(Qt.WA_TranslucentBackground)
        self.browser.page().setBackgroundColor(Qt.transparent)
        self.browser.setFocusPolicy(Qt.NoFocus)  # Prevent QWebEngineView from capturing focus

        # Enable mouse tracking
        self.setMouseTracking(True)

        # Try to load the URL with retries
        self.load_with_retries()

        # Variables for dragging
        self.old_pos = None
        self.dragging = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.dragging = True

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def load_with_retries(self, max_retries=5, delay=2000, timeout=1):
        attempt = 0
        while attempt < max_retries:
            try:
                # Diagnostic check for RockSniffer on port 9938
                response = requests.get("http://localhost:9938", timeout=timeout)
                response.raise_for_status()
                logging.info("RockSniffer detected on port 9938")

                # Use the Flask port
                flask_url = f"http://localhost:{self.port}/overlay"
                logging.info(f"Attempting to connect to Flask at {flask_url}")
                response = requests.get(flask_url, timeout=timeout)
                response.raise_for_status()
                logging.info(f"Flask server running on port {self.port}")
                self.browser.setUrl(QUrl(flask_url))
                logging.info(f"Overlay URL loaded successfully on port {self.port}")
                return

            except requests.exceptions.RequestException as e:
                logging.error(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt == max_retries - 1:
                    logging.error("Max retries reached. Check if Flask is running on port 5000 and RockSniffer on port 9938.")
                    self.browser.setUrl(QUrl(f"http://localhost:{self.port}/overlay"))  # Force load even on failure
                time.sleep(delay / 1000)  # Convert ms to seconds
                attempt += 1

# Simple function to check if a port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Create and run Flask app in a separate thread
def run_flask_app(port):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    @app.route('/overlay')
    def overlay():
        try:
            response = requests.get("http://localhost:9938", timeout=1)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException:
            data = {}
        return render_template('overlay.html', data=data)

    @app.route('/data')
    def data():
        try:
            response = requests.get("http://localhost:9938", timeout=1)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "No data from RockSniffer"}

    if not is_port_in_use(port):
        thread = Thread(target=lambda: app.run(port=port, debug=True, use_reloader=False), daemon=True)
        thread.start()
        logging.info(f"Flask thread started on port {port}")
    else:
        logging.error(f"Port {port} is already in use. Please free the port or change it.")

if __name__ == "__main__":
    port = 5000
    run_flask_app(port)  # Start Flask server
    app = QApplication(sys.argv)
    window = OverlayWindow(port)
    window.show()
    sys.exit(app.exec_())
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal, QPoint
from PyQt5.QtWebEngineWidgets import QWebEngineView
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class OverlayWindow(QWidget):
    def __init__(self, port):
        super().__init__()
        self.port = port  # Store the Flask port
        self.setGeometry(0, 0, 800, 600)  # Fixed size to match content
        self.setWindowTitle("Rocksmith Overlay")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        print("OverlayWindow initialized with transparent background.")

        # Add a web view to load the Flask app
        self.browser = QWebEngineView(self)
        self.browser.setGeometry(0, 0, 800, 600)
        self.browser.setAttribute(Qt.WA_TranslucentBackground)
        print("QWebEngineView created with transparent background.")

        # Try to load the URL with retries
        self.load_with_retries()

        # Variables for dragging
        self.old_pos = None
        self.dragging = False

    def load_with_retries(self, max_retries=5, delay=2000, timeout=5):
        attempt = 0
        while attempt < max_retries:
            try:
                # Diagnostic check for RockSniffer on port 9938
                response = requests.get("http://localhost:9938", timeout=timeout)
                response.raise_for_status()
                logging.info("RockSniffer detected on port 9938")

                # Use the provided Flask port
                flask_url = f"http://localhost:{self.port}/overlay"
                logging.info(f"Attempting to connect to Flask at {flask_url}")
                response = requests.get(flask_url, timeout=timeout)
                response.raise_for_status()
                logging.info(f"Flask server detected on port {self.port}")
                self.browser.setUrl(QUrl(flask_url))
                QTimer.singleShot(100, lambda: self.ensure_transparency())
                logging.info(f"Overlay URL loaded successfully on port {self.port}")
                return  # Exit if successful
            except requests.exceptions.RequestException as e:
                if "localhost:9938" in str(e):
                    logging.error(f"Failed to connect to RockSniffer (attempt {attempt + 1}/{max_retries}): {e}")
                else:
                    logging.error(f"Failed to connect to Flask on port {self.port} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logging.error("Failed to connect after retries. Check if RockSniffer is on port 9938 and Flask started.")
                time.sleep(delay / 1000)  # Convert ms to seconds
                attempt += 1

    def ensure_transparency(self):
        self.browser.page().setBackgroundColor(Qt.transparent)
        print("Ensured transparency of QWebEngineView page.")

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

from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverlayWindow(port=5000)
    window.show()
    sys.exit(app.exec_())
import sys
import logging
from flask import Flask, render_template, jsonify
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QPoint
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

def start_flask():
    logger.info("Starting Flask app at http://localhost:5000...")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Hide title bar, keep on top
        self.setAttribute(Qt.WA_TranslucentBackground)  # Transparent background
        self.setStyleSheet("background: transparent;")  # Ensure no white background

        self.browser = QWebEngineView(self)
        self.browser.setUrl(QUrl("http://localhost:5000"))  # Load Flask-served page
        self.setCentralWidget(self.browser)

        # Center on primary monitor and adjust size
        primary_screen = QDesktopWidget().screenGeometry(0)  # Primary screen
        self.move(primary_screen.left() + 50, primary_screen.top() + 50)  # Offset from top-left
        content_size = self.browser.sizeHint()  # Approximate content size
        self.resize(content_size.width() + 20, content_size.height() + 20)  # Add padding

        self.show()

        self.dragging = False
        self.drag_position = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

if __name__ == "__main__":
    # Start Flask server in a thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Start overlay data thread
    overlay_thread = threading.Thread(target=start_overlay, daemon=True)
    overlay_thread.start()

    # Launch PyQt window
    qt_app = QApplication(sys.argv)
    window = OverlayWindow()
    logger.info("Starting standalone PyQt window...")
    sys.exit(qt_app.exec_())
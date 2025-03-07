import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt

class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.dragging = False
        self.offset = None

    def initUI(self):
        self.setGeometry(100, 100, 400, 300)
        self.label = QLabel("Overlay Content", self)
        self.label.setStyleSheet("background-color: rgba(0, 0, 0, 100); color: white;")
        self.label.setAlignment(Qt.AlignCenter)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging and self.offset:
            self.move(self.pos() + event.pos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.offset = None

    def update_song(self, song):
        self.label.setText(f"Song: {song}")

    def update_artist(self, artist):
        self.label.setText(f"Artist: {artist}")  # Adjust to append or use a layout

    # Add other update methods as needed

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverlayWindow()
    sys.exit(app.exec_())
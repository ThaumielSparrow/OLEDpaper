from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OLEDpaper")
        load_button = QPushButton("Load Image")
        load_button.setCheckable(True)
        load_button.clicked.connect()

        self.setCentralWidget(load_button)

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
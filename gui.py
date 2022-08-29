from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None

        self.setWindowTitle("OLEDpaper")
        load_button = QPushButton("Load Image")
        load_button.setCheckable(True)
        load_button.clicked.connect(self.file_explorer)

        self.setCentralWidget(load_button)
    
    def file_explorer(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select Image", "","All Files (*);;PNG Image (*.png);;JPG Image (*.jpg)", options=options)
        if fileName:
            self.current_file = fileName

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QWidget, QHBoxLayout, QVBoxLayout
import sys

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.current_file = None
        self.button_func_dict = {"Load Image": self.load_image}

        self.setWindowTitle("OLEDpaper")
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.vLayout = QVBoxLayout(self.centralWidget)

        self.buttonsWidget = QWidget()
        self.buttonsWidgetLayout = QHBoxLayout(self.buttonsWidget)
        self.buttons = [QPushButton(i) for i in list(self.button_func_dict.keys())]
        for idx, button in enumerate(self.buttons):
            self.buttonsWidgetLayout.addWidget(button)
            button.clicked.connect(list(self.button_func_dict.values())[idx])
            # assign function to buttons, probably use dict where key=button name, value=button function
        
        self.mainCanvas = QWidget()
        self.mainCanvas.setMinimumWidth(320)
        self.mainCanvas.setMinimumHeight(480)
        self.mainCanvas.setStyleSheet('* {background: gray;}')

        self.vLayout.addWidget(self.mainCanvas)
        self.vLayout.addWidget(self.buttonsWidget)
        # load_button = QPushButton("Load Image")
        # load_button.setCheckable(True)
        # load_button.clicked.connect(self.load_image)
        # self.setCentralWidget(load_button)
    
    def load_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select Image", "","All Files (*);;PNG Image (*.png);;JPG Image (*.jpg)", options=options)
        if fileName:
            self.current_file = fileName
            pixmap = QPixmap(fileName)

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
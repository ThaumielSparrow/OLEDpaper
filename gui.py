from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSlider)
import sys
import qimage2ndarray as QIA

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.current_file = None
        self.button_func_dict = {"Load Image": self._load_image}

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

        self.slider_r, self.slider_g, self.slider_b = [QSlider(self)]*3
        for i in [self.slider_r, self.slider_g, self.slider_b]:
            i.setOrientation(QtCore.Qt.Horizontal)
            i.setMinimum(0)
            i.setMaximum(255)
            i.sliderMoved.connect(self._slider_moved)
            self.vLayout.addWidget(i)

        self.mainCanvas = QLabel()
        # self.mainCanvas.setMinimumWidth(480)
        # self.mainCanvas.setMinimumHeight(720)
        self.mainCanvas.setStyleSheet('* {background: gray;}')

        self.vLayout.addWidget(self.mainCanvas)
        self.vLayout.addWidget(self.buttonsWidget)
        # load_button = QPushButton("Load Image")
        # load_button.setCheckable(True)
        # load_button.clicked.connect(self.load_image)
        # self.setCentralWidget(load_button)
    
    def _load_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select Image", "","All Files (*);;PNG Image (*.png);;JPG Image (*.jpg)", options=options)
        if fileName:
            self.current_file = fileName
            # label = QLabel(self)
            pixmap = QPixmap(fileName)
            self.mainCanvas.setPixmap(pixmap)
            # self.vLayout.addWidget(label)
            self.mainCanvas.setMinimumWidth(pixmap.width())
            self.mainCanvas.setMinimumHeight(pixmap.height())
            self.show()
    
    def _slider_moved(self, val):
        pass


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
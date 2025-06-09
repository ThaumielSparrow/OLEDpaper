import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QHBoxLayout, QWidget, QPushButton, QLabel, 
                            QSlider, QLineEdit, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIntValidator
import os

class ImageViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle('OLEDpaper')
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create and setup the image display label (canvas)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid gray; background-color: white;")
        self.image_label.setText("No image loaded")
        self.image_label.setMinimumSize(600, 400)
        main_layout.addWidget(self.image_label)
        
        # Create controls layout
        controls_layout = QVBoxLayout()
        
        # Load Image button
        self.load_button = QPushButton('Load Image')
        self.load_button.clicked.connect(self.load_image)
        self.load_button.setMaximumWidth(150)
        controls_layout.addWidget(self.load_button)
        
        # Slider and input controls
        slider_layout = QHBoxLayout()
        
        # Slider label
        slider_label = QLabel('Threshold:')
        slider_layout.addWidget(slider_label)
        
        # Slider (1 to 255)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(255)
        self.slider.setValue(1)  # Default value
        self.slider.valueChanged.connect(self.slider_changed)
        slider_layout.addWidget(self.slider)
        
        # Input box
        self.value_input = QLineEdit()
        self.value_input.setText('1')
        self.value_input.setMaximumWidth(60)
        # Set validator to only allow integers between 1 and 255
        validator = QIntValidator(1, 255)
        self.value_input.setValidator(validator)
        self.value_input.textChanged.connect(self.input_changed)
        self.value_input.returnPressed.connect(self.input_finished)
        slider_layout.addWidget(self.value_input)
        
        controls_layout.addLayout(slider_layout)
        main_layout.addLayout(controls_layout)
        
        # Store the original pixmap for scaling
        self.original_pixmap = None
        
    def load_image(self):
        """Open file dialog to load an image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Load Image',
            '',
            'Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;All Files (*)'
        )
        
        if file_path:
            try:
                # Load the image
                pixmap = QPixmap(file_path)
                if pixmap.isNull():
                    QMessageBox.warning(self, 'Error', 'Failed to load the image.')
                    return
                
                # Store original pixmap
                self.original_pixmap = pixmap
                
                # Scale and display the image
                self.display_scaled_image()
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred while loading the image:\n{str(e)}')
    
    def display_scaled_image(self):
        """Display the image scaled to fit the label while maintaining aspect ratio"""
        if self.original_pixmap:
            # Get the size of the label
            label_size = self.image_label.size()
            
            # Scale the pixmap to fit the label while maintaining aspect ratio
            scaled_pixmap = self.original_pixmap.scaled(
                label_size, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
    
    def slider_changed(self):
        """Handle slider value change"""
        value = self.slider.value()
        self.value_input.setText(str(value))
    
    def input_changed(self):
        """Handle input box text change (real-time)"""
        text = self.value_input.text()
        if text.isdigit():
            value = int(text)
            if 1 <= value <= 255:
                # Update slider without triggering its signal
                self.slider.blockSignals(True)
                self.slider.setValue(value)
                self.slider.blockSignals(False)
    
    def input_finished(self):
        """Handle when user presses Enter in input box"""
        text = self.value_input.text()
        if not text.isdigit():
            # Reset to slider value if invalid
            self.value_input.setText(str(self.slider.value()))
        else:
            value = int(text)
            if not (1 <= value <= 255):
                # Clamp value to valid range
                value = max(1, min(255, value))
                self.value_input.setText(str(value))
                self.slider.setValue(value)
    
    def resizeEvent(self, event):
        """Handle window resize to rescale image"""
        super().resizeEvent(event)
        if self.original_pixmap:
            self.display_scaled_image()

def main():
    app = QApplication(sys.argv)
    window = ImageViewerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
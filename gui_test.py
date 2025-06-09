import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QHBoxLayout, QWidget, QPushButton, QLabel, 
                            QSlider, QLineEdit, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QIntValidator
import os

from utils.threshold_qimage import threshold

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
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Load Image button
        self.load_button = QPushButton('Load Image')
        self.load_button.clicked.connect(self.load_image)
        self.load_button.setMaximumWidth(150)
        buttons_layout.addWidget(self.load_button)
        
        # Save Image button
        self.save_button = QPushButton('Save Image')
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setMaximumWidth(150)
        self.save_button.setEnabled(False)  # Disabled until image is loaded
        buttons_layout.addWidget(self.save_button)
        
        # Add stretch to push buttons to the left
        buttons_layout.addStretch()
        
        controls_layout.addLayout(buttons_layout)
        
        # Slider and input controls
        slider_layout = QHBoxLayout()
        
        # Slider label
        slider_label = QLabel('Threshold:')
        slider_layout.addWidget(slider_label)
        
        # Slider (1 to 255)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(255)
        self.slider.setValue(1)  # Default
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
        
        # Store the original image data
        self.original_image = None
        self.processed_image = None
        

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
                # Load the image as QImage for fast pixel operations
                loaded_image = QImage(file_path)
                if loaded_image.isNull():
                    QMessageBox.warning(self, 'Error', 'Failed to load the image.')
                    return
                
                # Convert to optimal format for fast pixel access
                # Use ARGB32 if image has alpha channel, otherwise RGB32
                if loaded_image.hasAlphaChannel():
                    self.original_image = loaded_image.convertToFormat(QImage.Format_ARGB32)
                    print(f"Converted image to Format_ARGB32 (original format: {loaded_image.format()})")
                else:
                    self.original_image = loaded_image.convertToFormat(QImage.Format_RGB32)
                    print(f"Converted image to Format_RGB32 (original format: {loaded_image.format()})")
                
                # Enable save button
                self.save_button.setEnabled(True)

                # Process and display the image with current slider value
                self.process_and_display_image()
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred while loading the image:\n{str(e)}')


    def save_image(self):
        """Save the currently processed image"""
        if not self.processed_image:
            QMessageBox.warning(self, 'Warning', 'No processed image to save.')
            return
        
        # Open save dialog
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            'Save Image',
            '',
            'PNG Files (*.png);;JPEG Files (*.jpg);;BMP Files (*.bmp);;TIFF Files (*.tiff);;All Files (*)'
        )
        
        if file_path:
            try:
                # Determine format from selected filter or file extension
                if selected_filter.startswith('PNG'):
                    format_str = 'PNG'
                elif selected_filter.startswith('JPEG'):
                    format_str = 'JPEG'
                elif selected_filter.startswith('BMP'):
                    format_str = 'BMP'
                elif selected_filter.startswith('TIFF'):
                    format_str = 'TIFF'
                else:
                    # Try to determine from file extension
                    ext = os.path.splitext(file_path)[1].lower()
                    format_map = {
                        '.png': 'PNG',
                        '.jpg': 'JPEG',
                        '.jpeg': 'JPEG',
                        '.bmp': 'BMP',
                        '.tiff': 'TIFF',
                        '.tif': 'TIFF'
                    }
                    format_str = format_map.get(ext, 'PNG')  # Default to PNG
                    
                    # Add extension if not present
                    if not ext:
                        file_path += '.png'
                
                # Save the processed image
                success = self.processed_image.save(file_path, format_str)
                
                if success:
                    QMessageBox.information(self, 'Success', f'Image saved successfully to:\n{file_path}')
                else:
                    QMessageBox.warning(self, 'Error', 'Failed to save the image.')
                    
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred while saving the image:\n{str(e)}')


    def process_and_display_image(self):
        """Process the image based on slider value and display it"""
        if not self.original_image:
            return
            
        # Get current slider value
        slider_value = self.slider.value()
        
        # TODO: Add your image processing logic here
        # For now, we'll just copy the original image
        # Example: self.processed_image = self.apply_brightness(self.original_image, slider_value)
        threshold_image = threshold(self.original_image.copy(), slider_value)
        self.processed_image = threshold_image
        
        # Convert to pixmap and display
        self.display_scaled_image()

    
    def display_scaled_image(self):
        """Display the processed image scaled to fit the label while maintaining aspect ratio"""
        if self.processed_image:
            # Convert QImage to QPixmap
            pixmap = QPixmap.fromImage(self.processed_image)
            
            # Get the size of the label
            label_size = self.image_label.size()
            
            # Scale the pixmap to fit the label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                label_size, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
    
    def slider_changed(self):
        """Handle slider value change - process and display image"""
        value = self.slider.value()
        self.value_input.setText(str(value))
        # Process and display image with new value
        self.process_and_display_image()
    
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
                # Process and display image with new value
                self.process_and_display_image()
    
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
        if self.processed_image:
            self.display_scaled_image()

def main():
    app = QApplication(sys.argv)
    window = ImageViewerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
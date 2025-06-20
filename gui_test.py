import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QHBoxLayout, QWidget, QPushButton, QLabel, 
                            QSlider, QLineEdit, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QMutexLocker
from PyQt5.QtGui import QPixmap, QImage, QIntValidator
import os
from queue import Queue
import time

from utils.threshold_qimage import threshold_qimage

THRESHOLD_MAX = 255

class ImageProcessor(QThread):
    """Background thread for image processing"""
    imageProcessed = pyqtSignal(object)  # Will emit the processed numpy array
    
    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.running = True
        self.original_array = None
        self.working_array = None
        self.mutex = QMutex()
        
    def set_image(self, image_array):
        """Set the original image to process"""
        with QMutexLocker(self.mutex):
            self.original_array = image_array.copy()
            # Pre-allocate working array for in-place operations
            self.working_array = np.empty_like(self.original_array)
        
    def add_threshold_value(self, value):
        """Add a threshold value to process, clearing any pending values"""
        # Clear the queue of any pending values
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except:
                pass
        # Add the new value
        self.queue.put(value)
        
    def run(self):
        """Main processing loop"""
        while self.running:
            try:
                # Wait for a threshold value (with timeout to check running status)
                threshold = self.queue.get(timeout=0.05)
                
                with QMutexLocker(self.mutex):
                    if self.original_array is not None:
                        # Process the image
                        # start_time = time.time()
                        processed = threshold_qimage(self.original_array, threshold)
                        # processing_time = (time.time() - start_time) * 1000
                        # print(f"Processing took {processing_time:.2f}ms for threshold={threshold}")
                        
                        # Emit the processed array
                        self.imageProcessed.emit(processed)
                        
            except:
                # Timeout - just continue to check if still running
                continue
                
    def stop(self):
        """Stop the processing thread"""
        self.running = False
        self.wait()

class ImageViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create and start the processing thread
        self.processor = ImageProcessor()
        self.processor.imageProcessed.connect(self.on_image_processed)
        self.processor.start()
        
        # Cache for QImage and QPixmap conversions
        self.qimage_cache = {}
        self.pixmap_cache = {}
        self.last_label_size = None
        
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle('OLEDpaper')
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create and setup the image display label
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
        self.save_button.setEnabled(False)
        buttons_layout.addWidget(self.save_button)
        
        buttons_layout.addStretch()
        controls_layout.addLayout(buttons_layout)
        
        # Slider and input controls
        slider_layout = QHBoxLayout()
        
        slider_label = QLabel('Threshold:')
        slider_layout.addWidget(slider_label)
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(THRESHOLD_MAX)
        self.slider.setValue(1)
        self.slider.valueChanged.connect(self.slider_changed)
        slider_layout.addWidget(self.slider)
        
        # Input box
        self.value_input = QLineEdit()
        self.value_input.setText('1')
        self.value_input.setMaximumWidth(60)
        validator = QIntValidator(1, THRESHOLD_MAX)
        self.value_input.setValidator(validator)
        self.value_input.textChanged.connect(self.input_changed)
        self.value_input.returnPressed.connect(self.input_finished)
        slider_layout.addWidget(self.value_input)
        
        controls_layout.addLayout(slider_layout)
        main_layout.addLayout(controls_layout)
        
        # Store the original image data
        self.original_array = None
        self.processed_array = None
        self.has_alpha = False
        self.current_threshold = 1
        
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
                loaded_image = QImage(file_path)
                if loaded_image.isNull():
                    QMessageBox.warning(self, 'Error', 'Failed to load the image.')
                    return
                
                # Convert to optimal format
                self.has_alpha = loaded_image.hasAlphaChannel()
                if self.has_alpha:
                    qimage = loaded_image.convertToFormat(QImage.Format_RGBA8888)
                else:
                    qimage = loaded_image.convertToFormat(QImage.Format_RGB888)
                
                # Convert to numpy array
                self.original_array = self.qimage_to_numpy(qimage)
                
                # Clear caches when loading new image
                self.qimage_cache.clear()
                self.pixmap_cache.clear()
                
                # Set the image in the processor
                self.processor.set_image(self.original_array)
                
                # Enable save button
                self.save_button.setEnabled(True)
                
                # Process with current threshold
                self.processor.add_threshold_value(self.slider.value())
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred while loading the image:\n{str(e)}')
    
    def save_image(self):
        """Save the currently processed image"""
        if self.processed_array is None:
            QMessageBox.warning(self, 'Warning', 'No processed image to save.')
            return
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            'Save Image',
            '',
            'PNG Files (*.png);;JPEG Files (*.jpg);;BMP Files (*.bmp);;TIFF Files (*.tiff);;All Files (*)'
        )
        
        if file_path:
            try:
                # Convert numpy array to QImage
                qimage = self.numpy_to_qimage(self.processed_array)
                
                # Determine format
                if selected_filter.startswith('PNG'):
                    format_str = 'PNG'
                elif selected_filter.startswith('JPEG'):
                    format_str = 'JPEG'
                elif selected_filter.startswith('BMP'):
                    format_str = 'BMP'
                elif selected_filter.startswith('TIFF'):
                    format_str = 'TIFF'
                else:
                    ext = os.path.splitext(file_path)[1].lower()
                    format_map = {
                        '.png': 'PNG',
                        '.jpg': 'JPEG',
                        '.jpeg': 'JPEG',
                        '.bmp': 'BMP',
                        '.tiff': 'TIFF',
                        '.tif': 'TIFF'
                    }
                    format_str = format_map.get(ext, 'PNG')
                    if not ext:
                        file_path += '.png'
                
                # Save the image
                success = qimage.save(file_path, format_str)
                
                if success:
                    QMessageBox.information(self, 'Success', f'Image saved successfully to:\n{file_path}')
                else:
                    QMessageBox.warning(self, 'Error', 'Failed to save the image.')
                    
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred while saving the image:\n{str(e)}')
    
    def qimage_to_numpy(self, qimage):
        """Convert QImage to numpy array"""
        width = qimage.width()
        height = qimage.height()
        
        ptr = qimage.bits()
        ptr.setsize(qimage.byteCount())
        
        if self.has_alpha:
            arr = np.array(ptr).reshape(height, width, 4)
        else:
            arr = np.array(ptr).reshape(height, width, 3)
        
        return arr.copy()
    
    def numpy_to_qimage(self, arr):
        """Convert numpy array to QImage with caching"""
        # Create a hash key for the array
        arr_key = hash(arr.tobytes())
        
        # Check cache
        if arr_key in self.qimage_cache:
            return self.qimage_cache[arr_key]
        
        height, width = arr.shape[:2]
        
        if arr.shape[2] == 4:  # RGBA
            qimage = QImage(arr.data, width, height, QImage.Format_RGBA8888)
        else:  # RGB
            qimage = QImage(arr.data, width, height, QImage.Format_RGB888)
        
        qimage = qimage.copy()
        
        # Cache the result (limit cache size)
        if len(self.qimage_cache) > 10:
            self.qimage_cache.clear()
        self.qimage_cache[arr_key] = qimage
        
        return qimage
    
    def on_image_processed(self, processed_array):
        """Handle processed image from the worker thread"""
        self.processed_array = processed_array
        self.display_scaled_image()
    
    def display_scaled_image(self):
        """Display the processed image scaled to fit the label"""
        if self.processed_array is not None:
            # Get the current label size
            label_size = self.image_label.size()
            
            # Check if we need to rescale (size changed or no cached pixmap)
            size_key = (label_size.width(), label_size.height(), self.current_threshold)
            
            if size_key not in self.pixmap_cache:
                # Convert to QImage
                qimage = self.numpy_to_qimage(self.processed_array)
                
                # Convert to QPixmap
                pixmap = QPixmap.fromImage(qimage)
                
                # Scale the pixmap
                scaled_pixmap = pixmap.scaled(
                    label_size, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.FastTransformation  # Use fast transformation for responsiveness
                )
                
                # Cache the scaled pixmap (limit cache size)
                if len(self.pixmap_cache) > 10:
                    self.pixmap_cache.clear()
                self.pixmap_cache[size_key] = scaled_pixmap
            else:
                scaled_pixmap = self.pixmap_cache[size_key]
            
            self.image_label.setPixmap(scaled_pixmap)
    
    def slider_changed(self):
        """Handle slider value change"""
        value = self.slider.value()
        self.current_threshold = value
        self.value_input.setText(str(value))
        
        # Clear pixmap cache as threshold changed
        self.pixmap_cache.clear()
        
        # Send new threshold to processor
        if self.original_array is not None:
            self.processor.add_threshold_value(value)
    
    def input_changed(self):
        """Handle input box text change"""
        text = self.value_input.text()
        if text.isdigit():
            value = int(text)
            if 1 <= value <= THRESHOLD_MAX:
                self.current_threshold = value
                # Update slider without triggering its signal
                self.slider.blockSignals(True)
                self.slider.setValue(value)
                self.slider.blockSignals(False)
                
                # Clear pixmap cache and process
                self.pixmap_cache.clear()
                if self.original_array is not None:
                    self.processor.add_threshold_value(value)
    
    def input_finished(self):
        """Handle when user presses Enter in input box"""
        text = self.value_input.text()
        if not text.isdigit():
            self.value_input.setText(str(self.slider.value()))
        else:
            value = int(text)
            if not (1 <= value <= THRESHOLD_MAX):
                value = max(1, min(THRESHOLD_MAX, value))
                self.value_input.setText(str(value))
                self.slider.setValue(value)
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        if self.processed_array is not None:
            self.display_scaled_image()
    
    def closeEvent(self, event):
        """Clean up when closing the application"""
        self.processor.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = ImageViewerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
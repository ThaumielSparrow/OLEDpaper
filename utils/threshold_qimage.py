import numpy as np
from PyQt5.QtGui import QImage

def threshold(qimage, threshold):
    """
    Creates a new QImage where all RGB values below the threshold are set to (0, 0, 0).
    
    Args:
        qimage (QImage): Input QImage
        threshold (int): Threshold value (1-255). Pixels with R, G, or B below this become black.
    
    Returns:
        QImage: New QImage with thresholding applied
    """
    # Get image dimensions and format
    width = qimage.width()
    height = qimage.height()
    format = qimage.format()
    
    # Convert QImage to numpy array for fast processing
    # QImage.constBits() gives us direct access to the pixel data
    ptr = qimage.constBits()
    ptr.setsize(qimage.byteCount())
    
    # Create numpy array from the raw data
    if format == QImage.Format_RGB32 or format == QImage.Format_ARGB32:
        # 4 bytes per pixel (BGRA order in memory)
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4))
        # Create a copy to avoid modifying original
        result_arr = arr.copy()
        
        # Extract BGR channels (Qt uses BGR order in memory)
        b_channel = result_arr[:, :, 0]
        g_channel = result_arr[:, :, 1] 
        r_channel = result_arr[:, :, 2]
        
        # Create mask where any RGB channel is below threshold
        mask = (r_channel < threshold) | (g_channel < threshold) | (b_channel < threshold)
        
        # Set RGB channels to 0 where mask is True (keep alpha unchanged)
        result_arr[mask, 0] = 0  # Blue
        result_arr[mask, 1] = 0  # Green  
        result_arr[mask, 2] = 0  # Red
        
    elif format == QImage.Format_RGB888:
        # 3 bytes per pixel (RGB order)
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 3))
        result_arr = arr.copy()
        
        # Extract RGB channels
        r_channel = result_arr[:, :, 0]
        g_channel = result_arr[:, :, 1]
        b_channel = result_arr[:, :, 2]
        
        # Create mask and apply threshold
        mask = (r_channel < threshold) | (g_channel < threshold) | (b_channel < threshold)
        result_arr[mask] = 0
        
    else:
        # Fallback for other formats - convert to RGB32 first
        qimage_rgb32 = qimage.convertToFormat(QImage.Format_RGB32)
        return threshold(qimage_rgb32, threshold)
    
    # Create new QImage from the modified array
    if format == QImage.Format_RGB888:
        # For RGB888, we need to ensure the data is contiguous
        result_data = result_arr.tobytes()
        result_qimage = QImage(result_data, width, height, QImage.Format_RGB888)
    else:
        # For RGB32/ARGB32
        result_data = result_arr.tobytes()
        bytes_per_line = width * 4
        result_qimage = QImage(result_data, width, height, bytes_per_line, format)
    
    # Return a copy to ensure the data persists after function returns
    return result_qimage.copy()

import numpy as np

def threshold_qimage(image_array, threshold):
    """
    Creates a new numpy array where all RGB values below the threshold are set to 0.
    
    Args:
        image_array (np.ndarray): Input image array from qimage_to_numpy()
                                 Shape: (height, width, 3) for RGB or (height, width, 4) for RGBA
        threshold (int): Threshold value (1-255). Pixels with R, G, or B below this become black.
    
    Returns:
        np.ndarray: New array with thresholding applied, same shape as input
    """
    # Create a copy to avoid modifying the original
    result = image_array.copy()
    
    # Handle both RGB and RGBA formats
    if image_array.shape[2] == 4:  # RGBA format
        # Note: Qt typically stores as BGRA in memory, so channels are [B, G, R, A]
        b_channel = result[:, :, 0]
        g_channel = result[:, :, 1] 
        r_channel = result[:, :, 2]
        # Alpha channel at index 3 is preserved
        
        # Create mask where any RGB channel is below threshold
        mask = (r_channel < threshold) | (g_channel < threshold) | (b_channel < threshold)
        
        # Set RGB channels to 0 where mask is True (preserve alpha)
        result[mask, 0] = 0  # Blue
        result[mask, 1] = 0  # Green  
        result[mask, 2] = 0  # Red
        # Alpha channel (index 3) remains unchanged
        
    elif image_array.shape[2] == 3:  # RGB format
        # For RGB888, channels are typically [R, G, B]
        r_channel = result[:, :, 0]
        g_channel = result[:, :, 1]
        b_channel = result[:, :, 2]
        
        # Create mask where any RGB channel is below threshold
        mask = (r_channel < threshold) | (g_channel < threshold) | (b_channel < threshold)
        
        # Set all RGB channels to 0 where mask is True
        result[mask] = 0
    
    else:
        raise ValueError(f"Unsupported array shape: {image_array.shape}. Expected (height, width, 3) or (height, width, 4)")
    
    return result
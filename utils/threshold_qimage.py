import numpy as np

def threshold_qimage(image_array, threshold):
    """
    Highly optimized version using advanced numpy operations.
    Slightly faster for very large images.
    """
    result = image_array.copy()
    
    if image_array.shape[2] == 4:  # RGBA
        # Use numpy's any() function along the channel axis for RGB channels only
        rgb_channels = result[:, :, :3]  # Extract RGB, exclude alpha
        mask = np.any(rgb_channels < threshold, axis=2)
        
        # Use advanced indexing to set RGB channels to 0
        result[mask, :3] = 0
        
    elif image_array.shape[2] == 3:  # RGB
        # Check if any channel is below threshold
        mask = np.any(result < threshold, axis=2)
        result[mask] = 0
        
    else:
        raise ValueError(f"Unsupported array shape: {image_array.shape}")
    
    return result
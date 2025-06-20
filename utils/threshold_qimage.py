import numpy as np

try:
    from numba import njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

if NUMBA_AVAILABLE:
    @njit(parallel=True, cache=True)
    def threshold_numba(image_array, threshold, result):
        """Fast thresholding using numba JIT compilation."""
        height, width = image_array.shape[:2]
        channels = image_array.shape[2]
        
        for i in prange(height):
            for j in prange(width):
                if channels == 4:  # RGBA
                    if (image_array[i, j, 0] < threshold or 
                        image_array[i, j, 1] < threshold or 
                        image_array[i, j, 2] < threshold):
                        result[i, j, 0] = 0
                        result[i, j, 1] = 0
                        result[i, j, 2] = 0
                        result[i, j, 3] = image_array[i, j, 3]
                    else:
                        for k in range(4):
                            result[i, j, k] = image_array[i, j, k]
                else:  # RGB
                    if (image_array[i, j, 0] < threshold or 
                        image_array[i, j, 1] < threshold or 
                        image_array[i, j, 2] < threshold):
                        result[i, j, 0] = 0
                        result[i, j, 1] = 0
                        result[i, j, 2] = 0
                    else:
                        for k in range(3):
                            result[i, j, k] = image_array[i, j, k]

def threshold_qimage(image_array, threshold):
    """
    Optimized thresholding function.
    Uses numba if available, otherwise falls back to numpy.
    """
    if NUMBA_AVAILABLE:
        result = np.empty_like(image_array)
        threshold_numba(image_array, threshold, result)
        return result
    else:
        # Numpy vectorized version
        result = image_array.copy()
        
        if image_array.shape[2] == 4:  # RGBA format
            mask = np.any(result[:, :, :3] < threshold, axis=2)
            result[mask, :3] = 0
        elif image_array.shape[2] == 3:  # RGB format
            mask = np.any(result < threshold, axis=2)
            result[mask] = 0
        else:
            raise ValueError(f"Unsupported array shape: {image_array.shape}")
        
        return result
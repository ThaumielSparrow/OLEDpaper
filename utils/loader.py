from PIL import Image
import cv2 as cv
import numpy as np
from exceptions.exceptions import ImportError
from cv_PIL_conv import *

def load(image, as_type:str="PIL"):
    if isinstance(image, str):
        if as_type == "PIL":
            img = Image.open(image)
        elif as_type == "CV2":
            img = cv.imread(image)
        else:
            raise ImportError("Only 'PIL' and 'CV2' import types supported.")
    
    elif isinstance(image, np.ndarray) and as_type=="PIL":
        img = cv_to_PIL(image)
    
    elif not isinstance(image, np.ndarray) and not isinstance(image, str) and as_type=="CV2":
        img = PIL_to_cv(image)

    else:
        img = image
    
    return img

import numpy as np
import cv2 as cv
from PIL import Image

def cv_to_PIL(img):
    img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)

    return pil_img

def PIL_to_cv(img):
    np_img = np.array(img)
    cv_img = cv.cvtColor(np_img, cv.COLOR_RGB2BGR)

    return cv_img
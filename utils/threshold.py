from copy import deepcopy
import numpy as np
from PIL import Image
from .cv_PIL_conv import cv_to_PIL

def threshold(image, drop_thresh:tuple=(10,10,10), save_hard_copy=False, output_filename=None) -> Image.Image:
    """
    Shallow scale function designed to convert color ranges to true blacks. Takes only PIL image formats.

    Parameters
    ----------
    `image` -> PIL.Image.Image: one of the supported PIL image formats. If using this function outside its
        wrapper, Use functions found in `loader` to convert to proper input.
    
    `drop_thresh` -> Iterable [tuple, list]: (R,G,B) values that represent the threshold to set as true black.
        Defaults to (10,10,10).

    Returns
    ----------
    `img` -> PIL.Image.Image: modified image object with set true black threshold.
    
    """
    if len(drop_thresh) != 3:
        raise ValueError("Threshold value passed not of (R,G,B) format")

    if type(image) == str:
        orig_img = Image.open(image)
    else:
        try:
            if isinstance(image, np.ndarray):
                orig_img = cv_to_PIL(image)
            else:
                orig_img = image
        except:
            raise TypeError("Argument was not a valid filepath or image object")

    img = deepcopy(orig_img)
    img = img.convert("RGB")
    d = img.getdata()

    new_img = []

    for i in d:
        if all(a <= b for a, b in zip(i, drop_thresh)):
            new_img.append((0, 0, 0))
        else:
            new_img.append(i)

    img.putdata(new_img)

    if save_hard_copy:
        if output_filename:
            img.save(output_filename)
        else:
            img.save("output.png")
    
    return img

from copy import deepcopy
import cv2 as cv
from PIL import Image
from exceptions import DimensionError

def threshold_blacks(image, drop_thresh, save_hard_copy=False, output_filename=None):
    if len(drop_thresh) != 3:
        raise DimensionError("Threshold value passed not of (R,G,B) format")

    orig_img = Image.open(image)
    img = deepcopy(orig_img)
    img = img.convert("RGB")
    d = img.getdata()

    new_img = []

    for i in d:
        if all(a < b for a, b in zip(i, drop_thresh)):
            new_img.append((0, 0, 0))
        else:
            new_img.append(i)

    img.putdata(new_img)

    if save_hard_copy:
        if output_filename:
            img.save(output_filename)
        else:
            img.save('output.png')
    
    return img


if __name__ == "__main__":
    threshold_blacks('flower.jpg', drop_thresh=(200,200,200), save_hard_copy=True, output_filename='output1.png')
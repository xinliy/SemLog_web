import cv2
import numpy as np


def cut_object(rgb_image, mask_image, object_color,saving_path=None):
    """This function is used to cut a specific object from the pair RGB/mask image."""
    rgb_image = cv2.imread(rgb_image)
    mask_image = cv2.imread(mask_image)
    mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGR2RGB)

    # Create mask image with the only object
    object_mask_binary = cv2.inRange(mask_image, object_color, object_color)
    object_mask = cv2.bitwise_and(mask_image, mask_image, mask=object_mask_binary)

    # Detect the position of the object
    object_contour = cv2.cvtColor(object_mask, cv2.COLOR_BGR2GRAY)
    object_position, c = cv2.findContours(
        object_contour, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    object_position = np.array(object_position).squeeze()
    hmin, hmax = object_position[:, :1].min(), object_position[:, :1].max()
    wmin, wmax = object_position[:, 1:2].min(), object_position[:, 1:2].max()

    # Cut the object from the RGB image
    crop_rgb = rgb_image[wmin:wmax, hmin:hmax]

    if saving_path is not None:
        cv2.imwrite(saving_path,crop_rgb)

    return crop_rgb

import cv2
import numpy as np


def display(image, name="Image"):
    cv2.imshow(name, image)

def display_and_wait(image, name="Image"):
    cv2.imshow(name, image)
    cv2.waitKey(0)

def get_ordered_colors_of_image_strip(image):
    color_index = np.unique(image, axis=0, return_inverse=True)

    ordered_color_index = []

    for i in color_index[1]:
        if len(ordered_color_index) > 0:
            if i != ordered_color_index[-1]:
                ordered_color_index.append(i)
        else:
            ordered_color_index.append(i)

    return np.array([color_index[0][i] for i in ordered_color_index])

def get_border_colors_clockwise(image):
    (image_height, image_width, _) = image.shape
    
    top_edge = image[0, 0 : image_width - 1]
    bottom_edge = image[image_height - 1, 0 : image_width - 1]
    left_edge = image[0 : image_height - 1, 0]
    right_edge = image[0 : image_height - 1, image_width - 1]

    all_edges = [top_edge, right_edge, bottom_edge, left_edge]

    border_colors = np.concatenate([get_ordered_colors_of_image_strip(edge) for edge in all_edges])

    return border_colors

def get_color_ranges_mask(colors, image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    color_range_sum = np.zeros(gray_image.shape, np.uint8)

    for i in range(len(colors) - 1):
        color_pair = [colors[i], colors[i + 1]]

        for color_a in color_pair:
            for color_b in color_pair:
                color_range = cv2.inRange(image, color_a, color_b)
                color_range_sum = cv2.bitwise_or(color_range_sum, color_range)

    return color_range_sum
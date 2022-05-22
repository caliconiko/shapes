import cv2
import numpy as np
from collections import defaultdict


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
    color_range_sum = np.zeros(image.shape[:2], np.uint8)

    for i in range(len(colors) - 1):
        color_pair = [colors[i], colors[i + 1]]

        for color_a in color_pair:
            for color_b in color_pair:
                color_range = cv2.inRange(image, color_a, color_b)
                color_range_sum = cv2.bitwise_or(color_range_sum, color_range)

    return color_range_sum

def get_background_mask(image):
    border_colors = get_border_colors_clockwise(image)

    return get_color_ranges_mask(border_colors, image)

def clean_mask(mask, kernel_size=3):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask

def get_tree_next_index(hierarchy_tree, index):
    return hierarchy_tree[index][0]

def get_tree_previous_index(hierarchy_tree, index):
    return hierarchy_tree[index][1]

def get_tree_child_index(hierarchy_tree, index):
    return hierarchy_tree[index][2]

def get_tree_parent_index(hierarchy_tree, index):
    return hierarchy_tree[index][3]

def sort_hierarchy_tree(hierarchy_tree):
    hierarchy_tree = hierarchy_tree[0]

    hierarchy_tree_length = len(hierarchy_tree)
    
    hierarchies = defaultdict(list)
    
    # store top hierarchy contours
    for i in range(hierarchy_tree_length):
        if hierarchy_tree[i][3] == -1:
            hierarchies[0].append(i)

    current_hierarchy = 0

    while len(hierarchies[current_hierarchy]) > 0:
        next_hierarchy = current_hierarchy + 1

        # store direct children of current hierarchy
        for i in hierarchies[current_hierarchy]:
            child_index = get_tree_child_index(hierarchy_tree, i)
            if child_index != -1:
                hierarchies[next_hierarchy].append(child_index)

        # store neighbours of direct children
        if len(hierarchies[next_hierarchy]) > 0:
            first_child = hierarchies[next_hierarchy][0]

            previous_index = get_tree_previous_index(hierarchy_tree, first_child)
            while previous_index != -1:
                hierarchies[next_hierarchy].append(previous_index)
                previous_index = get_tree_previous_index(hierarchy_tree, previous_index)

            next_index = get_tree_next_index(hierarchy_tree, first_child)
            while next_index != -1:
                hierarchies[next_hierarchy].append(next_index)
                next_index = get_tree_next_index(hierarchy_tree, next_index)

        current_hierarchy = next_hierarchy

    return hierarchies

def get_contours_of_hierarchy(sorted_hierarchies, contours, hierarchy):
    return np.array([contours[i] for i in sorted_hierarchies[hierarchy]])

def mask_contour(contour, image):
    mask = np.zeros(image.shape[:2], np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    return mask

def mask_contours(contours, image):
    mask = np.zeros(image.shape[:2], np.uint8)
    cv2.drawContours(mask, contours, -1, 255, -1)
    return mask

def mask_contours_of_hierarchy(sorted_hierarchies, contours, hierarchy, image):
    return mask_contours(get_contours_of_hierarchy(sorted_hierarchies, contours, hierarchy), image)

def mask_contours_of_hierarchy_with_holes(sorted_hierarchies, contours, hierarchy, image):
    mask = mask_contours_of_hierarchy(sorted_hierarchies, contours, hierarchy, image)
    hole_mask = mask_contours_of_hierarchy(sorted_hierarchies, contours, hierarchy+1, image)

    mask_with_hole = cv2.bitwise_xor(mask, hole_mask)

    return mask_with_hole

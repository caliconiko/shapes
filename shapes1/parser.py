import cv2
from pathlib import Path
import numpy as np


from shapes1.cv_helper import *

class Parser:
    def __init__(self, file_path:Path):
        assert file_path.exists() and file_path.is_file(), "Huh? Can't find that file anywhere"

        self.file_path = file_path

        self.image = cv2.imread(str(self.file_path))

        assert self.image is not None, "That's not an image (I think)"

    def parse_frames(self):
        background_mask = get_background_mask(self.image)

        foreground_mask = cv2.bitwise_not(background_mask)
        foreground_mask = clean_mask_open(foreground_mask)

        contours, hierarchy = cv2.findContours(foreground_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        sorted_hierarchy_tree = sort_hierarchy_tree(hierarchy)

        shape_frame_mask = mask_contours_of_hierarchy_with_holes(sorted_hierarchy_tree, contours, 0, self.image)

        path_frame_mask = mask_contours_of_hierarchy_with_holes(sorted_hierarchy_tree, contours, 2, self.image)

        skelotonized_shape_frame_mask = skeletonize(shape_frame_mask)
        skelotonized_shape_frame_mask_dilate = morph_func(skelotonized_shape_frame_mask, cv2.dilate, 3)
        skelotonized_shape_frame_mask_clean = clean_mask_close(skelotonized_shape_frame_mask_dilate, 3)

        skeletonized_shape_frame = (shape_frame_mask
            .skeletonized()
            .morph_func(cv2.dilate, 3)
            .clean_mask_close(3))

        shape_skeleton_contours, shape_skeleton_hierarchy = cv2.findContours(skelotonized_shape_frame_mask_clean, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        shape_skeleton_sorted_hierarchy_tree = sort_hierarchy_tree(hierarchy) 

        shape_skeleton_inner_edge = mask_contours_of_hierarchy(shape_skeleton_sorted_hierarchy_tree, shape_skeleton_contours, 2, skelotonized_shape_frame_mask_clean, 1)
        
        shape_skeleton_inner_edge_contours = get_contours_of_hierarchy(shape_skeleton_sorted_hierarchy_tree, shape_skeleton_contours, 2)

        test = np.zeros_like(shape_skeleton_inner_edge)

        for contour_index, contour in enumerate(shape_skeleton_inner_edge_contours):
            contour:np.ndarray
            print(contour.shape)
            print(contour[:,0].shape)
            for position in contour[:,0]:
                test[position[1], position[0]]=255


        test = morph_func(test, cv2.dilate, 10)

        display(test, "debug")


        display_and_wait(self.image, "Image")

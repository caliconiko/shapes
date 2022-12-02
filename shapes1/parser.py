import cv2
from pathlib import Path
import numpy as np
import imutils

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
        foreground_mask = clean_mask(foreground_mask)

        contours, hierarchy = cv2.findContours(foreground_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        sorted_hierarchy_tree = sort_hierarchy_tree(hierarchy)

        shape_frame_mask = mask_contours_of_hierarchy_with_holes(sorted_hierarchy_tree, contours, 0, self.image)

        path_frame_mask = mask_contours_of_hierarchy_with_holes(sorted_hierarchy_tree, contours, 2, self.image)

        skelotonized_shape_frame_mask = imutils.skeletonize(shape_frame_mask, (10, 10), structuring=cv2.MORPH_CROSS)
        display(skelotonized_shape_frame_mask, "skelotonized shape frame mask")

        display_and_wait(self.image, "Image")
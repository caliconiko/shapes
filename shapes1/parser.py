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
        border_colors = get_border_colors_clockwise(self.image)
        background_mask = get_color_ranges_mask(border_colors, self.image)

        display_and_wait(self.image, "Image")
        display_and_wait(background_mask, "Background Mask")
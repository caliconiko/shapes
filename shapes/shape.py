import cv2
import numpy as np

from enum import Enum, auto

from shapes.utils import distance


class ShapeEnum(Enum):
    ANY = auto()
    START = auto()
    END = auto()

    JUNCTION = auto()
    NUMBER = auto()
    POP = auto()
    DUPE = auto()
    CONTAINER = auto()
    CONTROL = auto()
    NUMBER_CHECK = auto()
    LENGTH = auto()
    OPER = auto()
    STACK = auto()

    TO_NUMBER = auto()
    TO_STRING = auto()
    TO_CHAR = auto()
    CHR_TO_NUM = auto()

    AND = auto()
    OR = auto()
    NOT = auto()

    EQUALS = auto()
    LARGER = auto()
    SMALLER = auto()

    IN = auto()
    READ = auto()
    OUT = auto()
    OUT_NO_LF = auto()


class Shape:
    type_map = {
        ((1, True), ((3, True),)): ShapeEnum.START,
        ((1, True), ((4, True),)): ShapeEnum.END,
        ((4, True), False): ShapeEnum.JUNCTION,
        ((5, True),): ShapeEnum.NUMBER,
        ((6, False), False): ShapeEnum.POP,
        ((6, False), True): ShapeEnum.OPER,
        ((3, True), 3): ShapeEnum.DUPE,
        ((5, False), False): ShapeEnum.CONTAINER,
        ((3, True), False): ShapeEnum.CONTROL,
        ((5, False), True): ShapeEnum.STACK,
        ((4, True), ((5, True),)): ShapeEnum.NUMBER_CHECK,
        ((4, False), 1): ShapeEnum.TO_NUMBER,
        ((4, False), 2): ShapeEnum.TO_CHAR,
        ((4, False), 3): ShapeEnum.CHR_TO_NUM,
        ((8, False), ((1, True),)): ShapeEnum.OR,
        ((8, False), ((3, True),)): ShapeEnum.NOT,
        ((8, False), ((4, True),)): ShapeEnum.AND,
        ((8, False), ((1, False),)): ShapeEnum.OR,
        ((8, False), ((3, False),)): ShapeEnum.NOT,
        ((8, False), ((4, False),)): ShapeEnum.AND,
        ((8, False), 2): ShapeEnum.SMALLER,
        ((8, False), 3): ShapeEnum.EQUALS,
        ((8, False), 4): ShapeEnum.LARGER,
        ((4, False), False): ShapeEnum.TO_STRING,
        ((2, False), False): ShapeEnum.LENGTH,
        ((7, False), False): ShapeEnum.IN,
        ((6, True), False): ShapeEnum.OUT,
        ((6, True), 1): ShapeEnum.OUT_NO_LF,
        ((7, False), ((1, True),)): ShapeEnum.READ,
        ((7, False), ((1, False),)): ShapeEnum.READ,
    }
    # [[shape sides, is_convex], [hole shapes]]

    def __init__(self, contour: np.ndarray, circular: bool, center):
        self.center = center
        self.contour = contour
        self.circular = circular
        self.points = []

        self.connecteds = {}
        self.insides = []
        self.outer = None
        self.value = None

    def get_all_connections(self):
        allc = []
        for k in self.connecteds.keys():
            for c in self.connecteds[k][1]:
                allc.append(c + [k])

        return allc

    def get_default_next(self, from_point):
        max_dist = 0
        farthest = None
        f_k = None
        for k in self.connecteds.keys():
            dist = distance(self.connecteds[k][0], from_point)
            if dist > max_dist:
                max_dist = dist
                farthest = self.connecteds[k]
                f_k = k

        min_dist = None
        nearest = None
        if farthest is None:
            return None
        for f in farthest[1]:
            dist = distance(farthest[0], f[1])
            if min_dist is None or dist < min_dist:
                min_dist = dist
                nearest = f

        return nearest + [f_k]

    def get_value(self):
        shape_type = self.get_shape_type()

        if shape_type == ShapeEnum.NUMBER:
            return len(self.get_holes())
        elif shape_type == ShapeEnum.STACK and self.value is not None:
            return self.value[-1]

        return self.value

    def get_shape_type(self):
        this_points = len(self.points)
        if self.circular:
            this_points = 1
        this_shape = [this_points, cv2.isContourConvex(np.array(self.points))]
        hole_shapes = []
        for h in self.get_holes():
            points = len(h.points)
            if h.circular:

                points = 1
            hole_shapes.append((points, cv2.isContourConvex(np.array(self.points))))

        hole_shapes.sort()

        # print((tuple(this_shape), tuple(hole_shapes)))

        if (tuple(this_shape), tuple(hole_shapes)) in Shape.type_map.keys():
            return Shape.type_map[(tuple(this_shape), tuple(hole_shapes))]
        if len(hole_shapes) == 0:
            if (tuple(this_shape), False) in Shape.type_map.keys():
                return Shape.type_map[(tuple(this_shape), False)]
        if len(hole_shapes) > 0:
            if (tuple(this_shape), len(hole_shapes)) in Shape.type_map.keys():
                return Shape.type_map[(tuple(this_shape), len(hole_shapes))]
            if (tuple(this_shape), True) in Shape.type_map.keys():
                return Shape.type_map[(tuple(this_shape), True)]
        if (tuple(this_shape),) in Shape.type_map.keys():
            return Shape.type_map[(tuple(this_shape),)]

        return ShapeEnum.ANY

    def connect_shape(self, path_contour_index, shape, connecting_point, to_point):
        if path_contour_index in self.connecteds.keys():
            self.connecteds[path_contour_index][1].append([shape, to_point])
        else:
            self.connecteds[path_contour_index] = [
                connecting_point,
                [[shape, to_point]],
            ]

    def add_inside(self, shape):
        self.insides.append(shape)

    def get_hops_to_root(self):
        total = 0

        def _get_hops_to_root(shape):
            if shape.outer is not None:
                nonlocal total
                total += 1
                _get_hops_to_root(shape.outer)

        _get_hops_to_root(self)
        return total

    def get_leafs(self):
        leafs = []

        def _get_leafs(shape_):
            if shape_ is not None:
                if len(shape_.insides) == 0:
                    leafs.append(shape_)
                for i in shape_.insides:
                    _get_leafs(i)

        _get_leafs(self)
        return leafs

    def get_all_children(self):
        children = []

        def _get_all_children(shape_):
            if shape_ is not None:
                for i in shape_.insides:
                    children.append(i)
                    _get_all_children(i)

        _get_all_children(self)
        return children

    def get_holes(self):
        holes = []
        for c in self.get_all_children():
            distance_to_root = c.get_hops_to_root()
            if distance_to_root % 2 == 1:
                holes.append(c)
        return holes

from math import hypot


def distance(a, b):
    return hypot(b[0] - a[0], b[1] - a[1])

import numpy as np

SIZE_IN_BYTES = 4


class Shape:
    def __init__(self, v, i):
        self.vertices = v
        self.indices = i

def createMinecraftFloor(l=0.5):
    vertices = [
        # cara de arriba
        l, l, 0, 1, 0.5, #0
        -l, l, 0, 0.5, 0.5, #1
        l, -l, 0, 1, 0, #2
        -l, -l, 0, 0.5, 0, #3
    ]
    indices = [
        0, 2, 1, 1, 3, 2
    ]

    return Shape(vertices, indices)

def createMinecraftCube(l=0.5):
    vertices = [
        # caras de los lados
        -l, -l, -l, 0, 1, #0
        -l, -l, l, 0, 0.5, #1
        -l, l, l, 0.5, 0.5, #2
        -l, l, -l, 0.5, 1, #3
        l, -l, -l, 0.5, 1, #4
        l, -l, l, 0.5, 0.5, #5
        l, l, -l, 0, 1, #6
        l, l, l, 0, 0.5, #7
        # cara de arriba
        l, l, l, 1, 0.5, #8
        -l, l, l, 0.5, 0.5, #9
        l, -l, l, 1, 0, #10
        -l, -l, l, 0.5, 0, #11
        # cara de abajo
        l, l, -l, 0, 0.5, #12
        -l, l, -l, 0.5, 0.5, #13
        l, -l, -l, 0, 0, #14
        -l, -l, -l, 0.5, 0 #15
    ]
    indices = [
        0, 1, 2, 2, 3, 0,
        3, 2, 6, 7, 2, 6,
        7, 6, 4, 4, 5, 7,
        5, 0, 4, 5, 1, 0,
        8, 10, 11, 11, 9, 8,
        12, 13, 14, 14, 13, 15
    ]

    return Shape(vertices, indices)
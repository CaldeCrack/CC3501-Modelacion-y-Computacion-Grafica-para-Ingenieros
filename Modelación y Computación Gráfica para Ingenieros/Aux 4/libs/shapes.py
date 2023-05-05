class Shape:
    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = indices

    def __str__(self):
        return "vertices: " + str(self.vertices) + "\n"\
            "indices: " + str(self.indices)


def createTextureQuad(nx, ny):

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
    #   positions        texture
        -0.5, -0.5, 0.0,  0, ny,
         0.5, -0.5, 0.0, nx, ny,
         0.5,  0.5, 0.0, nx, 0,
        -0.5,  0.5, 0.0,  0, 0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    return Shape(vertices, indices)


def createTextureCube(nx, ny):

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
    #   positions         texture coordinates
    # Z+
        -0.5, -0.5,  0.5, 0, ny,
         0.5, -0.5,  0.5, nx, ny,
         0.5,  0.5,  0.5, nx, 0,
        -0.5,  0.5,  0.5, 0, 0,

    # Z-
        -0.5, -0.5, -0.5, 0, ny,
         0.5, -0.5, -0.5, nx, ny,
         0.5,  0.5, -0.5, nx, 0,
        -0.5,  0.5, -0.5, 0, 0,

    # X+
         0.5, -0.5, -0.5, 0, ny,
         0.5,  0.5, -0.5, nx, ny,
         0.5,  0.5,  0.5, nx, 0,
         0.5, -0.5,  0.5, 0, 0,

    # X-
        -0.5, -0.5, -0.5, 0, ny,
        -0.5,  0.5, -0.5, nx, ny,
        -0.5,  0.5,  0.5, nx, 0,
        -0.5, -0.5,  0.5, 0, 0,

    # Y+
        -0.5,  0.5, -0.5, 0, ny,
         0.5,  0.5, -0.5, nx, ny,
         0.5,  0.5,  0.5, nx, 0,
        -0.5,  0.5,  0.5, 0, 0,

    # Y-
        -0.5, -0.5, -0.5, 0, ny,
         0.5, -0.5, -0.5, nx, ny,
         0.5, -0.5,  0.5, nx, 0,
        -0.5, -0.5,  0.5, 0, 0
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0,  # Z+
          7, 6, 5, 5, 4, 7,  # Z-
          8, 9,10,10,11, 8,  # X+
         15,14,13,13,12,15,  # X-
         19,18,17,17,16,19,  # Y+
         20,21,22,22,23,20]  # Y-

    return Shape(vertices, indices)


def rubiksCube():

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
    #   positions         texture coordinates
    # Z+
        -0.5, -0.5,  0.5, 1/3, 2/4,
         0.5, -0.5,  0.5, 2/3, 2/4,
         0.5,  0.5,  0.5, 2/3, 1/4,
        -0.5,  0.5,  0.5, 1/3, 1/4,

    # Z-
        -0.5, -0.5, -0.5, 1/3, 4/4,
         0.5, -0.5, -0.5, 2/3, 4/4,
         0.5,  0.5, -0.5, 2/3, 3/4,
        -0.5,  0.5, -0.5, 1/3, 3/4,

    # X+
         0.5, -0.5, -0.5, 0/3, 2/4,
         0.5,  0.5, -0.5, 1/3, 2/4,
         0.5,  0.5,  0.5, 1/3, 1/4,
         0.5, -0.5,  0.5, 0/3, 1/4,

    # X-
        -0.5, -0.5, -0.5, 2/3, 2/4,
        -0.5,  0.5, -0.5, 3/3, 2/4,
        -0.5,  0.5,  0.5, 3/3, 1/4,
        -0.5, -0.5,  0.5, 2/3, 1/4,

    # Y+
        -0.5,  0.5, -0.5, 1/3, 1/4,
         0.5,  0.5, -0.5, 2/3, 1/4,
         0.5,  0.5,  0.5, 2/3, 0/4,
        -0.5,  0.5,  0.5, 1/3, 0/4,

    # Y-
        -0.5, -0.5, -0.5, 1/3, 3/4,
         0.5, -0.5, -0.5, 2/3, 3/4,
         0.5, -0.5,  0.5, 2/3, 2/4,
        -0.5, -0.5,  0.5, 1/3, 2/4
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0,  # Z+
          7, 6, 5, 5, 4, 7,  # Z-
          8, 9,10,10,11, 8,  # X+
         15,14,13,13,12,15,  # X-
         19,18,17,17,16,19,  # Y+
         20,21,22,22,23,20]  # Y-

    return Shape(vertices, indices)


def minecraftCube():

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
    #   positions         texture coordinates
    # Z+
        -0.5, -0.5,  0.5, 1/4, 2/3,
         0.5, -0.5,  0.5, 2/4, 2/3,
         0.5,  0.5,  0.5, 2/4, 1/3,
        -0.5,  0.5,  0.5, 1/4, 1/3,

    # Z-
        -0.5, -0.5, -0.5, 3/4, 2/3,
         0.5, -0.5, -0.5, 4/4, 2/3,
         0.5,  0.5, -0.5, 4/4, 1/3,
        -0.5,  0.5, -0.5, 3/4, 1/3,

    # X+
         0.5, -0.5, -0.5, 1/4, 3/3,
         0.5,  0.5, -0.5, 2/4, 3/3,
         0.5,  0.5,  0.5, 2/4, 2/3,
         0.5, -0.5,  0.5, 1/4, 2/3,

    # X-
        -0.5, -0.5, -0.5, 1/4, 3/3,
        -0.5,  0.5, -0.5, 2/4, 3/3,
        -0.5,  0.5,  0.5, 2/4, 2/3,
        -0.5, -0.5,  0.5, 1/4, 2/3,

    # Y+
        -0.5,  0.5, -0.5, 1/4, 3/3,
         0.5,  0.5, -0.5, 2/4, 3/3,
         0.5,  0.5,  0.5, 2/4, 2/3,
        -0.5,  0.5,  0.5, 1/4, 2/3,

    # Y-
        -0.5, -0.5, -0.5, 1/4, 3/3,
         0.5, -0.5, -0.5, 2/4, 3/3,
         0.5, -0.5,  0.5, 2/4, 2/3,
        -0.5, -0.5,  0.5, 1/4, 2/3
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0,  # Z+
          7, 6, 5, 5, 4, 7,  # Z-
          8, 9,10,10,11, 8,  # X+
         15,14,13,13,12,15,  # X-
         19,18,17,17,16,19,  # Y+
         20,21,22,22,23,20]  # Y-

    return Shape(vertices, indices)

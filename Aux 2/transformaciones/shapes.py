class Shape:
    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = indices

    def __str__(self):
        return "vertices: " + str(self.vertices) + "\n"\
            "indices: " + str(self.indices)

def createRainbowTriangle():

    vertices = [
    #   positions        colors
        -0.5, -0.5, 0.0,  1.0, 0.0, 0.0,
         0.5, -0.5, 0.0,  0.0, 1.0, 0.0,
         0.0,  0.5, 0.0,  0.0, 0.0, 1.0]

    indices = [0, 1, 2]

    return Shape(vertices, indices)


def createRainbowQuad():

    vertices = [
    #   positions        colors
        -0.5, -0.5, 0.0,  1.0, 0.0, 0.0,
         0.5, -0.5, 0.0,  0.0, 1.0, 0.0,
         0.5,  0.5, 0.0,  0.0, 0.0, 1.0,
        -0.5,  0.5, 0.0,  1.0, 1.0, 1.0]

    indices = [
        0, 1, 2,
        2, 3, 0]

    return Shape(vertices, indices)

def createGradientTriangle():

    vertices = [
    #   positions        colors
        -0.5, -0.5, 0.0,  1.0, 1.0, 1.0,
         0.5, -0.5, 0.0,  0.5, 0.5, 0.5,
         0.0,  0.5, 0.0,  0.0, 0.0, 0.0]

    indices = [0, 1, 2]

    return Shape(vertices, indices)
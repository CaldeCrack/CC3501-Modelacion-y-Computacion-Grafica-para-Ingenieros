# coding=utf-8
import pyglet
from OpenGL.GL import (glUseProgram, glClearColor, glEnable, GL_DEPTH_TEST,
                        glUniformMatrix4fv, glGetUniformLocation, GL_TRUE,
                        glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
                        glPolygonMode, GL_FRONT_AND_BACK, GL_FILL, GL_LINES)
import numpy as np
import grafica.transformations as tr
import grafica.basic_shapes as bs
from grafica.gpu_shape import createGPUShape
import libs.shaders as sh


WIDTH, HEIGHT = 800, 800


class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"Curvas"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.pipeline = sh.SimpleModelViewProjectionShaderProgram()
        self.step = 0


controller = Controller(width=WIDTH, height=HEIGHT)


# Funciones de las curvas
def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T


def hermiteMatrix(P1, P2, T1, T2):

    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, T1, T2), axis=1)

    # Hermite base matrix is a constant
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])

    return np.matmul(G, Mh)


def bezierMatrix(P0, P1, P2, P3):

    # Generate a matrix concatenating the columns
    G = np.concatenate((P0, P1, P2, P3), axis=1)

    # Bezier base matrix is a constant
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])

    return np.matmul(G, Mb)


# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)

    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)

    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T

    return curve


glClearColor(0.15, 0.15, 0.15, 1.0)

glEnable(GL_DEPTH_TEST)

glUseProgram(controller.pipeline.shaderProgram)


# Creating shapes on GPU memory
gpuAxis = createGPUShape(controller.pipeline, bs.createAxis(7))
gpuRedCube = createGPUShape(controller.pipeline, bs.createColorCube(1, 0, 0))
gpuGreenCube = createGPUShape(controller.pipeline, bs.createColorCube(0, 1, 0))


# Setting up the view transform
cam_radius = 10
camera_theta = np.pi/4
cam_x = cam_radius * np.sin(camera_theta)
cam_y = cam_radius * np.cos(camera_theta)
cam_z = cam_radius

viewPos = np.array([cam_x, cam_y, cam_z])

view = tr.lookAt(viewPos, np.array([0, 0, 0]), np.array([0, 0, 1]))

# Setting up the projection transform
projection = tr.ortho(-8, 8, -8, 8, 0.1, 100)

# Creamos las curvas

# Definimos una variable para tener el
# numero de iteraciones que consideraremos
N = 3000

# Creando una curva de Hermite
# Definimos los puntos
P1 = np.array([[0, 0, -5]]).T
P2 = np.array([[0, 0, 5]]).T
T1 = np.array([[60, 0, 0]]).T
T2 = np.array([[60, 0, 0]]).T

# Creamos la curva
GMh = hermiteMatrix(P1, P2, T1, T2)
HermiteCurve1 = evalCurve(GMh, N)

# Creando las curvas de Bezier

# Definimos los puntos de una primera curva
P0 = np.array([[0, 0, -5]]).T
P1 = np.array([[-10, 0, -5]]).T
P2 = np.array([[-10, 0, 0]]).T
P3 = np.array([[0, 0, 0]]).T

# Creamos la primera parte de la curva
M1 = bezierMatrix(P0, P1, P2, P3)
bezierCurve1 = evalCurve(M1, N//2)

# Definimos los puntos de una segunda curva
P4 = np.array([[0, 0, 0]]).T
P5 = np.array([[10, 0, 0]]).T
P6 = np.array([[10, 0, 5]]).T
P7 = np.array([[0, 0, 5]]).T

# Creamos la segunda parte de la curva
M2 = bezierMatrix(P4, P5, P6, P7)
bezierCurve2 = evalCurve(M2, N//2)

# Se pueden concatenar las 2 curvas de Bezier en una sola
BezierCurve = np.concatenate((bezierCurve1, bezierCurve2), axis=0)


@controller.event
def on_draw():
    controller.clear()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Agregamos los step para tener la cuena de las iteraciones
    # Si step es mayor a N, reseteamos su cuenta
    if controller.step >= N-1:
        controller.step = 0

    controller.step += 1

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    # En cada iteración actualizamos la posición del cubo rojo
    # Llamamos a la curva de Hermite definida
    transformRed = tr.matmul([
        tr.translate(HermiteCurve1[controller.step, 0], HermiteCurve1[controller.step, 1], HermiteCurve1[controller.step, 2])
    ])
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, transformRed)
    controller.pipeline.drawCall(gpuRedCube)


    # En cada iteración actualizamos la posición del cubo verde
    # Llamamos a la curva de Bezier definida
    transformGreen = tr.matmul([
        tr.translate(BezierCurve[controller.step, 0], BezierCurve[controller.step, 1], BezierCurve[controller.step, 2])
    ])
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, transformGreen)
    controller.pipeline.drawCall(gpuGreenCube)

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
    controller.pipeline.drawCall(gpuAxis, GL_LINES)


# Each time update is called, on_draw is called again
# That is why it is better to draw and update each one in a separated function
# We could also create 2 different gpuQuads and different transform for each
# one, but this would use more memory
def update(dt, controller):
    controller.total_time += dt


if __name__ == "__main__":
    # Try to call this function 60 times per second
    pyglet.clock.schedule(update, controller)
    # Set the view
    pyglet.app.run()

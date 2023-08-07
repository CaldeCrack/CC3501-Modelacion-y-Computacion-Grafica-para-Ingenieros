# coding=utf-8
"""Código de Ejemplo Auxiliar 3"""

import os.path
import sys
import glfw
import numpy as np
import pyglet
from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import grafica.easy_shaders as es
import grafica.scene_graph as sg
import grafica.basic_shapes as bs
import grafica.transformations as tr

# Controlador que permite comunicarse con la ventana de pyglet

class Controller(pyglet.window.Window):

    def __init__(self, width, height, title="Snowman via scene graph"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.fillPolygon = True
        self.pipeline = None
        self.repeats = 0


# Se asigna el ancho y alto de la ventana y se crea.
WIDTH, HEIGHT = 800, 800
controller = Controller(width=WIDTH, height=HEIGHT)
# Se asigna el color de fondo de la ventana
glClearColor(0.55, 0.55, 0.85, 1.0)

# Se configura el pipeline y se le dice a OpenGL que utilice ese shader
pipeline = es.SimpleTransformShaderProgram()
controller.pipeline = pipeline
glUseProgram(pipeline.shaderProgram)

# El controlador puede recibir inputs del usuario. Estas funciones define cómo manejarlos.


@controller.event
def on_key_press(symbol, modifiers):

    if symbol == pyglet.window.key.SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif symbol == glfw.KEY_ESCAPE:
        controller.close()

    else:
        print('Unknown key')

# Función que crea un triángulo de un color especificado


def createColorTriangle(r, g, b):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
        #   positions        colors
        -0.5, -0.5, 0.0,  r, g, b,
        0.5, -0.5, 0.0,  r, g, b,
        0.0,  0.5, 0.0,  r, g, b]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2]

    return bs.Shape(vertices, indices)


# Función que crea un círculo de una resolución, radio y color especificado
def createColorCircle(N, R, r, g, b):

    # First vertex at the center
    vertices = [0, 0, 0, r, g, b]
    indices = []

    dtheta = 2 * np.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            R * np.cos(theta), R * np.sin(theta), 0, r, g, b]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    return bs.Shape(vertices, indices)

# Función que crea un grafo de escena de un hombre de nieve


def createSnowman(pipeline):

    # Convenience function to ease initialization
    def createGPUShape(shape):
        gpuShape = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuShape)
        gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
        return gpuShape

    # basic GPUShapes
    gpuWhiteCircle = createGPUShape(createColorCircle(30, 1, 1, 1, 1))
    gpuBlackCircle = createGPUShape(createColorCircle(10, 1, 0, 0, 0))
    gpuBrownQuad = createGPUShape(bs.createColorQuad(0.6, 0.3, 0))
    gpuOrangeTriangle = createGPUShape(createColorTriangle(1, 0.6, 0))

    # Leaf nodes
    whiteCircleNode = sg.SceneGraphNode("whiteCircleNode")
    whiteCircleNode.childs = [gpuWhiteCircle]

    blackCircleNode = sg.SceneGraphNode("blackCircleNode")
    blackCircleNode.childs = [gpuBlackCircle]

    brownQuadNode = sg.SceneGraphNode("brownQuadNode")
    brownQuadNode.childs = [gpuBrownQuad]

    orangeTriangleNode = sg.SceneGraphNode("orangeTriangleNode")
    orangeTriangleNode.childs = [gpuOrangeTriangle]

    # Body
    snowballBody = sg.SceneGraphNode("snowballBody")
    snowballBody.transform = tr.scale(10, 10, 0)
    snowballBody.childs = [whiteCircleNode]

    arm = sg.SceneGraphNode("arm")
    arm.transform = tr.matmul([
        tr.translate(0, 5, 0),
        # tr.rotationZ(0),
        tr.scale(2, 10, 1)
    ])
    arm.childs = [brownQuadNode]

    leftArm = sg.SceneGraphNode("leftArm")
    leftArm.transform = tr.matmul([
        tr.translate(-7, 7, 0),
        tr.rotationZ(60 * np.pi / 180),
        # tr.scale(1, 1, 1)
    ])
    leftArm.childs = [arm]

    rightArm = sg.SceneGraphNode("rightArm")
    rightArm.transform = tr.matmul([
        tr.translate(7, 7, 0),
        tr.rotationZ(-60 * np.pi / 180),
        # tr.scale(1, 1, 1)
    ])
    rightArm.childs = [arm]

    body = sg.SceneGraphNode("body")
    body.transform = tr.translate(0, 10, 0)
    body.childs = [snowballBody, leftArm, rightArm]

    # Head
    snowballHead = sg.SceneGraphNode("snowballHead")
    snowballHead.transform = tr.scale(8, 8, 0)
    snowballHead.childs = [whiteCircleNode]

    leftEye = sg.SceneGraphNode("leftEye")
    leftEye.transform = tr.matmul([
        tr.translate(0, 5, 0),
        # tr.rotationZ(0),
        tr.scale(2, 2, 1)
    ])
    leftEye.childs = [blackCircleNode]

    rightEye = sg.SceneGraphNode("rightEye")
    rightEye.transform = tr.matmul([
        tr.translate(5, 5, 0),
        # tr.rotationZ(0),
        tr.scale(2, 2, 1)
    ])
    rightEye.childs = [blackCircleNode]

    baseTriangle = sg.SceneGraphNode("baseTriangle")
    baseTriangle.transform = tr.matmul([
        tr.translate(0, 3.5, 0),
        # tr.rotationZ(0),
        tr.scale(2, 7, 1)
    ])
    baseTriangle.childs = [orangeTriangleNode]

    nose = sg.SceneGraphNode("nose")
    nose.transform = tr.matmul([
        tr.translate(2, 0, 0),
        tr.rotationZ(-70 * np.pi / 180),
        # tr.scale(1, 1, 1)
    ])
    nose.childs = [baseTriangle]

    head = sg.SceneGraphNode("head")
    head.transform = tr.translate(0, 27, 0)
    head.childs = [snowballHead, leftEye, rightEye, nose]

    # Snowman, the one and only
    snowman = sg.SceneGraphNode("snowman")
    snowman.childs = [head, body]

    return snowman

# Esta función se ejecuta aproximadamente 60 veces por segundo, dt es el tiempo entre la última
# ejecución y ahora


def update(dt, controller):
    controller.total_time += dt

# Cada vez que se llama update(), se llama esta función también


@controller.event
def on_draw():
    controller.clear()

    # Si el controller está en modo fillPolygon, dibuja polígonos. Si no, líneas.
    if controller.fillPolygon:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # Creating shapes on GPU memory
    snowman = createSnowman(pipeline)

    theta = np.sin(3.0 * controller.total_time)

    leftArm = sg.findNode(snowman, "leftArm")
    leftArm.transform = tr.matmul([
        tr.translate(-7, 7, 0),
        tr.rotationZ(theta),
        # tr.scale(1, 1, 1)
    ])

    rightArm = sg.findNode(snowman, "rightArm")
    rightArm.transform = tr.matmul([
        tr.translate(7, 7, 0),
        tr.rotationZ(theta),
        # tr.scale(1, 1, 1)
    ])

    # Drawing the Car
    sg.drawSceneGraphNode(snowman, pipeline, "transform",
                          np.matmul(tr.translate(0, -0.5, 0), tr.scale(0.03, 0.03, 1)))


# Try to call this function 60 times per second
pyglet.clock.schedule(update, controller)
# Se ejecuta la aplicación
pyglet.app.run()

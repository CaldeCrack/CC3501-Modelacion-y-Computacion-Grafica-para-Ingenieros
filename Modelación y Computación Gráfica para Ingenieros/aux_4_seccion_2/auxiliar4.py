# coding=utf-8
"""Código de Ejemplo Auxiliar 4"""

import os.path
import sys
import numpy as np
import pyglet
from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es

__author__ = "Daniel Calderon"
__license__ = "MIT"


# Controlador que permite comunicarse con la ventana de pyglet
class Controller(pyglet.window.Window):

    def __init__(self, width, height, title="3D cars via scene graph"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.fillPolygon = True
        self.showAxis = True
        self.pipeline = None
        self.repeats = 0


# Se asigna el ancho y alto de la ventana y se crea.
WIDTH, HEIGHT = 1280, 800
controller = Controller(width=WIDTH, height=HEIGHT)
# Se asigna el color de fondo de la ventana
glClearColor(0.85, 0.85, 0.85, 1.0)

# Como trabajamos en 3D, necesitamos chequear cuáles objetos están en frente, y cuáles detrás.
glEnable(GL_DEPTH_TEST)

# Se configura el pipeline y se le dice a OpenGL que utilice ese shader
mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
controller.pipeline = mvpPipeline
glUseProgram(mvpPipeline.shaderProgram)

# El controlador puede recibir inputs del usuario. Estas funciones define cómo manejarlos.
@controller.event
def on_key_press(symbol, modifiers):

    if symbol == pyglet.window.key.SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif symbol == pyglet.window.key.LCTRL:
        controller.showAxis = not controller.showAxis

    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()

# Función que crea un grafo de escena de un autito en 3D
def createCar(pipeline, r, g, b):

    # Creating shapes on GPU memory
    blackCube = bs.createColorCube(0,0,0)
    gpuBlackCube = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBlackCube)
    gpuBlackCube.fillBuffers(blackCube.vertices, blackCube.indices, GL_STATIC_DRAW)

    chasisCube = bs.createColorCube(r,g,b)
    gpuChasisCube = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuChasisCube)
    gpuChasisCube.fillBuffers(chasisCube.vertices, chasisCube.indices, GL_STATIC_DRAW)

    # Cheating a single wheel
    wheel = sg.SceneGraphNode("wheel")
    wheel.transform = tr.scale(0.2, 0.8, 0.2)
    wheel.childs += [gpuBlackCube]

    wheelRotation = sg.SceneGraphNode("wheelRotation")
    wheelRotation.childs += [wheel]

    # Instanciating 2 wheels, for the front and back parts
    frontWheel = sg.SceneGraphNode("frontWheel")
    frontWheel.transform = tr.translate(0.3,0,-0.3)
    frontWheel.childs += [wheelRotation]

    backWheel = sg.SceneGraphNode("backWheel")
    backWheel.transform = tr.translate(-0.3,0,-0.3)
    backWheel.childs += [wheelRotation]

    # Creating the chasis of the car
    chasis = sg.SceneGraphNode("chasis")
    chasis.transform = tr.scale(1,0.7,0.5)
    chasis.childs += [gpuChasisCube]

    # All pieces together
    car = sg.SceneGraphNode("car")
    car.childs += [chasis]
    car.childs += [frontWheel]
    car.childs += [backWheel]

    return car

# Creating shapes on GPU memory
cpuAxis = bs.createAxis(7)
gpuAxis = es.GPUShape().initBuffers()
mvpPipeline.setupVAO(gpuAxis)
gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)

redCarNode = createCar(mvpPipeline, 1, 0, 0)
blueCarNode = createCar(mvpPipeline, 0, 0, 1)

# Esta función se ejecuta aproximadamente 60 veces por segundo, dt es el tiempo entre la última
# ejecución y ahora
def update(dt, window):
    window.total_time += dt

# Cada vez que se llama update(), se llama esta función también
@controller.event
def on_draw():
    controller.clear()

    # Si el controller está en modo fillPolygon, dibuja polígonos. Si no, líneas.
    if controller.fillPolygon:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    blueCarNode.transform = np.matmul(tr.rotationZ(-np.pi/4), tr.translate(3.0,0,0.5))

    # Using the same view and projection matrices in the whole application
    projection = tr.perspective(45, float(WIDTH)/float(HEIGHT), 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE,
                       projection)

    view = tr.lookAt(
            np.array([5,5,7]),
            np.array([0,0,0]),
            np.array([0,0,1])
        )
    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    if controller.showAxis:
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE,
                           tr.identity())
        mvpPipeline.drawCall(gpuAxis, GL_LINES)

    # Moving the red car and rotating its wheels
    redCarNode.transform = tr.translate(3 * np.sin(controller.total_time),0,0.5)
    redWheelRotationNode = sg.findNode(redCarNode, "wheelRotation")
    redWheelRotationNode.transform = tr.rotationY(-10 * controller.total_time)

    # Drawing the Car
    sg.drawSceneGraphNode(redCarNode, mvpPipeline, "model")
    sg.drawSceneGraphNode(blueCarNode, mvpPipeline, "model")

# Try to call this function 60 times per second
pyglet.clock.schedule(update, controller)
# Se ejecuta la aplicación
pyglet.app.run()

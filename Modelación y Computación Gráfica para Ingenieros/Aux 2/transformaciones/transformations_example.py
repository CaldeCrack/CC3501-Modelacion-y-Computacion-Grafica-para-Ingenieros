# coding=utf-8
"""Drawing 4 shapes with different transformations"""

import pyglet
from OpenGL.GL import *

from math import cos, sin

import shapes
import shaders
from gpu_shape import createGPUShape
import transformations as tr


class Controller(pyglet.window.Window):

    def __init__(self, width, height, title="Pyglet window"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.fillPolygon = True
        self.pipeline = shaders.SimpleTransformShaderProgram()
        self.shapes = []
        self.shapes_index = 0
        self.repeats = 0
        self.translation = [0.0, 0.0, 0.0]

    def setShapes(self, s):
        self.shapes = s

    def nextShape(self):
        self.shapes_index = (self.shapes_index + 1) % len(self.shapes) 

# We will use the global controller as communication with the callback function
WIDTH, HEIGHT = 1280, 800
controller = Controller(width=WIDTH, height=HEIGHT)

# Setting up the clear screen color
glClearColor(0.15, 0.15, 0.15, 1.0)

# Setting the model (data of our code)
# Creating our shader program and telling OpenGL to use it


glUseProgram(controller.pipeline.shaderProgram)

gpuTriangle = createGPUShape(controller.pipeline,
                             shapes.createRainbowTriangle())
gpuQuad = createGPUShape(controller.pipeline, shapes.createRainbowQuad())
gpuGradientTriangle = createGPUShape(controller.pipeline,
                                     shapes.createGradientTriangle())
controller.setShapes([gpuTriangle, gpuQuad, gpuGradientTriangle])


# What happens when the user presses these keys
@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.SPACE:
        controller.fillPolygon = not controller.fillPolygon
    if symbol == pyglet.window.key.LEFT:
        controller.translation[0] -= 0.1
    if symbol == pyglet.window.key.RIGHT:
        controller.translation[0] += 0.1
    if symbol == pyglet.window.key.UP:
        controller.translation[1] += 0.1
    if symbol == pyglet.window.key.DOWN:
        controller.translation[1] -= 0.1
    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()


@controller.event
def on_draw():
    controller.clear()
    transform = tr.translate(*controller.translation)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "transform"),
                       1, GL_TRUE, transform)
    controller.pipeline.drawCall(controller.shapes[controller.shapes_index])


# Each time update is called, on_draw is called again
# That is why it is better to draw and update each one in a separated function
# We could also create 2 different gpuQuads and different transform for each
# one, but this would use more memory
def update(dt, controller):
    controller.total_time += dt


# Try to call this function 60 times per second
pyglet.clock.schedule(update, controller)
# Set the view
pyglet.app.run()

# coding=utf-8
"""Showing how to handle textures on a cube"""

import sys
import os
import pyglet
import numpy as np

import libs.shaders as sh
import libs.transformations as tr

from libs.gpu_shape import createGPUShape
from libs.obj_handler import read_OBJ
from libs.assets_path import getAssetPath

from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
Controles:
    - WASD: Movimiento de camara

    - '+': Zoom-in
    - '-': Zoom-out

"""

WIDTH, HEIGHT = 800, 800

PERSPECTIVE_PROJECTION = 0
ORTOGRAPHIC_PROJECTION = 1

PROJECTIONS = [
    tr.perspective(60, float(WIDTH)/float(HEIGHT), 0.1, 100),  # PERSPECTIVE_PROJECTION
    tr.ortho(-8, 8, -8, 8, 0.1, 100)  # ORTOGRAPHIC_PROJECTION
]

ASSETS = {
    "pochita_obj": getAssetPath("pochita3.obj"),
}


class Controller(pyglet.window.Window):

    def __init__(self, width, height, title="Pochita :3"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.pipeline = sh.SimpleModelViewProjectionShaderProgram()

        self.obj_color = (0.7, 0.2, 0.6)
        self.ex_shape = createGPUShape(self.pipeline,read_OBJ(ASSETS["pochita_obj"], self.obj_color))



class Camera:

    def __init__(self, at=np.array([0.0, 0.0, 0.0]), eye=np.array([1.0, 1.0, 1.0]), up=np.array([0.0, 0.0, 1.0])) -> None:
        # View parameters
        self.at = at
        self.eye = eye
        self.up = up

        # Spherical coordinates
        self.R = np.sqrt(np.square(self.eye[0]) + np.square(self.eye[1]) + np.square(self.eye[2]))
        self.theta = np.arccos(self.eye[2]/self.R) # vertical
        self.phi = np.arctan(self.eye[1]/self.eye[0]) # horizontal

        # Movement/Rotation speed
        self.phi_speed = 0.1
        self.theta_speed = 0.1
        self.R_speed = 0.1

        # Movement/Rotation direction
        self.phi_direction = 0
        self.theta_direction = 0
        self.R_direction = 0

        # Projections
        self.available_projections = PROJECTIONS
        self.projection = self.available_projections[PERSPECTIVE_PROJECTION]

    def set_projection(self, projection_name):
        self.projection = self.available_projections[projection_name]

    def update(self):
        self.R += self.R_speed * self.R_direction
        self.theta += self.theta_speed * self.theta_direction
        self.phi += self.phi_speed * self.phi_direction

        # Spherical coordinates
        self.eye[0] = self.R * np.sin(self.theta) * np.cos(self.phi)
        self.eye[1] = self.R * np.sin(self.theta) * np.sin(self.phi)
        self.eye[2] = (self.R) * np.cos(self.theta)


camera = Camera()
controller = Controller(width=WIDTH, height=HEIGHT)


# Setting up the clear screen color
glClearColor(0.1, 0.1, 0.1, 1.0)

glEnable(GL_DEPTH_TEST)

glUseProgram(controller.pipeline.shaderProgram)

# What happens when the user presses these keys
@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.P:
        camera.set_projection(PERSPECTIVE_PROJECTION)
    if symbol == pyglet.window.key.O:
        camera.set_projection(ORTOGRAPHIC_PROJECTION)
    if symbol == pyglet.window.key.A:
        camera.phi_direction -= 1
    if symbol == pyglet.window.key.D:
        camera.phi_direction += 1
    if symbol == pyglet.window.key.W:
        camera.theta_direction -= 1
    if symbol == pyglet.window.key.S:
        camera.theta_direction += 1
    if symbol == pyglet.window.key.PLUS:
        camera.R_direction -= 1
    if symbol == pyglet.window.key.MINUS:
        camera.R_direction += 1

    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()

# What happens when the user releases these keys
@controller.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.A:
        camera.phi_direction += 1
    if symbol == pyglet.window.key.D:
        camera.phi_direction -= 1
    if symbol == pyglet.window.key.W:
        camera.theta_direction += 1
    if symbol == pyglet.window.key.S:
        camera.theta_direction -= 1
    if symbol == pyglet.window.key.PLUS:
        camera.R_direction += 1
    if symbol == pyglet.window.key.MINUS:
        camera.R_direction -= 1


@controller.event
def on_draw():
    controller.clear()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    camera.update()

    view = tr.lookAt(
        camera.eye,
        camera.at,
        camera.up
    )

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    controller.pipeline.drawCall(controller.ex_shape)


# Each time update is called, on_draw is called again
# That is why it is better to draw and update each one in a separated function
# We could also create 2 different gpuQuads and different transform for each
# one, but this would use more memory
def update(dt, controller):
    controller.total_time += dt


if __name__ == '__main__':
    # Try to call this function 60 times per second
    pyglet.clock.schedule(update, controller)
    # Set the view
    pyglet.app.run()

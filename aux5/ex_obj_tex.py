# coding=utf-8
import sys
import os
import pyglet
import numpy as np

import libs.shaders as sh
import libs.transformations as tr

from libs.gpu_shape import createGPUShape
from libs.obj_handler import read_OBJ2
from libs.assets_path import getAssetPath

from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WIDTH, HEIGHT = 800, 800

PERSPECTIVE_PROJECTION = 0
ORTOGRAPHIC_PROJECTION = 1

PROJECTIONS = [
    tr.perspective(100, float(WIDTH)/float(HEIGHT), 0.1, 100),  # PERSPECTIVE_PROJECTION
    tr.ortho(-6, 6, -6, 6, 0.1, 100)  # ORTOGRAPHIC_PROJECTION
]

ASSETS = {
    "pochita_obj": getAssetPath("pochita3.obj"),
    "pochita_tex": getAssetPath("pochita.png"),
}


class Controller(pyglet.window.Window):

    def __init__(self, width, height, title=f"Pochita :3"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.pipeline = sh.SimpleTextureModelViewProjectionShaderProgram()

        self.ex_shape = createGPUShape(self.pipeline, read_OBJ2(ASSETS["pochita_obj"]))

        self.tex_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
        self.current_tex = ASSETS["pochita_tex"]

        self.ex_shape.texture = sh.textureSimpleSetup(
            self.current_tex, *self.tex_params
        )


class Camera:

    def __init__(self, at=np.array([0.0, 0.0, 0.0]), eye=np.array([1.0, 1.0, 1.0]), up=np.array([0.0, 0.0, 1.0])) -> None:
        # View parameters
        self.at = at
        self.eye = eye
        self.up = up

        self.x = np.square(self.eye[0])
        self.y = np.square(self.eye[1])
        self.z = np.square(self.eye[2])

        # Movement/Rotation speed
        self.x_speed = 0.1
        self.y_speed = 0.1
        self.z_speed = 0.1

        # Movement/Rotation direction
        self.x_direction = 0
        self.y_direction = 0
        self.z_direction = 0

        # Projections
        self.available_projections = PROJECTIONS
        self.projection = self.available_projections[PERSPECTIVE_PROJECTION]

    def set_projection(self, projection_name):
        self.projection = self.available_projections[projection_name]

    def update(self):
        self.x += self.x_speed * self.x_direction
        self.y += self.y_speed * self.y_direction
        self.z += self.z_speed * self.z_direction

        # Spherical coordinates
        self.eye[0] = self.x
        self.eye[1] = self.y
        self.eye[2] = self.z
        self.at[0] = self.x-1
        self.at[1] = self.y-1
        self.at[2] = self.z-1


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
        camera.x_direction -= 1
    if symbol == pyglet.window.key.D:
        camera.x_direction += 1
    if symbol == pyglet.window.key.W:
        camera.y_direction -= 1
    if symbol == pyglet.window.key.S:
        camera.y_direction += 1
    if symbol == pyglet.window.key.PLUS:
        camera.z_direction -= 1
    if symbol == pyglet.window.key.MINUS:
        camera.z_direction += 1

    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()

# What happens when the user releases these keys
@controller.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.A:
        camera.x_direction += 1
    if symbol == pyglet.window.key.D:
        camera.x_direction -= 1
    if symbol == pyglet.window.key.W:
        camera.y_direction += 1
    if symbol == pyglet.window.key.S:
        camera.y_direction -= 1
    if symbol == pyglet.window.key.PLUS:
        camera.z_direction += 1
    if symbol == pyglet.window.key.MINUS:
        camera.z_direction -= 1


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
    pyglet.clock.schedule(update, controller)
    pyglet.app.run()

# coding=utf-8
"""Showing how to handle textures on a cube"""

import sys
import os
import pyglet
import numpy as np

import libs.shaders as sh
import libs.transformations as tr

from libs.gpu_shape import createGPUShape
from libs.assets_path import getAssetPath

from libs.shapes import read_OFF

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
    "sphere_off": getAssetPath("sphere.off"),
}


class Controller(pyglet.window.Window):

    def __init__(self, width, height, title=f"Pochita :3"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.pipeline = sh.MultipleLightPhongShaderProgram()

        self.obj_color = (0.7, 0.2, 0.6)
        self.ex_shape = createGPUShape(self.pipeline,
                                       read_OFF(ASSETS["sphere_off"], self.obj_color))
        self.rotation = 0.0
        self.lines = False

    def set_mode(self):
        self.lines = not self.lines

    def get_mode(self):
        if self.lines:
            return GL_LINES
        return GL_TRIANGLES


class PointLight:
    def __init__(self, pos: list) -> None:
        self.attribs = {
            "position": np.array(pos),
            "ambient": np.array([0.2, 0.2, 0.2]),
            "diffuse": np.array([0.9, 0.9, 0.9]),
            "specular": np.array([1.0, 1.0, 1.0]),
            "constant": 0.1,
            "linear": 0.1,
            "quadratic": 0.01
        }

    def set_pos(self, x, y, z):
        self.attribs["position"] = np.array([x, y, z])

    def set_ambient(self, r, g, b):
        self.attribs["ambient"] = np.array([r, g, b])

    def set_diffuse(self, r, g, b):
        self.attribs["diffuse"] = np.array([r, g, b])

    def set_specular(self, r, g, b):
        self.attribs["specular"] = np.array([r, g, b])

    def show_colors(self):
        colors = f"ambient: ({self.attribs['ambient']})\n"
        colors += f"diffuse: ({self.attribs['diffuse']})\n"
        colors += f"specular: ({self.attribs['specular']})\n"
        return colors


class Camera:

    def __init__(self, at=np.array([0.0, 0.0, 0.0]), eye=np.array([2.0, 2.0, 2.0]), up=np.array([0.0, 0.0, 1.0])) -> None:
        # View parameters
        self.at = at
        self.eye = eye
        self.up = up

        # Spherical coordinates
        self.R = np.sqrt(np.square(self.eye[0]) + np.square(self.eye[1]) + np.square(self.eye[2]))
        self.theta = np.arccos(self.eye[2]/self.R)
        self.phi = np.arctan(self.eye[1]/self.eye[0])

        # Movement/Rotation speed
        self.phi_speed = 0.1
        self.theta_speed = 0.1
        self.R_speed = 0.1

        # Movement/Rotation direction
        self.phi_direction = 0.0
        self.theta_direction = 0.0
        self.R_direction = 0.0

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
pointlights = []

pointlights.append(PointLight([10.0, 10.0, 5.0]))
pointlights.append(PointLight([-10.0, 10.0, 5.0]))
pointlights.append(PointLight([10.0, -10.0, 5.0]))
pointlights.append(PointLight([-10.0, -10.0, 5.0]))

# Setting up the clear screen color
glClearColor(0.1, 0.1, 0.1, 1.0)

glEnable(GL_DEPTH_TEST)

glUseProgram(controller.pipeline.shaderProgram)

glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "material.ambient"), 0.2, 0.2, 0.2)
glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "material.diffuse"), 0.9, 0.9, 0.9)
glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "material.specular"), 1.0, 1.0, 1.0)
glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, "material.shininess"), 32)


def update_lights():
    for i, pointlight in enumerate(pointlights):
        random_color = np.random.rand(3)
        pointlight.set_ambient(*(random_color * 0.2))
        pointlight.set_diffuse(*(random_color * 0.9))
        pointlight.set_specular(*(random_color * 1.0))
        print(f"Luz puntual {i+1}:\n{pointlight.show_colors()}")
        for key in pointlight.attribs.keys():
            attrib = pointlight.attribs[key]
            if isinstance(attrib, float):
                glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, f"pointLights[{i}].{key}"), attrib)
            elif isinstance(attrib, np.ndarray):
                glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, f"pointLights[{i}].{key}"), *attrib)


update_lights()

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
    if symbol == pyglet.window.key.L:
        update_lights()
    if symbol == pyglet.window.key.LCTRL:
        controller.set_mode()

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

    controller.rotation += 0.05

    transformations = tr.matmul([tr.rotationZ(controller.rotation), tr.rotationX(np.pi/2)])

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, transformations)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    controller.pipeline.drawCall(controller.ex_shape, mode=controller.get_mode())


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

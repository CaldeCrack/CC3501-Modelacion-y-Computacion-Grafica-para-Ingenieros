# coding=utf-8
# Useful imports
import sys
import os
import pyglet
import numpy as np
import libs.shaders as sh
import libs.transformations as tr
import libs.scene_graph as sg
import libs.basic_shapes as bs
import libs.easy_shaders as es

from libs.gpu_shape import createGPUShape
from libs.obj_handler import read_OBJ2
from libs.assets_path import getAssetPath
from OpenGL.GL import *

# Initial data
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WIDTH, HEIGHT = 800, 800
ASSETS = {
    "pochita_obj": getAssetPath("pochita3.obj"),
    "pochita_tex": getAssetPath("pochita.png"),
}

# Controller of the pyglet window
class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"Pochita :3"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.pipeline = sh.SimpleTextureModelViewProjectionShaderProgram()

        # Ship model and texture
        self.ex_shape = createGPUShape(self.pipeline, read_OBJ2(ASSETS["pochita_obj"]))
        self.tex_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
        self.current_tex = ASSETS["pochita_tex"]
        self.ex_shape.texture = sh.textureSimpleSetup(self.current_tex, *self.tex_params)

# Camera which controls the projection and view
class Camera:
    def __init__(self, at=np.array([0.0, 0.0, 0.0]), eye=np.array([5.0, 5.0, 5.0]), up=np.array([0.0, 0.0, 1.0])) -> None:
        # View parameters
        self.at = at
        self.eye = eye
        self.up = up

        # Cartesian coordinates
        self.x = np.square(self.eye[0])
        self.y = np.square(self.eye[1])
        self.z = np.square(self.eye[2])

        # Ortographic projection
        self.projection = tr.ortho(-5, 5, -5, 5, 0.1, 100)

    def set_projection(self, projection_name):
        self.projection = self.available_projections[projection_name]

    # Follow the ship
    def update(self, coords):
        self.eye[0] = self.x+coords[0]
        self.eye[1] = self.y+coords[1]
        self.eye[2] = self.z+coords[2]
        self.at[0] = coords[0]
        self.at[1] = coords[1]
        self.at[2] = coords[2]

# Setup of the window
camera = Camera()
controller = Controller(width=WIDTH, height=HEIGHT)


glClearColor(0.05, 0.05, 0.12, 1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(controller.pipeline.shaderProgram)

# Setup of the objects in the scene
pochita = sg.SceneGraphNode("pochita")
pochita.childs += [controller.ex_shape]

# What happens when the user presses these keys
@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.A:
        pass
    if symbol == pyglet.window.key.D:
        pass
    if symbol == pyglet.window.key.W:
        pass
    if symbol == pyglet.window.key.S:
        pass
    if symbol == pyglet.window.key.PLUS:
        pass
    if symbol == pyglet.window.key.MINUS:
        pass
    # Close the window
    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()

# What happens when the user releases these keys
@controller.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.A:
        pass
    if symbol == pyglet.window.key.D:
        pass
    if symbol == pyglet.window.key.W:
        pass
    if symbol == pyglet.window.key.S:
        pass
    if symbol == pyglet.window.key.PLUS:
        pass
    if symbol == pyglet.window.key.MINUS:
        pass

# What draws at every frame
@controller.event
def on_draw():
    controller.clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    move = [tr.rotationZ(np.pi), tr.rotationX(np.pi/2), tr.translate(5 * np.sin(controller.total_time), 0, 0)]
    pochita.transform = tr.matmul(move)
    pochita_coords = sg.findPosition(pochita, "pochita")
    camera.update(pochita_coords)
    view = tr.lookAt(
        camera.eye,
        camera.at,
        camera.up
    )
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)


    sg.drawSceneGraphNode(pochita, controller.pipeline, "model")

# Set a time in controller
def update(dt, controller):
    controller.total_time += dt

# Start the scene
if __name__ == '__main__':
    pyglet.clock.schedule(update, controller)
    pyglet.app.run()
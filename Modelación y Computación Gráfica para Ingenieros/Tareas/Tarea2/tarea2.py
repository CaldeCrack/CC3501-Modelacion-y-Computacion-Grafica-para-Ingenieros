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
    "pochita_obj": getAssetPath("pochita2.obj"),
    "pochita_tex": getAssetPath("pochita.png"),
    "cube_obj": getAssetPath("cube.obj"),
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
        self.projection = tr.ortho(-6, 6, -6, 6, 0.1, 100)

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

# Movement of the ship#*s
class Movement:
    def __init__(self, at=np.array([1.0, 0.0, 0.0]), eye=np.array([0.0, 0.0, 0.0]), up=np.array([0.0, 0.0, 1.0]), rotationZ=np.array([0.0])) -> None:
        # Local coordinates
        self.at = at
        self.eye = eye
        self.up = up
        self.rotationZ = rotationZ

        # Cartesian coordinates
        self.x = np.square(self.eye[0])
        self.y = np.square(self.eye[1])
        self.z = np.square(self.eye[2])

        # Rotations
        self.z_rotation = 0

        # Directions
        self.x_direction = 0
        self.y_direction = 0
        self.z_direction = 0

    # Move the ship
    def update(self):
        self.eye[0] += self.x_direction*0.1
        self.eye[1] += self.y_direction*0.1
        self.eye[2] += self.z_direction*0.1
        self.rotationZ[0] += self.z_rotation*0.1

# Setup of the window
camera = Camera()
movement = Movement()
controller = Controller(width=WIDTH, height=HEIGHT)

glClearColor(0.05, 0.05, 0.1, 1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(controller.pipeline.shaderProgram)

# Setup of the objects in the scene
ship = sg.SceneGraphNode("ship")
shipRotation = sg.SceneGraphNode("shipRotation")
shipRotation.childs += [controller.ex_shape]
ship.childs += [shipRotation]

cube = createGPUShape(controller.pipeline, read_OBJ2(ASSETS["cube_obj"]))
cube.texture = sh.textureSimpleSetup(controller.current_tex, *controller.tex_params)

platform = sg.SceneGraphNode("platform")
platform.childs += [cube]

# What happens when the user presses these keys
@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.A:
        movement.z_rotation += 1
    if symbol == pyglet.window.key.D:
        movement.z_rotation -= 1
    if symbol == pyglet.window.key.W:
        movement.x_direction += 1
    if symbol == pyglet.window.key.S:
        movement.x_direction -= 1
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
        movement.z_rotation -= 1
    if symbol == pyglet.window.key.D:
        movement.z_rotation += 1
    if symbol == pyglet.window.key.W:
        movement.x_direction -= 1
    if symbol == pyglet.window.key.S:
        movement.x_direction += 1
    if symbol == pyglet.window.key.PLUS:
        pass
    if symbol == pyglet.window.key.MINUS:
        pass

# What draws at every frame
@controller.event
def on_draw():
    # Clear window every frame
    controller.clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Ship movement
    movement.update()
    pochita_move = [tr.rotationZ(movement.rotationZ[0]), tr.translate(movement.eye[0], 0, 0)]

    # Camera tracking of the ship
    pochita_coords = sg.findPosition(ship, "shipRotation")
    camera.update(pochita_coords)

    # Projection and view
    view = tr.lookAt(
        camera.eye,
        camera.at,
        camera.up
    )
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    pochitaShip = sg.findNode(ship, "shipRotation")
    pochitaShip.transform = tr.matmul(pochita_move)
    
    # Drawing of the scene graph
    platform.transform = np.matmul(tr.scale(20, 20, 0.25), tr.translate(0, 0, -1))
    sg.drawSceneGraphNode(platform, controller.pipeline, "model")
    sg.drawSceneGraphNode(ship, controller.pipeline, "model")

# Set a time in controller
def update(dt, controller):
    controller.total_time += dt

# Start the scene
if __name__ == '__main__':
    pyglet.clock.schedule(update, controller)
    pyglet.app.run()
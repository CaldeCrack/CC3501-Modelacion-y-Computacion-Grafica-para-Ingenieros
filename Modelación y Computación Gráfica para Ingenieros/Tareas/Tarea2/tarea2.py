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
    def __init__(self, at=np.array([1.0, 0.0, 0.0]), eye=np.array([0.0, 0.0, 1.0]), up=np.array([0.0, 0.0, 1.0]), rotation_y=0, rotation_z=0) -> None:
        # Initial setup
        self.at = at
        self.eye = eye
        self.up = up

        # Rotations
        self.rotation_y = rotation_y
        self.rotation_z = rotation_z

        # Local x axis direction
        self.x_direction = 0

        # Angles
        self.y_angle = 0
        self.z_angle = 0

    # Move the ship
    def update(self):
        # Update facing angle of the ship
        self.rotation_y += self.y_angle*0.1
        self.rotation_z += self.z_angle*0.1

        # Move in the local x axis
        self.eye[0] += self.x_direction*0.1 *np.cos(self.rotation_y)*np.cos(self.rotation_z)
        self.eye[1] += self.x_direction*0.1 *np.cos(self.rotation_y)*np.sin(self.rotation_z)
        self.eye[2] += self.x_direction*0.1 *np.sin(self.rotation_y)*-1

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
        movement.z_angle += 1
    if symbol == pyglet.window.key.D:
        movement.z_angle -= 1
    if symbol == pyglet.window.key.W:
        movement.x_direction += 1
    if symbol == pyglet.window.key.S:
        movement.x_direction -= 1
    if symbol == pyglet.window.key.PLUS:
        movement.y_angle -= 1
    if symbol == pyglet.window.key.MINUS:
        movement.y_angle += 1
    # Close the window
    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()

# What happens when the user releases these keys
@controller.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.A:
        movement.z_angle -= 1
    if symbol == pyglet.window.key.D:
        movement.z_angle += 1
    if symbol == pyglet.window.key.W:
        movement.x_direction -= 1
    if symbol == pyglet.window.key.S:
        movement.x_direction += 1
    if symbol == pyglet.window.key.PLUS:
        movement.y_angle += 1
    if symbol == pyglet.window.key.MINUS:
        movement.y_angle -= 1

# What draws at every frame
@controller.event
def on_draw():
    # Clear window every frame
    controller.clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Ship movement
    movement.update()
    ship_coords = sg.findPosition(ship, "shipRotation")
    ship_rot = [tr.rotationZ(movement.rotation_z), tr.rotationY(movement.rotation_y)] #! rotacion del personaje
    ship_move = [tr.translate(movement.eye[0], movement.eye[1], movement.eye[2])] #! movimiento del personaje

    # Camera tracking of the ship
    camera.update(ship_coords)

    # Projection and view
    view = tr.lookAt(
        camera.eye,
        camera.at,
        camera.up
    )
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    shipShip = sg.findNode(ship, "shipRotation")
    shipShip.transform = tr.matmul(ship_rot)
    ship.transform = tr.matmul(ship_move)

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
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
#! icono pal juego xd
ASSETS = {
    "ship_obj": getAssetPath("ship.obj"),
    "ship_tex": getAssetPath("ship.png"),
    "cube_obj": getAssetPath("cube.obj"),
}
forward = False

# Aspect ratio and projection
display = pyglet.canvas.Display()
screen = display.get_default_screen()
screen_height = screen.height
screen_width = screen.width
ORTHO = tr.ortho(-7*screen_width/screen_height, 7*screen_width/screen_height, -7, 7, 0.1, 100)

# Controller of the pyglet window
class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"La mejor tarea 2 de la sección"):
        # Initial setup of the window
        super().__init__(width, height, title, fullscreen=True)
        self.set_exclusive_mouse(True)

        # Time in the scene
        self.total_time = 0.0

        # Setup of the pipeline (texture models)
        self.pipeline = sh.SimpleTextureModelViewProjectionShaderProgram()

        # Ship model and texture
        self.ex_shape = createGPUShape(self.pipeline, read_OBJ2(ASSETS["ship_obj"]))
        self.tex_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
        self.current_tex = ASSETS["ship_tex"]
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

        self.projection = ORTHO

    # Follow the ship
    def update(self, coords):
        self.eye[0] = self.x+coords[0]
        self.eye[1] = self.y+coords[1]
        # If traverses across the floor to accomplish the ship being always on camera
        if coords[2]>0: self.eye[2] = self.z+coords[2]
        else: self.eye[2] = -self.z+coords[2]
        self.at[0] = coords[0]
        self.at[1] = coords[1]
        self.at[2] = coords[2]

# Movement of the ship #! s
class Movement:
    def __init__(self, eye=np.array([0.0, 0.0, 1.0]), rotation_y=0, rotation_z=0) -> None:
        # Initial setup
        self.eye = eye

        # Rotations
        self.rotation_y = rotation_y
        self.rotation_z = rotation_z

        # Local x axis direction
        self.x_direction = 0

        # Angles
        self.y_angle = 0 # theta
        self.z_angle = 0 # phi

    # Move the ship
    def update(self):
        # Update facing angle of the ship
        self.rotation_y += self.y_angle*0.1
        self.rotation_z += self.z_angle*0.1

        # Move in the local x axis (and hover a little bit)
        self.eye[0] += (self.x_direction*np.cos(self.rotation_y)+np.sin(self.rotation_y)*np.sin(2*controller.total_time)*0.07)*np.cos(self.rotation_z)*0.15
        self.eye[1] += (self.x_direction*np.cos(self.rotation_y)+np.sin(self.rotation_y)*np.sin(2*controller.total_time)*0.07)*np.sin(self.rotation_z)*0.15
        self.eye[2] += (self.x_direction*np.sin(self.rotation_y)+np.cos(self.rotation_y)*np.sin(2*controller.total_time)*-0.07)*-0.15

        # Stop rotation with the mouse
        movement.y_angle = 0

# Setup of the window
camera = Camera()
movement = Movement()
controller = Controller(width=screen_width, height=screen_height)

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

# Controls | W/S: move forward / backward | A/D: turn left/right | move mouse up/down: turn up/down | LeftShift: turbo
# What happens when the user presses these keys
@controller.event
def on_key_press(symbol, modifiers):
    global forward
    if symbol == pyglet.window.key.A: movement.z_angle += 1
    if symbol == pyglet.window.key.D: movement.z_angle -= 1
    if symbol == pyglet.window.key.W:
        forward = True
        movement.x_direction += 1
    if symbol == pyglet.window.key.S: movement.x_direction -= 1
    if modifiers == 17 and forward and movement.x_direction < 2:
        movement.x_direction += 1
    # Close the window
    if symbol == pyglet.window.key.ESCAPE: controller.close()

# What happens when the user releases these keys
@controller.event
def on_key_release(symbol, modifiers):
    global forward
    if modifiers == 16 and movement.x_direction > 1: movement.x_direction -= 1
    if symbol == pyglet.window.key.A: movement.z_angle -= 1
    if symbol == pyglet.window.key.D: movement.z_angle += 1
    if symbol == pyglet.window.key.W and movement.x_direction > 1:
        movement.x_direction -= 2
        forward = False
    if symbol == pyglet.window.key.W and movement.x_direction == 1:
        movement.x_direction -= 1
        forward = False
    if symbol == pyglet.window.key.S and movement.x_direction < -1: movement.x_direction += 2
    if symbol == pyglet.window.key.S and movement.x_direction == -1: movement.x_direction += 1

@controller.event
def on_mouse_motion(x, y, dx, dy):
    if dy>0: movement.y_angle = -1
    if dy<0: movement.y_angle = 1

# What draws at every frame
@controller.event
def on_draw():
    # Clear window every frame
    controller.clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Ship movement
    movement.update()
    # print(movement.y_angle)
    ship_coords = sg.findPosition(ship, "shipRotation")
    ship_rot = [tr.rotationZ(movement.rotation_z), tr.rotationY(movement.rotation_y)] #! rotacion del personaje
    ship_move = [tr.translate(movement.eye[0], movement.eye[1], movement.eye[2])] #! movimiento del personaje

    # Camera tracking of the ship
    camera.update(ship_coords)

    # Projection and view
    view = tr.lookAt(camera.eye, camera.at, camera.up)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    shipShip = sg.findNode(ship, "shipRotation")
    shipShip.transform = tr.matmul(ship_rot)
    ship.transform = tr.matmul(ship_move)

    # Drawing of the scene graph
    platform.transform = np.matmul(tr.scale(20, 20, 0.00003), tr.translate(0, 0, -1))
    sg.drawSceneGraphNode(platform, controller.pipeline, "model")
    sg.drawSceneGraphNode(ship, controller.pipeline, "model")

# Set a time in controller
def update(dt, controller):
    controller.total_time += dt

# Start the scene
if __name__ == '__main__':
    pyglet.clock.schedule(update, controller)
    pyglet.app.run()
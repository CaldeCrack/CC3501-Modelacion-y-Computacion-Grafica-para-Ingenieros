# coding=utf-8
# Useful imports
import sys
import os
import pyglet
import numpy as np
import libs.shaders as sh
import libs.transformations as tr
import libs.scene_graph as sg
import libs.shapes as shp

from libs.gpu_shape import createGPUShape
from libs.obj_handler import read_OBJ2
from libs.assets_path import getAssetPath
from OpenGL.GL import *

"""
Controles:
    W/S: move forward/backward
    A/D: turn left/right
    move mouse up/down: turn up/down
    hold shift: turbo
"""

# Initial data
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = {
    "ship_obj": getAssetPath("ship.obj"), "ship_tex": getAssetPath("ship.png"), # models and textures by me
    "ring_obj": getAssetPath("ring.obj"), "ring_tex": getAssetPath("ring.png"), # ---
    "coin_obj": getAssetPath("coin.obj"), # ---
    "cube_obj": getAssetPath("cube.obj"), "cube_tex": getAssetPath("dirt_1.png"), # texture by Screaming Brain Studios
    "among_us_obj": getAssetPath("among_us.obj"), "among_us_tex": getAssetPath("among_us.png"), # model and texture by Vilitay
    "build1_obj": getAssetPath("build1.obj"), "build1_tex": getAssetPath("build1.png"), # models and textures by Mykhailo Ohorodnichuk
    "build2_obj": getAssetPath("build2.obj"), "build2_tex": getAssetPath("build2.png"), # ---
    "icon": getAssetPath("icon.png"), # icon by Freepik
}

# Aspect ratio and projection
display = pyglet.canvas.Display()
screen = display.get_default_screen()
screen_height = screen.height
screen_width = screen.width
ORTHO = tr.ortho(-10*screen_width/screen_height, 10*screen_width/screen_height, -10, 10, 0.1, 100)
TEX = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]

# Controller of the pyglet window
class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"La mejor tarea 2 de la sección"):
        # Initial setup of the window
        super().__init__(width, height, title, fullscreen=True)
        self.set_exclusive_mouse(True)
        self.set_icon(pyglet.image.load(ASSETS["icon"]))

        # Time in the scene
        self.total_time = 0.0

# Scene graph manager
class Scene:
    def __init__(self) -> None:
        # Initial setup of the scene
        self.pipeline = sh.SimpleTextureModelViewProjectionShaderProgram()
        self.root = sg.SceneGraphNode("root")
        tex_params = TEX

        # --- Squad ---
        ship_obj = createGPUShape(self.pipeline, read_OBJ2(ASSETS["ship_obj"]))
        ship_obj.texture = sh.textureSimpleSetup(ASSETS["ship_tex"], *tex_params)
        self.squad = sg.SceneGraphNode("squad")
        self.root.childs += [self.squad]

        # Ships
        self.shipRotation = sg.SceneGraphNode("shipRotation") # Main ship
        self.shipRotation.childs += [ship_obj]
        self.shipRotation2 = sg.SceneGraphNode("shipRotation2") # Side ships
        self.shipRotation2.childs += [ship_obj]
        self.shipRotation3 = sg.SceneGraphNode("shipRotation3")
        self.shipRotation3.childs += [ship_obj]
        self.squad.childs += [self.shipRotation, self.shipRotation2, self.shipRotation3]

        # --- Scenery ---
        # Floor
        self.scenario = sg.SceneGraphNode("scenario")
        cube = createGPUShape(self.pipeline, shp.createTextureQuad(*[50, 50]), "cube")
        cube.texture = sh.textureSimpleSetup(ASSETS["cube_tex"], *tex_params)
        self.floor = sg.SceneGraphNode("floor")
        self.floor.childs += [cube]
        self.scenario.childs += [self.floor]
        self.floor.transform = tr.scale(200, 200, 1)
        self.root.childs += [self.scenario]

        # Buildings
        build1 = sg.SceneGraphNode("build1") # First building
        build1_transform = [tr.translate(10, 12, 0), tr.uniformScale(1.5), tr.rotationX(np.pi/2)]
        build1.transform = tr.matmul(build1_transform)
        build_model = createGPUShape(self.pipeline, read_OBJ2(ASSETS["build1_obj"]))
        build_model.texture = sh.textureSimpleSetup(ASSETS["build1_tex"], *tex_params)
        build1.childs += [build_model]
        self.scenario.childs += [build1]
        build2 = sg.SceneGraphNode("build2") # Second building
        build2_transform = [tr.translate(-7, -2, 0), tr.uniformScale(1.4), tr.rotationZ(np.pi/2), tr.rotationX(np.pi/2)]
        build2.transform = tr.matmul(build2_transform)
        build_model2 = createGPUShape(self.pipeline, read_OBJ2(ASSETS["build2_obj"]))
        build_model2.texture = sh.textureSimpleSetup(ASSETS["build2_tex"], *tex_params)
        build2.childs += [build_model2]
        self.scenario.childs += [build2]

        # Ring
        ring = sg.SceneGraphNode("ring")
        ring_model = createGPUShape(self.pipeline, read_OBJ2(ASSETS["ring_obj"]))
        ring_model.texture = sh.textureSimpleSetup(ASSETS["ring_tex"], *tex_params)
        ring.childs += [ring_model]
        self.scenario.childs += [ring]

        # Coin
        coin = sg.SceneGraphNode("coin")
        coin_model = createGPUShape(self.pipeline, read_OBJ2(ASSETS["coin_obj"]))
        coin_model.texture = sh.textureSimpleSetup(ASSETS["ring_tex"], *tex_params)
        coin.childs += [coin_model]
        self.scenario.childs += [coin]

        # Among Us
        among_us = sg.SceneGraphNode("among_us")
        among_us_transform = [tr.translate(9, -1, 1.5), tr.uniformScale(2.0), tr.rotationZ(np.pi), tr.rotationX(np.pi/2)]
        among_us.transform = tr.matmul(among_us_transform)
        among_us_model = createGPUShape(self.pipeline, read_OBJ2(ASSETS["among_us_obj"]))
        among_us_model.texture = sh.textureSimpleSetup(ASSETS["among_us_tex"], *tex_params)
        among_us.childs += [among_us_model]
        self.scenario.childs += [among_us]

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
        self.eye[2] = self.z+coords[2]

        self.at[0] = coords[0]
        self.at[1] = coords[1]
        self.at[2] = coords[2]

# Movement of the ships
class Movement:
    def __init__(self, eye=np.array([0.0, 0.0, 1.0]), rotation_y=0, rotation_z=0) -> None:
        # Initial setup
        self.eye = eye
        self.speed = 0.15

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

        # Move in the local x axis (and hover a little bit) (and set the limits of the map)
        if np.abs(self.eye[0]) < 50: self.eye[0] += (self.x_direction*np.cos(self.rotation_y)+np.sin(self.rotation_y)*np.sin(2*controller.total_time)*0.01/self.speed)*np.cos(self.rotation_z)*self.speed
        elif self.eye[0] >= 50: self.eye[0] -= 0.01
        else: self.eye[0] += 0.01
        if np.abs(self.eye[1]) < 50: self.eye[1] += (self.x_direction*np.cos(self.rotation_y)+np.sin(self.rotation_y)*np.sin(2*controller.total_time)*0.01/self.speed)*np.sin(self.rotation_z)*self.speed
        elif self.eye[1] >= 50: self.eye[1] -= 0.01
        else: self.eye[1] += 0.01
        if self.eye[2] < 20 and self.eye[2] > 0.3: self.eye[2] += (self.x_direction*np.sin(self.rotation_y)*-1+np.cos(self.rotation_y)*np.sin(2*controller.total_time)*0.01/self.speed)*self.speed
        elif self.eye[2] >= 20: self.eye[2] -= 0.01
        elif self.eye[2] <= 0.3: self.eye[2] += 0.01

        # Stop rotation with the mouse
        movement.y_angle = 0

# Initial setup
controller = Controller(width=screen_width, height=screen_height)
scene = Scene()
camera = Camera()
movement = Movement()

# Camera setup
glClearColor(0.05, 0.05, 0.1, 1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(scene.pipeline.shaderProgram)

# What happens when the user presses these keys
@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.A: movement.z_angle += 1
    if symbol == pyglet.window.key.D: movement.z_angle -= 1
    if symbol == pyglet.window.key.W: movement.x_direction += 1
    if symbol == pyglet.window.key.S: movement.x_direction -= 1
    if modifiers == pyglet.window.key.MOD_SHIFT: movement.speed = 0.3
    # Close the window
    if symbol == pyglet.window.key.ESCAPE: controller.close()

# What happens when the user releases these keys
@controller.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.A: movement.z_angle -= 1
    if symbol == pyglet.window.key.D: movement.z_angle += 1
    if symbol == pyglet.window.key.W: movement.x_direction -= 1
    if symbol == pyglet.window.key.S: movement.x_direction += 1
    if modifiers == pyglet.window.key.MOD_SHIFT-1: movement.speed = 0.15 # for some reason is a different value on release (at least in my pc)

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

    # Ships movement
    movement.update()
    ship_coords = sg.findPosition(scene.squad, "shipRotation")
    ship_rot = [tr.rotationZ(movement.rotation_z), tr.rotationY(movement.rotation_y)]
    ship_move = [tr.translate(movement.eye[0], movement.eye[1], movement.eye[2])]
    scene.shipRotation.transform = tr.matmul(ship_rot)
    scene.shipRotation2.transform = tr.matmul([tr.translate(-2.0, -2.0, 0.0)]+ship_rot)
    scene.shipRotation3.transform = tr.matmul([tr.translate(-2.0, 2.0, 0.0)]+ship_rot)
    scene.squad.transform = tr.matmul(ship_move)

    # Ring movement
    ring = sg.findNode(scene.root, "ring")
    ring_transform = [tr.translate(5, -4, 5+np.sin(controller.total_time)), tr.uniformScale(2), tr.rotationZ(controller.total_time*0.3)]
    ring.transform = tr.matmul(ring_transform)

    # Coin movement
    coin = sg.findNode(scene.root, "coin")
    coin_transform = [tr.translate(-2, 10, 3+np.sin(controller.total_time)*0.5), tr.uniformScale(0.7), tr.rotationZ(controller.total_time)]
    coin.transform = tr.matmul(coin_transform)

    # Camera tracking of the ship
    camera.update(ship_coords)

    #! Illumination or something
    # glEnable(GL_LIGHTING)

    # Projection and view
    view = tr.lookAt(camera.eye, camera.at, camera.up)
    glUniformMatrix4fv(glGetUniformLocation(scene.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(scene.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    # Drawing of the scene graph
    sg.drawSceneGraphNode(scene.root, scene.pipeline, "model")

# Set a time in controller
def update(dt, controller):
    controller.total_time += dt

# Start the scene
if __name__ == '__main__':
    pyglet.clock.schedule(update, controller)
    pyglet.app.run()
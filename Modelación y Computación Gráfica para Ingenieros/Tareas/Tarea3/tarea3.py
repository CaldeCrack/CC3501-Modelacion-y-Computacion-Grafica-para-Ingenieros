# coding=utf-8
import sys, os, pyglet
import numpy as np
import libs.transformations as tr
import libs.scene_graph as sg
import libs.shapes as shp
import libs.shaders as sh
import libs.lighting_shaders as ls

from libs.gpu_shape import createGPUShape
from libs.obj_handler import read_OBJ2
from libs.assets_path import getAssetPath
from OpenGL.GL import *

""" Controles:
    W/S: move forward/backward
    A/D: turn left/right
    move mouse up/down: turn up/down
    hold shift: turbo
"""

# Initial data
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
N=100
ASSETS = {
    "ship_obj": getAssetPath("ship.obj"), "ship_tex": getAssetPath("ship.png"), # models and textures by me
    "ring_obj": getAssetPath("ring.obj"), "ring_tex": getAssetPath("ring.png"), # ---
    "coin_obj": getAssetPath("coin.obj"), "black_tex": getAssetPath("black.png"), # ---
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
PROJECTIONS = [
    tr.ortho(-10*screen_width/screen_height, 10*screen_width/screen_height, -10, 10, 0.1, 100),  # ORTOGRAPHIC_PROJECTION
    tr.perspective(100, float(screen_width)/float(screen_height), 0.1, 100)  # PERSPECTIVE_PROJECTION
]
TEX = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]

# Curve functions
def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

# Hermite curve
def hermiteMatrix(P1, P2, T1, T2):
    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, T1, T2), axis=1)
    # Hermite base matrix is a constant
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])
    return np.matmul(G, Mh)

# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
    return curve

# Set lightning shader
def setLightShader(shader):
    glUniform3f(glGetUniformLocation(shader.shaderProgram, "La"), 0.8, 0.8, 0.8)
    glUniform3f(glGetUniformLocation(shader.shaderProgram, "Ld"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(shader.shaderProgram, "Ls"), 1, 1, 1)
    glUniform3f(glGetUniformLocation(shader.shaderProgram, "Ka"), 1, 1, 1)
    glUniform3f(glGetUniformLocation(shader.shaderProgram, "Kd"), 1, 1, 1)
    glUniform3f(glGetUniformLocation(shader.shaderProgram, "Ks"), 1, 1, 1)
    glUniform3f(glGetUniformLocation(shader.shaderProgram, "lightPosition"), 0, 0, 25)
    glUniform3f(glGetUniformLocation(shader.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
    glUniform1ui(glGetUniformLocation(shader.shaderProgram, "shininess"), 300)
    glUniform1f(glGetUniformLocation(shader.shaderProgram, "constantAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(shader.shaderProgram, "linearAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(shader.shaderProgram, "quadraticAttenuation"), 0.01)

# Controller of the pyglet window
class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"La mejor tarea 2 de la sección"):
        # Initial setup of the window
        super().__init__(width, height, title, fullscreen=True)
        self.set_exclusive_mouse(True)
        self.set_icon(pyglet.image.load(ASSETS["icon"]))
        self.showCurve = False
        self.total_time = 0.0 # Time in the scene
        self.step = 0

# Scene graph manager
class Scene:
    def __init__(self) -> None:
        # Initial setup of the scene
        self.linePipeline = sh.SimpleModelViewProjectionShaderProgram()
        self.pipeline = ls.SimpleTexturePhongShaderProgram()
        self.root = sg.SceneGraphNode("root")
        tex_params = TEX

        # --- Squad ---
        ship_obj = createGPUShape(self.pipeline, read_OBJ2(ASSETS["ship_obj"]))
        ship_obj.texture = sh.textureSimpleSetup(ASSETS["ship_tex"], *tex_params)
        ship_shadow_obj = createGPUShape(self.pipeline, read_OBJ2(ASSETS["ship_obj"]))
        ship_shadow_obj.texture = sh.textureSimpleSetup(ASSETS["black_tex"], *tex_params)
        self.squad = sg.SceneGraphNode("squad")
        self.root.childs += [self.squad]

        # Ships
        self.shipRotation = sg.SceneGraphNode("shipRotation") # Main ship
        self.shipRotation.childs += [ship_obj]
        self.shipRotation2 = sg.SceneGraphNode("shipRotation2") # Side ships
        self.shipRotation2.childs += [ship_obj]
        self.shipRotation3 = sg.SceneGraphNode("shipRotation3")
        self.shipRotation3.childs += [ship_obj]
        # Perspective camera
        self.eye = sg.SceneGraphNode("eye")
        self.at = sg.SceneGraphNode("at")
        self.up = sg.SceneGraphNode("up")
        self.squad.childs += [self.shipRotation, self.shipRotation2, self.shipRotation3, self.eye, self.up, self.at] # Add ships

        # Shadows
        self.ship_shadows = sg.SceneGraphNode("ship_shadows")
        self.shipRotationShadow = sg.SceneGraphNode("shipRotationShadow") # Main ship
        self.shipRotationShadow.childs += [ship_shadow_obj]
        self.shipRotationShadow2 = sg.SceneGraphNode("shipRotationShadow2") # Side ships
        self.shipRotationShadow2.childs += [ship_shadow_obj]
        self.shipRotationShadow3 = sg.SceneGraphNode("shipRotationShadow3")
        self.shipRotationShadow3.childs += [ship_shadow_obj]
        self.ship_shadows.childs += [self.shipRotationShadow, self.shipRotationShadow2, self.shipRotationShadow3] # Add shadows
        self.root.childs += [self.ship_shadows]

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
        ring_shadow_obj = createGPUShape(self.pipeline, read_OBJ2(ASSETS["ring_obj"])) # Ring shadow
        ring_shadow_obj.texture = sh.textureSimpleSetup(ASSETS["black_tex"], *tex_params)
        self.ringShadow = sg.SceneGraphNode("ringShadow")
        self.ringShadow.childs += [ring_shadow_obj]
        self.scenario.childs += [self.ringShadow]

        # Coin
        coin = sg.SceneGraphNode("coin")
        coin_model = createGPUShape(self.pipeline, read_OBJ2(ASSETS["coin_obj"]))
        coin_model.texture = sh.textureSimpleSetup(ASSETS["ring_tex"], *tex_params)
        coin.childs += [coin_model]
        self.scenario.childs += [coin]
        coin_shadow_obj = createGPUShape(self.pipeline, read_OBJ2(ASSETS["coin_obj"])) # Coin shadow
        coin_shadow_obj.texture = sh.textureSimpleSetup(ASSETS["black_tex"], *tex_params)
        self.coinShadow = sg.SceneGraphNode("coinShadow")
        self.coinShadow.childs += [coin_shadow_obj]
        self.scenario.childs += [self.coinShadow]

        # Among Us
        among_us = sg.SceneGraphNode("among_us")
        among_us_transform = [tr.translate(9, -1, 1.6), tr.uniformScale(2.0), tr.rotationZ(np.pi), tr.rotationX(np.pi/2)]
        among_us.transform = tr.matmul(among_us_transform)
        among_us_model = createGPUShape(self.pipeline, read_OBJ2(ASSETS["among_us_obj"]))
        among_us_model.texture = sh.textureSimpleSetup(ASSETS["among_us_tex"], *tex_params)
        among_us.childs += [among_us_model]
        self.scenario.childs += [among_us]
        among_us_shadow_obj = createGPUShape(self.pipeline, read_OBJ2(ASSETS["among_us_obj"])) # Among Us shadow
        among_us_shadow_obj.texture = sh.textureSimpleSetup(ASSETS["black_tex"], *tex_params)
        self.amongUsShadow = sg.SceneGraphNode("amongUsShadow")
        self.amongUsShadow.childs += [among_us_shadow_obj]
        self.scenario.childs += [self.amongUsShadow]

# Camera which controls the projection and view
class Camera:
    def __init__(self, at=np.array([0.0, 0.0, 0.0]), eye=np.array([5.0, 5.0, 5.0]), up=np.array([-0.577, -0.577, 0.577])) -> None:
        # View parameters
        self.at = at
        self.eye = eye
        self.up = up

        # Cartesian coordinates
        self.x = np.square(self.eye[0])
        self.y = np.square(self.eye[1])
        self.z = np.square(self.eye[2])

        # Projections
        self.available_projections = PROJECTIONS
        self.proj = 0
        self.projection = self.available_projections[0]

    # Set orthographic or perspective projection
    def set_projection(self):
        self.proj = (self.proj+1)%2
        self.projection = self.available_projections[self.proj]

    # Follow the ship
    def update(self, eye, at, up, ship):
        if(self.proj==0): # orthographic projection
            self.up = np.array([-0.577, -0.577, 0.577])
            self.eye[0] = self.x+ship[0][0]
            self.eye[1] = self.y+ship[1][0]
            self.eye[2] = self.z+ship[2][0]
            self.at[0] = ship[0][0]
            self.at[1] = ship[1][0]
            self.at[2] = ship[2][0]
        else: # perspective projection
            self.eye[0] = eye[0][0]
            self.eye[1] = eye[1][0]
            self.eye[2] = eye[2][0]
            self.at = [at[0][0], at[1][0], at[2][0]]
            self.up = [0, 0, up[2][0]-eye[2][0]]

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

        # Curve
        self.curving = False

    # Move the ship
    def update(self):
        # Update facing angle of the ship
        self.rotation_y += self.y_angle*0.1
        self.rotation_z += self.z_angle*0.05

        # Move in the local x axis, hover a little bit and set the limits of the map
        if np.abs(self.eye[0]) < 50: self.eye[0] += (self.x_direction*np.cos(self.rotation_y)+np.sin(self.rotation_y)*np.sin(2*controller.total_time)*0.01/self.speed)*np.cos(self.rotation_z)*self.speed
        elif self.eye[0] >= 50: self.eye[0] -= 0.01
        else: self.eye[0] += 0.01
        if np.abs(self.eye[1]) < 50: self.eye[1] += (self.x_direction*np.cos(self.rotation_y)+np.sin(self.rotation_y)*np.sin(2*controller.total_time)*0.01/self.speed)*np.sin(self.rotation_z)*self.speed
        elif self.eye[1] >= 50: self.eye[1] -= 0.01
        else: self.eye[1] += 0.01
        if self.eye[2] < 20 and self.eye[2] > 0.3: self.eye[2] += (self.x_direction*np.sin(self.rotation_y)*-1+np.cos(self.rotation_y)*np.sin(2*controller.total_time)*0.01/self.speed)*self.speed
        elif self.eye[2] >= 20: self.eye[2] -= 0.01
        else: self.eye[2] += 0.01

        # Stop rotation with the mouse
        movement.y_angle = 0

# Initial setup
controller = Controller(width=screen_width, height=screen_height)
scene = Scene()
camera = Camera()
movement = Movement()
control_points = [[], []] # Coordenates, angles
prevHermiteCurve = None
hermiteCurve = None

# Camera setup
glClearColor(0.05, 0.05, 0.1, 1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(scene.pipeline.shaderProgram)

# What happens when the user presses these keys
@controller.event
def on_key_press(symbol, modifiers):
    global prevHermiteCurve
    global hermiteCurve
    global n
    # reproduction
    if symbol == pyglet.window.key._1:
        controller.step = 0
        if len(control_points[0]) > 0: movement.curving = not movement.curving
    # everything else
    if symbol == pyglet.window.key.C: camera.set_projection()
    if symbol == pyglet.window.key.V: controller.showCurve = not controller.showCurve
    if not movement.curving:
        # checkpoints
        if symbol == pyglet.window.key.R:
            point = np.array([[movement.eye[0], movement.eye[1], movement.eye[2]]]).T
            rot_y, rot_z = movement.rotation_y, movement.rotation_z
            angle = np.array([[np.cos(rot_y)*np.cos(rot_z), np.cos(rot_y)*np.sin(rot_z), -np.sin(rot_y)]]).T
            control_points[0].append(point)
            control_points[1].append(angle)
            lenC = len(control_points[0])
            if lenC > 2:
                # re create prev curve
                vector = point-control_points[0][-3]
                control_points[1][-2] = vector
                GMh = hermiteMatrix(control_points[0][-3], control_points[0][-2], control_points[1][-3], control_points[1][-2])
                # save it
                if lenC > 3: prevHermiteCurve = np.concatenate((prevHermiteCurve, evalCurve(GMh, N)), axis=0)
                else: prevHermiteCurve = evalCurve(GMh, N)
                # create the end of the curve
                GMh = hermiteMatrix(control_points[0][-2], control_points[0][-1], control_points[1][-2], control_points[1][-1])
                hermiteCurve = np.concatenate((prevHermiteCurve, evalCurve(GMh, N)), axis=0)
            elif lenC == 2:
                GMh = hermiteMatrix(control_points[0][-2], control_points[0][-1], control_points[1][-2], control_points[1][-1])
                hermiteCurve = evalCurve(GMh, N)
        if symbol == pyglet.window.key.A: movement.z_angle += 1
        if symbol == pyglet.window.key.D: movement.z_angle -= 1
        if symbol == pyglet.window.key.W: movement.x_direction += 1
        if symbol == pyglet.window.key.S: movement.x_direction -= 1
        # the value of modifier when I press shift sometimes is 17 and other times is 1 (16 and 0 on release) and idk why
        # pyglet.window.key.MOD_SHIFT doesn't always get the right value
        if modifiers == 17: movement.speed = 0.3
    # Close the window
    if symbol == pyglet.window.key.ESCAPE: controller.close()

# What happens when the user releases these keys
@controller.event
def on_key_release(symbol, modifiers):
    if not movement.curving:
        if symbol == pyglet.window.key.A: movement.z_angle -= 1
        if symbol == pyglet.window.key.D: movement.z_angle += 1
        if symbol == pyglet.window.key.W: movement.x_direction -= 1
        if symbol == pyglet.window.key.S: movement.x_direction += 1
        if modifiers == 17-1: movement.speed = 0.15

# What happens when the user moves the mouse
@controller.event
def on_mouse_motion(x, y, dx, dy):
    if dy>0: movement.y_angle = -0.6
    if dy<0: movement.y_angle = 0.6

# What draws at every frame
@controller.event
def on_draw():
    # Step update
    if controller.step >= N*(len(control_points[0])-1)-1: controller.step = 0
    controller.step += 1

    # Things
    controller.clear()
    glUseProgram(scene.pipeline.shaderProgram)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # mvpPipeline = scene.linePipeline

    # Ships movement
    movement.update()
    if movement.curving: # ship through the curve
        ship_move = [tr.translate(hermiteCurve[controller.step, 0], hermiteCurve[controller.step, 1], hermiteCurve[controller.step, 2])]
        ship_rot = [tr.rotationZ(0), tr.rotationY(0)]
    else: # ship free movement
        ship_move = [tr.translate(movement.eye[0], movement.eye[1], movement.eye[2])]
        ship_rot = [tr.rotationZ(movement.rotation_z), tr.rotationY(movement.rotation_y)]
    # ship_move = [tr.translate(movement.eye[0], movement.eye[1], movement.eye[2])]
    scene.shipRotation2.transform = tr.matmul([tr.translate(-2, -1, 0.0)])
    scene.shipRotation3.transform = tr.matmul([tr.translate(-2, 1, 0.0)])

    # Camera in perspective
    scene.eye.transform = tr.matmul([tr.translate(-4.0, 0, 2.0)])
    scene.at.transform = tr.matmul([tr.translate(0.0, 0, 2.0)])
    scene.up.transform = tr.matmul([tr.translate(-4.0, 0, 3.0)])

    # Shadows
    ship1, ship2, ship3 = sg.findPosition(scene.squad, "shipRotation"), sg.findPosition(scene.squad, "shipRotation2"), sg.findPosition(scene.squad, "shipRotation3")
    scene.shipRotationShadow.transform = tr.matmul([tr.translate(ship1[0][0], ship1[1][0], 0.1)]+[tr.scale(1, 1, 0.01)]+ship_rot)
    scene.shipRotationShadow2.transform = tr.matmul([tr.translate(ship2[0][0], ship2[1][0], 0.1)]+[tr.scale(1, 1, 0.01)]+ship_rot)
    scene.shipRotationShadow3.transform = tr.matmul([tr.translate(ship3[0][0], ship3[1][0], 0.1)]+[tr.scale(1, 1, 0.01)]+ship_rot)
    scene.squad.transform = tr.matmul(ship_move+ship_rot) # Start movement of the ships

    # Perspective position and up
    eye, up, at = sg.findPosition(scene.squad, "eye"), sg.findPosition(scene.squad, "up"), sg.findPosition(scene.squad, "at")

    # Ring movement
    ring = sg.findNode(scene.root, "ring")
    ring.transform = tr.matmul([tr.translate(5, -4, 5+np.sin(controller.total_time)), tr.uniformScale(2), tr.rotationZ(controller.total_time*0.3)])
    scene.ringShadow.transform = tr.matmul([tr.translate(5, -4, 0.1), tr.scale(2, 2, 0.01), tr.rotationZ(controller.total_time*0.3)]) # Ring shadow

    # Coin movement
    coin = sg.findNode(scene.root, "coin")
    coin.transform = tr.matmul([tr.translate(-2, 10, 3+np.sin(controller.total_time)*0.5), tr.uniformScale(0.7), tr.rotationZ(controller.total_time)])
    scene.coinShadow.transform = tr.matmul([tr.translate(-2, 10, 0.1), tr.scale(0.7, 0.7, 0.01), tr.rotationZ(controller.total_time*0.3)]) # Coin shadow

    # Among Us shadow
    scene.amongUsShadow.transform = tr.matmul([tr.translate(9, -1, 0.1), tr.scale(2, 2, 0.01), tr.rotationZ(np.pi), tr.rotationX(np.pi/2)])

    # Lighting shader
    setLightShader(scene.pipeline)

    # Camera tracking of the ship, projection and view
    camera.update(eye, at, up, ship1)
    view = tr.lookAt(camera.eye, camera.at, camera.up)
    glUniformMatrix4fv(glGetUniformLocation(scene.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(scene.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    sg.drawSceneGraphNode(scene.root, scene.pipeline, "model")

# Set a time in controller
def update(dt, controller):
    controller.total_time += dt

# Start the scene
if __name__ == '__main__':
    pyglet.clock.schedule(update, controller)
    pyglet.app.run()
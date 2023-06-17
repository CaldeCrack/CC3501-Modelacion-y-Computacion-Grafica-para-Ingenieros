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
from pyglet.graphics.shader import Shader, ShaderProgram
from itertools import chain
from pathlib import Path
from OpenGL.GL import *

""" Controls:
    W/S: move forward/backward
    A/D: turn left/right
    move mouse up/down: turn up/down
    hold shift: turbo
    C: change perspective
    R: create control point
    V: view curve
    B: restart curves
    1: reproduce path
"""

# Initial data
N=75
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        self.pipeline = ls.SimpleTexturePhongShaderProgram()
        self.root = sg.SceneGraphNode("root")
        self.tex_params = TEX

        # --- Squad ---
        ship_obj = createGPUShape(self.pipeline, read_OBJ2(ASSETS["ship_obj"]))
        ship_obj.texture = sh.textureSimpleSetup(ASSETS["ship_tex"], *self.tex_params)
        ship_shadow_obj = createGPUShape(self.pipeline, read_OBJ2(ASSETS["ship_obj"]))
        ship_shadow_obj.texture = sh.textureSimpleSetup(ASSETS["black_tex"], *self.tex_params)
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
        cube.texture = sh.textureSimpleSetup(ASSETS["cube_tex"], *self.tex_params)
        self.floor = sg.SceneGraphNode("floor")
        self.floor.childs += [cube]
        self.scenario.childs += [self.floor]
        self.floor.transform = tr.scale(200, 200, 1)
        self.root.childs += [self.scenario]

    # Add scenery to the scene
    def addScenery(self, obj, tex, pos, rotX, rotZ, scale):
        # Model
        node = sg.SceneGraphNode(obj)
        model = createGPUShape(self.pipeline, read_OBJ2(ASSETS[obj]))
        model.texture = sh.textureSimpleSetup(ASSETS[tex], *self.tex_params)
        node.transform = tr.matmul([tr.translate(*pos), tr.uniformScale(scale), tr.rotationZ(rotZ), tr.rotationX(rotX)])
        node.childs += [model]
        self.scenario.childs += [node]
        # Shadow
        shadow = sg.SceneGraphNode(obj+"_shadow")
        shadow_model = createGPUShape(self.pipeline, read_OBJ2(ASSETS[obj]))
        shadow_model.texture = sh.textureSimpleSetup(ASSETS["black_tex"], *self.tex_params)
        shadow.transform = tr.matmul([tr.translate(pos[0], pos[1], 0), tr.scale(scale, scale, 0.01), tr.rotationZ(rotZ), tr.rotationX(rotX)])
        shadow.childs += [shadow_model]
        self.scenario.childs += [shadow]

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

    def curveUpdate(self):
        pass

# Initial setup
controller = Controller(width=screen_width, height=screen_height)
scene = Scene()
camera = Camera()
movement = Movement()
control_points = [[], []] # Coordenates, angles
prevHermiteCurve = None
hermiteCurve = None
# smoothAngles = []

# Scenario
scene.addScenery("build1_obj", "build1_tex", [10, 12, 0], np.pi/2, 0, 1.5)
scene.addScenery("build2_obj", "build2_tex", [-7, -2, 0], np.pi/2, np.pi/2, 1.4)
scene.addScenery("ring_obj", "ring_tex", [0, 0, 0], 0, 0, 1)
scene.addScenery("coin_obj", "ring_tex", [0, 0, 0], 0, 0, 1)
scene.addScenery("among_us_obj", "among_us_tex", [9, -1, 1.6], np.pi/2, np.pi, 2)

# Camera setup
glClearColor(0.05, 0.05, 0.1, 1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(scene.pipeline.shaderProgram)

# What happens when the user presses these keys
@controller.event
def on_key_press(symbol, modifiers):
    # global variables
    global control_points
    global prevHermiteCurve
    global hermiteCurve
    global n

    # everything else
    if symbol == pyglet.window.key._1:
        controller.step = 0
        if len(control_points[0]) > 0: movement.curving = not movement.curving
    if symbol == pyglet.window.key.C: camera.set_projection()
    if symbol == pyglet.window.key.V: controller.showCurve = not controller.showCurve
    if not movement.curving:
        if symbol == pyglet.window.key.B:
            control_points = [[], []]
            prevHermiteCurve = None
            hermiteCurve = None
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
            elif lenC == 2: # Create curve when just 2 control points
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
    if not movement.curving:
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

    # Ships movement
    if movement.curving: # curve movement
        movement.curveUpdate()
        ship_move = [tr.translate(hermiteCurve[controller.step, 0], hermiteCurve[controller.step, 1], hermiteCurve[controller.step, 2])]
    else: # free movement
        movement.update()
        ship_move = [tr.translate(movement.eye[0], movement.eye[1], movement.eye[2])]
    ship_rot = [tr.rotationZ(movement.rotation_z), tr.rotationY(movement.rotation_y)]
    scene.shipRotation2.transform = tr.matmul([tr.translate(-2, -1, 0)])
    scene.shipRotation3.transform = tr.matmul([tr.translate(-2, 1, 0)])
    ship1, ship2, ship3 = sg.findPosition(scene.squad, "shipRotation"), sg.findPosition(scene.squad, "shipRotation2"), sg.findPosition(scene.squad, "shipRotation3")

    # Camera in perspective
    scene.eye.transform = tr.matmul([tr.translate(-4.0, 0, 2.0)])
    scene.at.transform = tr.matmul([tr.translate(0.0, 0, 2.0)])
    scene.up.transform = tr.matmul([tr.translate(-4.0, 0, 3.0)])
    eye, up, at = sg.findPosition(scene.squad, "eye"), sg.findPosition(scene.squad, "up"), sg.findPosition(scene.squad, "at")

    # Shadows
    scene.shipRotationShadow.transform = tr.matmul([tr.translate(ship1[0][0], ship1[1][0], 0.01)]+[tr.scale(1, 1, 0.01)]+ship_rot)
    scene.shipRotationShadow2.transform = tr.matmul([tr.translate(ship2[0][0], ship2[1][0], 0.01)]+[tr.scale(1, 1, 0.01)]+ship_rot)
    scene.shipRotationShadow3.transform = tr.matmul([tr.translate(ship3[0][0], ship3[1][0], 0.01)]+[tr.scale(1, 1, 0.01)]+ship_rot)
    scene.squad.transform = tr.matmul(ship_move+ship_rot) # Start movement of the ships

    # Ring and coin movement
    ring = sg.findNode(scene.root, "ring_obj")
    ringShadow = sg.findNode(scene.root, "ring_obj_shadow")
    ring.transform = tr.matmul([tr.translate(5, -4, 5+np.sin(controller.total_time)), tr.uniformScale(2), tr.rotationZ(controller.total_time*0.2)])
    ringShadow.transform = tr.matmul([tr.translate(5, -4, 0.1), tr.scale(2, 2, 0.01), tr.rotationZ(controller.total_time*0.2)])
    coin = sg.findNode(scene.root, "coin_obj")
    coinShadow = sg.findNode(scene.root, "coin_obj_shadow")
    coin.transform = tr.matmul([tr.translate(-2, 10, 3+np.sin(controller.total_time)*0.5), tr.uniformScale(0.7), tr.rotationZ(controller.total_time)])
    coinShadow.transform = tr.matmul([tr.translate(-2, 10, 0.1), tr.scale(0.7, 0.7, 0.01), tr.rotationZ(controller.total_time)])

    # Camera tracking of the ship, projection and view
    setLightShader(scene.pipeline)
    camera.update(eye, at, up, ship1)
    view = tr.lookAt(camera.eye, camera.at, camera.up)
    glUniformMatrix4fv(glGetUniformLocation(scene.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(scene.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    # Draw curve
    with open(Path(os.path.dirname(__file__)) / "shaders\point_vertex_program.glsl") as f: vertex_program = f.read()
    with open(Path(os.path.dirname(__file__)) / "shaders\point_fragment_program.glsl") as f: fragment_program = f.read()
    vert_shader = Shader(vertex_program, "vertex")
    frag_shader = Shader(fragment_program, "fragment")
    linePipeline = ShaderProgram(vert_shader, frag_shader)
    if(controller.showCurve and len(control_points[0]) > 1):
        controller.node_data = linePipeline.vertex_list(len(hermiteCurve), pyglet.gl.GL_POINTS, position="f")
        controller.joint_data = linePipeline.vertex_list_indexed(len(hermiteCurve), pyglet.gl.GL_LINES,
            tuple(chain(*(j for j in [range(len(hermiteCurve))]))), position="f",)
        controller.node_data.position[:] = tuple(chain(*((p[0], p[1], p[2]) for p in hermiteCurve)))
        controller.joint_data.position[:] = tuple(chain(*((p[0], p[1], p[2]) for p in hermiteCurve)))
        linePipeline["projection"] = camera.projection.reshape(16, 1, order="F")
        linePipeline["view"] = view.reshape(16, 1, order="F")
        linePipeline.use()
        controller.node_data.draw(pyglet.gl.GL_POINTS)
        controller.joint_data.draw(pyglet.gl.GL_LINES)

    # Light shader
    glUseProgram(scene.pipeline.shaderProgram)
    sg.drawSceneGraphNode(scene.root, scene.pipeline, "model")

# Set a time in controller
def update(dt, controller):
    controller.total_time += dt

# Start the scene
if __name__ == '__main__':
    pyglet.clock.schedule(update, controller)
    pyglet.app.run()
from socket import has_ipv6
import sys
import os
import pyglet
import numpy as np
from pyglet.gl import *

import grafica.shaders as sh
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.scene_graph as sg

from grafica.gpu_shape import createGPUShape
from grafica.obj_handler import read_OBJ2
from grafica.assets_path import getAssetPath
#from pyglet.graphics.shader.Shader import Shader, ShaderProgram
from pathlib import Path
from itertools import chain
#from pyglet.graphics.shader import Shader, ShaderProgram

from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# A class to store the application control

# Se asigna el ancho y alto de la ventana y se crea.
WIDTH, HEIGHT = 1280, 800

with open(Path(os.path.dirname(__file__)) / "grafica/vertex_shader.glsl") as f:
    vertex_program = f.read()

with open(Path(os.path.dirname(__file__)) / "grafica/point_fragment_program.glsl") as f:
    fragment_program = f.read()
vert_shader = pyglet.graphics.shader.Shader(vertex_program, "vertex")
frag_shader = pyglet.graphics.shader.Shader(fragment_program, "fragment")
# Controlador que permite comunicarse con la ventana de pyglet
class Controller(pyglet.window.Window):

    def __init__(self, width, height, title="naves"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.fillPolygon = True
        self.showAxis = True
        self.pipeline = sh.SimpleTextureModelViewProjectionShaderProgram()
        self.pipeline2 =  pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)
        self.repeats = 0
        self.step = 0

 

controller = Controller(width=WIDTH, height=HEIGHT)
# Se asigna el color de fondo de la ventana
glClearColor(0.0, 0.0, 0.0, 1.0)
# Como trabajamos en 3D, necesitamos chequear cuáles objetos están en frente, y cuáles detrás.
glEnable(GL_DEPTH_TEST)

# Se configura el pipeline y se le dice a OpenGL que utilice ese shader
glUseProgram(controller.pipeline.shaderProgram)

# El controlador puede recibir inputs del usuario. Estas funciones define cómo manejarlos.
@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        controller.close()

    else:
        print('Unknown key')

class nave:
    def __init__(self,obj,textura, pipeline):
        self.shape = createGPUShape(pipeline,read_OBJ2(obj))
        self.shape.texture = sh.textureSimpleSetup(textura, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        self.x = 0
        self.y = 0
        self.z = 0
        self.x_direction_avance = 0
        self.y_direction_rot = 0#theta
        self.z_direction_rot = 0#phi

        self.x_speed = 0.12
        self.y_speed = 0.12
        self.z_speed = 0.12

        self.anguloy = 0
        self.anguloz = 0

        self.camino = False
        self.guardarp = False
        self.guardart = False
        self.puntos = []
        self.tangentes = []
        self.orientacionesy = []
        self.orientacionesz = []
        self.anterior = None
        self.graficarcurve = False
        self.haycurva = False
        self.curva = None
        self.pirueta = False
    def update(self):#(r,theta=zdirect,phi=ydirect)
        self.anguloy += self.y_direction_rot
        self.anguloz += self.z_direction_rot

        self.x += np.cos(self.anguloy)*np.cos(self.anguloz)*self.x_direction_avance*self.x_speed
        self.y += np.cos(self.anguloy)*self.x_direction_avance*np.sin(self.anguloz)*self.y_speed
        newZ = self.z + -np.sin(self.anguloy)*self.x_direction_avance*self.z_speed
        if newZ >= 0:
            self.z = newZ
        
class camara:
    def __init__(self, at=np.array([0.0, 0.0, 0.0]), eye=np.array([5.0, 5.0, 5.0]), up=np.array([0.0, 0.0, 1.0])) -> None:
        self.at = at
        self.eye = eye
        self.up = up

        self.x = np.square(self.eye[0])
        self.y = np.square(self.eye[1])
        self.z = np.square(self.eye[2])

        self.projection = "ortho"
        self.projection2 = "perspective"
        self.proactual = "ortho"
        self.infopro = tr.ortho(-8, 8, -8, 8, 0.1, 100)

        self.anguloy =0
        self.anguloz=0
        self.speed = 0.12
        self.avance = 0


    def update(self,coordenadas,anguloz):
        if self.proactual == self.projection:
            self.eye[0] = coordenadas[0]+self.x
            self.eye[1] = coordenadas[1]+self.y
            self.eye[2] = coordenadas[2]+self.z

            self.at[0] = coordenadas[0]
            self.at[1] = coordenadas[1]
            self.at[2] = coordenadas[2]
        else:
            x = float(coordenadas[0])
            y = float(coordenadas[1])
            z = float(coordenadas[2])
            nave_position = np.array([x, y, z, 1])
            camera_transform = tr.matmul([tr.rotationZ(anguloz), tr.translate(-5,0,3), tr.rotationZ(-anguloz)])
            camera_position = np.matmul(camera_transform,nave_position)
            self.eye = camera_position[0:3]

            self.at[0] = coordenadas[0]
            self.at[1] = coordenadas[1]
            self.at[2] = coordenadas[2]
        
obj=getAssetPath("naveultintento.obj")
nave_tex = getAssetPath("Ship_texture.png")
sombra_tex = getAssetPath("sombra_texture.png")
naveshape = nave(obj,nave_tex,controller.pipeline)
navesombra = nave(obj,sombra_tex,controller.pipeline)

obj2 = getAssetPath("plano2.obj")
planotex= getAssetPath("fondo.png")
planoshape = createGPUShape(controller.pipeline, read_OBJ2(obj2))
planoshape.texture=sh.textureSimpleSetup(planotex, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj3 =getAssetPath("pochita3.obj")
pochitatex = getAssetPath("pochita.png")
pochitashape = createGPUShape(controller.pipeline, read_OBJ2(obj3))
pochitashape.texture = sh.textureSimpleSetup(pochitatex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj4 = getAssetPath("anillo.obj")
anillotex = getAssetPath("anillo.png")
anilloshape = createGPUShape(controller.pipeline, read_OBJ2(obj4))
anilloshape.texture = sh.textureSimpleSetup(anillotex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj5 = getAssetPath("astronauta.obj")
astrotex = getAssetPath("astro.png")
astroshape = createGPUShape(controller.pipeline, read_OBJ2(obj5))
astroshape.texture = sh.textureSimpleSetup(astrotex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj6 = getAssetPath("estrella.obj")
startex = getAssetPath("estrella.png")
starshape = createGPUShape(controller.pipeline, read_OBJ2(obj6))
starshape.texture = sh.textureSimpleSetup(startex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj7 =getAssetPath("Oso2.obj")
osotex = getAssetPath("oso.png")
ososhape= createGPUShape(controller.pipeline, read_OBJ2(obj7))
ososhape.texture = sh.textureSimpleSetup(osotex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

def CreateScene(naveShape):

    nave = sg.SceneGraphNode("naveNode")
    nave.transform = tr.matmul([tr.rotationX(np.pi),tr.uniformScale(0.1)])
    nave.childs += [naveShape.shape]
    
    nave2 = sg.SceneGraphNode("nave2Node")
    nave2.transform = tr.matmul([tr.translate(-2,-1,0),tr.rotationX(np.pi),tr.uniformScale(0.1)])
    nave2.childs += [naveShape.shape]

    nave3 = sg.SceneGraphNode("nave3Node")
    nave3.transform =tr.matmul([tr.translate(-2,1,0),tr.rotationX(np.pi),tr.uniformScale(0.1)])
    nave3.childs += [naveShape.shape]

    navesombra1 = sg.SceneGraphNode("navesombra")
    navesombra1.transform = tr.matmul([tr.translate(0,0,-1.9),tr.scale(0.1,0.1,0.0)])
    navesombra1.childs += [navesombra.shape]

    navesombra2 = sg.SceneGraphNode("navesombra2")
    navesombra2.transform = tr.matmul([tr.translate(-2,-1,-1.9),tr.scale(0.1,0.1,0.0)])
    navesombra2.childs += [navesombra.shape]

    navesombra3 = sg.SceneGraphNode("navesombra3")
    navesombra3.transform = tr.matmul([tr.translate(-2,1,-1.9),tr.scale(0.1,0.1,0.0)])
    navesombra3.childs += [navesombra.shape]

    sombrarot = sg.SceneGraphNode("sombrarot")
    sombrarot.childs += [navesombra1,navesombra2,navesombra3]

    sombratrasl = sg.SceneGraphNode("sombratrasl")
    sombratrasl.childs += [sombrarot]

    naverot = sg.SceneGraphNode("naverot")
    naverot.childs += [nave,nave2,nave3]

    navetrasl = sg.SceneGraphNode("navetrasl")
    navetrasl.childs += [naverot]

    anillomov = sg.SceneGraphNode("anillomov")
    anillomov.childs += [anilloshape]

    anillo = sg.SceneGraphNode("anillo")
    anillo.transform = tr.matmul([tr.translate(5,0,1)])
    anillo.childs += [anillomov]

    astronauta = sg.SceneGraphNode("astronauta")
    astronauta.transform = tr.matmul([tr.translate(-4,-7,1),tr.rotationX(np.pi/2),tr.uniformScale(0.5)])
    astronauta.childs += [astroshape]

    astromov = sg.SceneGraphNode("astromov")
    astromov.childs += [astronauta]

    pochitauwu = sg.SceneGraphNode("Pochita")
    pochitauwu.transform = tr.matmul([tr.translate(-5,4,0),tr.uniformScale(2.0),tr.rotationX(np.pi/2),tr.rotationY(np.pi/2)])
    pochitauwu.childs += [pochitashape]

    star = sg.SceneGraphNode("star")
    star.transform = tr.matmul([tr.translate(-3,-3,0),tr.rotationX(np.pi/2),tr.uniformScale(0.5)])
    star.childs += [starshape]

    star2 = sg.SceneGraphNode("star2")
    star2.transform = tr.matmul([tr.translate(-3,3,0),tr.rotationX(np.pi/2),tr.uniformScale(0.5)])
    star2.childs += [starshape]

    plano = sg.SceneGraphNode("plano")
    plano.transform = tr.matmul([tr.translate(0,0,-1),tr.uniformScale(20),tr.rotationX(np.pi/2)])
    plano.childs += [planoshape]

    oso = sg.SceneGraphNode("oso")
    oso.transform = tr.matmul([tr.translate(-5,-4,0),tr.uniformScale(0.3), tr.rotationX(np.pi/2)])
    oso.childs += [ososhape]

    scene = sg.SceneGraphNode("scene")

    scene.childs += [sombratrasl]
    scene.childs += [navetrasl]
    scene.childs += [plano]
    scene.childs += [pochitauwu,anillo,astromov,star,star2,oso]

    return scene

#creamos la escena
escena = CreateScene(naveshape)
camera= camara()

# Esta función se ejecuta aproximadamente 60 veces por segundo, dt es el tiempo entre la última
# ejecución y ahora
def update(dt, window):
    window.total_time += dt

def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

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

@controller.event
def on_key_press(symbol,modifiers):
    if symbol == pyglet.window.key.A:
        naveshape.z_direction_rot = np.pi/30
        navesombra.z_direction_rot = np.pi/30
    if symbol == pyglet.window.key.D:
        naveshape.z_direction_rot = -np.pi/30
        navesombra.z_direction_rot = -np.pi/30
    if symbol == pyglet.window.key.W:
        naveshape.x_direction_avance = 1
        navesombra.x_direction_avance = 1
    if symbol == pyglet.window.key.S:
        naveshape.x_direction_avance = -1
        navesombra.x_direction_avance = 1 
    if symbol == pyglet.window.key.C:
        if camera.proactual == camera.projection:
            camera.proactual = camera.projection2
        else:
            camera.proactual = camera.projection
    if symbol == pyglet.window.key.R:
        naveshape.guardarp = True
    if symbol == pyglet.window.key._1:
        if len(naveshape.tangentes) >= 2:
            naveshape.camino = True
        else:
            print("faltan puntos de control, deben ser 2 mínimo para Hermite")
    if symbol==pyglet.window.key.V:
        if len(naveshape.tangentes) >= 2:
            naveshape.graficarcurve = True
        else:
            print("faltan puntos de control, deben ser 2 mínimo para Hermite")
    if symbol == pyglet.window.key.P:
        naveshape.pirueta = True
    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()

@controller.event
def on_mouse_motion(x,y,dx,dy):
    if dy > 0:
        naveshape.y_direction_rot = -np.pi/30
        navesombra.y_direction_rot = -np.pi/30
    if dy < 0:
        naveshape.y_direction_rot = np.pi/30
        navesombra.y_direction_rot = np.pi/30

@controller.event
def on_key_release(symbol,modifiers):
    if symbol == pyglet.window.key.A:
        naveshape.z_direction_rot = 0
        navesombra.z_direction_rot =0
    if symbol == pyglet.window.key.D:
        naveshape.z_direction_rot = 0
        navesombra.z_direction_rot =0
    if symbol == pyglet.window.key.W:
       naveshape.x_direction_avance = 0
       navesombra.x_direction_avance = 0
    if symbol == pyglet.window.key.S:
       naveshape.x_direction_avance = 0
       navesombra.x_direction_avance = 0
        
# Cada vez que se llama update(), se llama esta función también
N=100
@controller.event
def on_draw():
    controller.clear()

    if naveshape.camino == False:
        naveshape.update()
        navesombra.update() 

    
    if naveshape.camino == False:
        navemover = sg.findNode(escena, "naverot")
        sombramover = sg.findNode(escena,"sombrarot")
        navemover2 = sg.findNode(escena, "navetrasl")
        sombramover2 = sg.findNode(escena,"sombratrasl")
        

        navemover.transform = tr.matmul([tr.rotationZ(naveshape.anguloz),tr.rotationY(naveshape.anguloy)])
        sombramover.transform = tr.matmul([tr.translate(0,0,-0.9),tr.scale(1,1,0), tr.rotationZ(navesombra.anguloz),tr.rotationY(navesombra.anguloy)])

        navemover2.transform = tr.matmul([tr.translate(naveshape.x,naveshape.y,naveshape.z)])
        sombramover2.transform = tr.matmul([tr.translate(naveshape.x,naveshape.y,0)])

    coordenadasnave = sg.findPosition(escena,"navetrasl")
    anguloz=naveshape.anguloz
    camera.update(coordenadasnave, anguloz)

    anillomov = sg.findNode(escena,"anillomov")
    astromov = sg.findNode(escena,"astromov")
    astromov.transform = tr.rotationZ(np.pi/20*controller.total_time)
    anillomov.transform = tr.rotationZ(np.pi/5*controller.total_time)
    
    coordenada1 = sg.findPosition(escena, "naverot")

    if naveshape.guardarp == True or naveshape.guardart == True:
        if naveshape.guardart == False:
            coordenada2 = sg.findPosition(escena, "naverot")
            coordenada2 = coordenada2 / coordenada2[3]
            coordenada2 = coordenada2[0:3]
            naveshape.anterior = coordenada2
            naveshape.puntos.append(coordenada2)
            naveshape.orientacionesy.append(naveshape.anguloy)
            naveshape.orientacionesz.append(naveshape.anguloz)
            naveshape.guardart = True
            naveshape.guardarp = False
        elif naveshape.guardart == True:
            coordenada1 = coordenada1 / coordenada1[3]
            coordenada1 = coordenada1[0:3]
            tangente = (coordenada1*1.7)-naveshape.anterior
            naveshape.tangentes.append(tangente)
            naveshape.guardarp = True
            naveshape.guardart = False
            
    # Si el controller está en modo fillPolygon, dibuja polígonos. Si no, líneas.
    if controller.fillPolygon:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


    if camera.proactual == camera.projection:
        camera.infopro = tr.ortho(-8, 8, -8, 8, 0.1, 100)
        glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE,
                       tr.ortho(-8, 8, -8, 8, 0.1, 100))
    else:
        camera.infopro = tr.perspective(60, float(WIDTH)/float(HEIGHT), 1, 1000)
        glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE,
                       tr.perspective(60, float(WIDTH)/float(HEIGHT), 1, 1000))
    view = tr.lookAt(
            camera.eye,
            camera.at,
            camera.up
        )
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    naveshape.y_direction_rot = 0
    navesombra.y_direction_rot = 0
    #----------------------pirueta
    """
    if naveshape.pirueta == True:
        N2 = 200
        coordenadanave = sg.findPosition(escena, "naverot")
        coordenadanave = coordenadanave / coordenadanave[3]
        coordenadanave = coordenadanave[0:3]
        x = float(coordenadanave[0])
        y = float(coordenadanave[1])
        z = float(coordenadanave[2])

        p1 = np.array([[-(x+3),y,z]]).T
        p2 = np.array([[x,y+3,z]]).T
        p3 = np.array([[x,-(y+3),z]]).T
        p4 = np.array([[x+3,y,z]]).T

        t1 = np.array([[0,4.97056,0]]).T
        t2 = np.array([[4.97056,0,0]]).T
        M1 = hermiteMatrix(p1,p2,t1,t2)
        hermiteCurve1 = evalCurve(M1,N2)
        M2 = hermiteMatrix(p2,p4,-t2,t1)
        hermiteCurve2 = evalCurve(M2,N2)
        M3 = hermiteMatrix(p4,p3,-t1,-t2)
        hermiteCurve3 = evalCurve(M3,N2)
        M4 = hermiteMatrix(p3,p1,t2,-t1)
        hermiteCurve4 = evalCurve(M4,N2)
        hermiteCurveFinal = np.concatenate((hermiteCurve1,hermiteCurve2,hermiteCurve3,hermiteCurve4))

        movernave = sg.findNode(escena, "navetrasl")
        movernave2 = sg.findNode(escena, "naverot")
        moversombra = sg.findNode(escena,"sombratrasl")
        moversombra2 = sg.findNode(escena, "sombrarot")

        movernave.transform = tr.matmul([tr.translate(hermiteCurveFinal[controller.step, 0],hermiteCurveFinal[controller.step, 1], hermiteCurveFinal[controller.step, 2])])
        moversombra.transform = tr.matmul([tr.translate(0,0,-0.9),tr.scale(1,1,0),tr.translate(hermiteCurveFinal[controller.step, 0],hermiteCurveFinal[controller.step, 1], 0)])
        
        if controller.step<N2-1:
            dif_vec = hermiteCurveFinal[controller.step+1]-hermiteCurveFinal[controller.step]
            anguloz = np.sign(dif_vec[1])*np.arccos((dif_vec[0])/np.sqrt((dif_vec[0]*dif_vec[0])+(dif_vec[1]*dif_vec[1])))

            movernave2.transform = tr.matmul([tr.rotationZ(anguloz)])
            moversombra2.transform = tr.matmul([tr.translate(0,0,-0.9),tr.scale(1,1,0),tr.rotationZ(anguloz)])
            navesombra.anguloz = anguloz
            naveshape.anguloz = anguloz
        
        if controller.step>=N2-1:
            controller.step = 0
            naveshape.pirueta = False
        controller.step+=1 
    """
    # ------------------------------------------------------------CURVA
    if naveshape.graficarcurve == True or naveshape.camino == True:
        if naveshape.haycurva == False:
            M = hermiteMatrix(naveshape.puntos[0],naveshape.puntos[1],naveshape.tangentes[0],naveshape.tangentes[1])
            hermiteCurvefinal = evalCurve(M,N)
            naveshape.curva = hermiteCurvefinal
            if len(naveshape.puntos)>=3:
                for i in range(1,len(naveshape.puntos)-1):
                    M = hermiteMatrix(naveshape.puntos[i], naveshape.puntos[i+1],naveshape.tangentes[i],naveshape.tangentes[i+1])
                    hermiteCurve = evalCurve(M,N)
                    hermiteCurvefinal = np.concatenate((hermiteCurvefinal,hermiteCurve))
                    naveshape.curva = hermiteCurvefinal
            naveshape.haycurva = True

        elif naveshape.guardart == False and naveshape.haycurva == True and naveshape.guardarp == True:
            naveshape.guardarp = False
            i = len(naveshape.puntos)-1
            M = hermiteMatrix(naveshape.puntos[i-1], naveshape.puntos[i], naveshape.tangentes[i-1], naveshape.tangentes[i])
            hermiteCurve = evalCurve(M,N)
            hermiteCurvefinal = np.concatenate((naveshape.curva,hermiteCurve))
            naveshape.curva = hermiteCurvefinal

        if naveshape.camino == True:
            movernave = sg.findNode(escena, "navetrasl")
            movernave2 = sg.findNode(escena, "naverot")
            moversombra = sg.findNode(escena,"sombratrasl")
            moversombra2 = sg.findNode(escena, "sombrarot")

            movernave.transform = tr.matmul([tr.translate(naveshape.curva[controller.step, 0],naveshape.curva[controller.step, 1], naveshape.curva[controller.step, 2])])
            moversombra.transform = tr.matmul([tr.translate(0,0,-0.9),tr.scale(1,1,0),tr.translate(naveshape.curva[controller.step, 0],naveshape.curva[controller.step, 1], 0)])
            
            if controller.step == 0:
                movernave2.transform = tr.matmul([tr.rotationZ(naveshape.orientacionesz[0]),tr.rotationY(naveshape.orientacionesy[0]),tr.rotationY(-naveshape.anguloy),tr.rotationZ(-naveshape.anguloz)])
                naveshape.anguloy += naveshape.orientacionesy[0] - naveshape.anguloy
                naveshape.anguloz += naveshape.orientacionesz[0] - naveshape.anguloz

            elif controller.step<(N*(len(naveshape.puntos)-1))-1:
                dif_vec = naveshape.curva[controller.step+1]-naveshape.curva[controller.step]
                z = naveshape.curva[controller.step+1,2]-naveshape.curva[controller.step,2]
                
                anguloz = np.sign(dif_vec[1])*np.arccos((dif_vec[0])/np.sqrt((dif_vec[0]*dif_vec[0])+(dif_vec[1]*dif_vec[1])))
                if dif_vec[0]*dif_vec[1]<0 and naveshape.anguloy>1.52:
                    anguloy = -np.arcsin(-z/np.sqrt((dif_vec[0]*dif_vec[0])+(dif_vec[1]*dif_vec[1])+(dif_vec[2]*dif_vec[2])))
                else:
                    anguloy = np.arcsin(-z/np.sqrt((dif_vec[0]*dif_vec[0])+(dif_vec[1]*dif_vec[1])+(dif_vec[2]*dif_vec[2])))
                #anguloy = np.arcsin(-z/np.sqrt((dif_vec[0]*dif_vec[0])+(dif_vec[1]*dif_vec[1])+(dif_vec[2]*dif_vec[2]))) 
                #anguloy = np.arcsin(-z/naveshape.z_speed)
                movernave2.transform = tr.matmul([tr.rotationY(anguloy),tr.rotationZ(anguloz)])
                moversombra2.transform = tr.matmul([tr.translate(0,0,-0.9),tr.scale(1,1,0),tr.rotationY(anguloy),tr.rotationZ(anguloz)])

                navesombra.anguloz = anguloz
                navesombra.anguloy = anguloy
                naveshape.anguloy = anguloy
                naveshape.anguloz = anguloz
            
            if controller.step>=(N*(len(naveshape.puntos)-1))-1:
                naveshape.camino = False
                controller.step = 0
                naveshape.puntos = []
                naveshape.tangentes = []
                naveshape.orientacionesy = []
                naveshape.orientacionesz = []
                naveshape.graficarcurve = False
                naveshape.curva = None
                naveshape.haycurva = False
            controller.step+=1 

        if naveshape.graficarcurve == True:
            controller.node_data= controller.pipeline2.vertex_list(
            len(naveshape.curva), pyglet.gl.GL_POINTS, position="f"
            )
            controller.joint_data = controller.pipeline2.vertex_list_indexed(
            len(naveshape.curva),
            pyglet.gl.GL_LINES,
            tuple(chain(*(j for j in [range(len(naveshape.curva))]))),
            position="f",
            )
            controller.node_data.position[:] = tuple(
                chain(*((p[0], p[1], p[2]) for p in naveshape.curva))
            )

            controller.joint_data.position[:] = tuple(
                chain(*((p[0], p[1], p[2]) for p in naveshape.curva))
            )
            controller.pipeline2["projection"] = camera.infopro.reshape(16, 1, order="F")
            controller.pipeline2["view"] = view.reshape(16, 1, order="F")
            
            controller.pipeline2.use()
            controller.node_data.draw(pyglet.gl.GL_POINTS)
            controller.joint_data.draw(pyglet.gl.GL_LINES)
    naveshape.guardarp = False
    glUseProgram(controller.pipeline.shaderProgram)
    sg.drawSceneGraphNode(escena, controller.pipeline, "model")
pyglet.clock.schedule(update, controller)
pyglet.app.run()

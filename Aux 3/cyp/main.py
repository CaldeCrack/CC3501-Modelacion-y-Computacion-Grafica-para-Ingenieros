# coding=utf-8
import glfw
from OpenGL.GL import *
from gpu_shape import GPUShape
from easy_shaders import SimpleTextureModelViewProjectionShaderProgram, textureSimpleSetup
import basic_shapes as bs
import transformations as tr
import numpy as np


class Controller():
    def __init__(self):
        self.state = 0
        self.ortho = False

    def nextState(self):
        self.state = (self.state+1) % 4


controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action == glfw.PRESS or action == glfw.REPEAT:

        if key == glfw.KEY_SPACE:
            controller.nextState()
        
        if key == glfw.KEY_ENTER:
            controller.ortho = not controller.ortho

        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def main():
    if not glfw.init():
        glfw.set_window_should_close(window, True)
        return -1

    width = 800
    height = 800

    window = glfw.create_window(width, height, "Perspectivas y Texturas", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)
        return -1

    glfw.make_context_current(window)

    glfw.set_key_callback(window, on_key)

    texPipeline = SimpleTextureModelViewProjectionShaderProgram()

    cubeShape = bs.createMinecraftCube(0.5)
    floorShape = bs.createMinecraftFloor(0.5)


    gpuFloor = GPUShape().initBuffers()
    texPipeline.setupVAO(gpuFloor)
    gpuFloor.fillBuffers(floorShape.vertices, floorShape.indices)
    gpuFloor.texture = textureSimpleSetup("Modelación y Computación Gráfica para Ingenieros/Aux 3/cyp/assets/dirt.png", GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    gpuDirt = GPUShape().initBuffers()
    texPipeline.setupVAO(gpuDirt)
    gpuDirt.fillBuffers(cubeShape.vertices, cubeShape.indices)
    gpuDirt.texture = textureSimpleSetup("Modelación y Computación Gráfica para Ingenieros/Aux 3/cyp/assets/dirt.png", GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    gpuShelf = GPUShape().initBuffers()
    texPipeline.setupVAO(gpuShelf)
    gpuShelf.fillBuffers(cubeShape.vertices, cubeShape.indices)
    gpuShelf.texture = textureSimpleSetup("Modelación y Computación Gráfica para Ingenieros/Aux 3/cyp/assets/bookshelf.png", GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    gpuStone = GPUShape().initBuffers()
    texPipeline.setupVAO(gpuStone)
    gpuStone.fillBuffers(cubeShape.vertices, cubeShape.indices)
    gpuStone.texture = textureSimpleSetup("Modelación y Computación Gráfica para Ingenieros/Aux 3/cyp/assets/cobblestone.png", GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)


    glClearColor(0.15, 0.15, 0.15, 1.0)


    glEnable(GL_DEPTH_TEST)

    
    while not glfw.window_should_close(window):
        t = glfw.get_time()
        glfw.poll_events()

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        if controller.ortho:
            if controller.state == 0:
                projection = tr.ortho(-1, 1, -1, 1, 0.01, 100) 
            if controller.state == 1:
                projection = tr.ortho(-2, 2, -2, 2, 0.01, 100) 
            if controller.state == 2:
                projection = tr.ortho(-4, 4, -4, 4, 0.01, 100) 
            if controller.state == 3:
                l = 4 + 3*np.cos(t)
                projection = tr.ortho(-l, l, -l, l, -100, 100) 
        else:
            if controller.state == 0:
                projection = tr.perspective(45, 1, 0.01, 100)
            if controller.state == 1:
                projection = tr.perspective(45 + 15*(1+np.cos(t)), 1, 0.10, 100)
            if controller.state == 2:
                projection = tr.perspective(45, 1, 0.01, 10*(1+np.cos(t)))
            if controller.state == 3:
                projection = tr.perspective(45, 1, 5*(2+np.cos(t/2)), 100)
        
        view = tr.lookAt(np.array([5, 5*np.cos(t), 5*np.sin(t)]), np.array([0,0,0.5], dtype= float), np.array([0,0,1], dtype= float))   


        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(texPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        
        for x in range(30):
            for y in range(30):
                glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
                    tr.translate(15-x,15-y,0),
                    tr.uniform_scale(1)
                ]))
                texPipeline.drawCall(gpuFloor)

        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
            tr.translate(0,0,0.5),
            tr.translate(0,0,0)
        ]))
        texPipeline.drawCall(gpuDirt)
        
        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
            tr.translate(0,0,0.55),
            tr.uniform_scale(1.1),
            tr.translate(-2,-4,0)
        ]))
        texPipeline.drawCall(gpuShelf)


        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
            tr.translate(0,0,0.85),
            tr.uniform_scale(1.7),  
            tr.translate(-4,-1,0)
        ]))
        texPipeline.drawCall(gpuStone)

        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
            tr.translate(0,0,0.6),
            tr.uniform_scale(1.2),
            tr.translate(-6,-0,0)
        ]))
        texPipeline.drawCall(gpuShelf)

        glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
            tr.translate(0,0,0.5),
            tr.uniform_scale(1),
            tr.translate(4,-2,0)
        ]))
        texPipeline.drawCall(gpuStone)

        glfw.swap_buffers(window)
    glfw.terminate()
    gpuFloor.clear()
    gpuDirt.clear()
    gpuShelf.clear()
    gpuStone.clear()


    return 0


if __name__ == "__main__":
    main()


# coding=utf-8
"""Showing how to handle textures on a square"""

import sys
import os
import pyglet

import libs.shaders as sh
import libs.transformations as tr

from libs.shapes import createTextureQuad
from libs.gpu_shape import createGPUShape
from libs.assets_path import getAssetPath

from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
Controles:

    Cambiar Textura:
        - 1: bricks
        - 2: baboon
        - 3: kirby
        - 4: paine

    Cambiar Wrap Modes: (Cicla entre 'REPEAT', 'MIRRORED REPEAT',
    'CLAMP TO EDGE' y 'MIRRORED CLAMP TO EDGE' en ese orden.)
        - A: sWrapMode
        - S: tWrapMode

    Cambiar Filter Modes: (Cicla entre 'NEAREST' y 'LINEAR' en ese orden.)
        - D: minFilterMode
        - F: maxFilterMode

    Alterar coordenadas de textura (s, t):
    Recordar que las coordenadas de textura son valores normalizados entre 0 y 1
        - LEFT_ARROW: Aumenta el valor en s por 0.1
        - RIGHT_ARROW: Disminute el valor en s por 0.1
        - UP_ARROW: Aumenta el valor en t por 0.1
        - DOWN_ARROW: Disminute el valor en t por 0.1

    - R: Reiniciar a los valores por defecto de la textura.
    Valores por defecto:
        - (s, t) = (1.0, 1.0)
        - sWrapMode = tWrapMode = GL_REPEAT
        - minFilterMode = maxFilterMode = GL_NEAREST

"""

WIDTH, HEIGHT = 800, 800

ASSETS = {
    "bricks": getAssetPath("bricks.jpg"),
    "baboon": getAssetPath("baboon.png"),
    "kirby": getAssetPath("kirby.png"),
    "paine": getAssetPath("torres-del-paine-sq.jpg"),
}

WRAP_MODES = [
    GL_REPEAT,
    GL_MIRRORED_REPEAT,
    GL_CLAMP_TO_EDGE,
    GL_MIRROR_CLAMP_TO_EDGE
]

FILTER_MODES = [
    GL_NEAREST,
    GL_LINEAR
]

class Controller(pyglet.window.Window):

    def __init__(self, width, height, title=f"2D Textures"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.pipeline = sh.SimpleTextureTransformShaderProgram()

        self.texture_coords = [1.0, 1.0]  # [s, t]

        self.ex_shape = createGPUShape(self.pipeline, createTextureQuad(*self.texture_coords))

        self.tex_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
        self.current_tex = "bricks"


        self.ex_shape.texture = sh.textureSimpleSetup(
            ASSETS[self.current_tex], *self.tex_params
        )

    def update_shape_texture(self):
        self.ex_shape = createGPUShape(self.pipeline, createTextureQuad(*self.texture_coords))
        self.ex_shape.texture = sh.textureSimpleSetup(
            ASSETS[self.current_tex], *self.tex_params
        )


controller = Controller(width=WIDTH, height=HEIGHT)


# Setting up the clear screen color
glClearColor(0.15, 0.15, 0.15, 1.0)

glEnable(GL_DEPTH_TEST)

glUseProgram(controller.pipeline.shaderProgram)

# What happens when the user presses these keys
@controller.event
def on_key_press(symbol, modifiers):

    if symbol == pyglet.window.key._1:
        controller.current_tex = "bricks"
        controller.update_shape_texture()
    if symbol == pyglet.window.key._2:
        controller.current_tex = "baboon"
        controller.update_shape_texture()
    if symbol == pyglet.window.key._3:
        controller.current_tex = "kirby"
        controller.update_shape_texture()
    if symbol == pyglet.window.key._4:
        controller.current_tex = "paine"
        controller.update_shape_texture()

    if symbol == pyglet.window.key.A:
        _sWrapMode = WRAP_MODES.index(controller.tex_params[0])
        _sWrapMode = (_sWrapMode + 1) % len(WRAP_MODES)
        controller.tex_params[0] = WRAP_MODES[_sWrapMode]
        controller.update_shape_texture()
    if symbol == pyglet.window.key.S:
        _tWrapMode = WRAP_MODES.index(controller.tex_params[1])
        _tWrapMode = (_tWrapMode + 1) % len(WRAP_MODES)
        controller.tex_params[1] = WRAP_MODES[_tWrapMode]
        controller.update_shape_texture()
    if symbol == pyglet.window.key.D:
        _minFilterMode = FILTER_MODES.index(controller.tex_params[2])
        _minFilterMode = (_minFilterMode + 1) % len(FILTER_MODES)
        controller.tex_params[2] = FILTER_MODES[_minFilterMode]
        controller.update_shape_texture()
    if symbol == pyglet.window.key.D:
        _maxFilterMode = FILTER_MODES.index(controller.tex_params[3])
        _maxFilterMode = (_maxFilterMode + 1) % len(FILTER_MODES)
        controller.tex_params[3] = FILTER_MODES[_maxFilterMode]
        controller.update_shape_texture()

    if symbol == pyglet.window.key.UP:
        controller.texture_coords[1] += 0.1
        controller.update_shape_texture()
    if symbol == pyglet.window.key.DOWN:
        controller.texture_coords[1] -= 0.1
        controller.update_shape_texture()
    if symbol == pyglet.window.key.LEFT:
        controller.texture_coords[0] += 0.1
        controller.update_shape_texture()
    if symbol == pyglet.window.key.RIGHT:
        controller.texture_coords[0] -= 0.1
        controller.update_shape_texture()

    if symbol == pyglet.window.key.R:
        controller.texture_coords = [1.0, 1.0]
        controller.tex_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
        controller.update_shape_texture()

    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()


@controller.event
def on_draw():
    controller.clear()

    controller.set_caption(f"tex: {controller.current_tex}; tex_coords: ({round(controller.texture_coords[0], 1)}, {round(controller.texture_coords[1], 1)}); tex_params: {controller.tex_params}")

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.identity())

    controller.pipeline.drawCall(controller.ex_shape)


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

import os
from collections import defaultdict, deque
from ctypes.wintypes import SIZE
from itertools import chain
from multiprocessing.spawn import prepare

import numpy as np
import pyglet
import pyglet.graphics as pygr
from OpenGL.GL import *
from OpenGL.GL import shaders
from PIL import Image

import libs.transformations as tr
from libs.gpu_shape import prepare_gpu_buffer, texture_setup

vertex_shader = """
#version 330
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 transform;
in vec3 position;
in vec2 texCoords;
out vec2 outTexCoords;
void main()
{
    vec4 vertexPos = model * vec4(position, 1.0);
    gl_Position = projection * view * transform * vertexPos;
    outTexCoords = texCoords;
}
"""

fragment_shader = """
#version 330
in vec2 outTexCoords;
out vec4 outColor;
uniform sampler2D samplerTex;
void main()
{
    vec4 texel = texture(samplerTex, outTexCoords);
    if (texel.a < 0.5)
        discard;
    outColor = texel;
}
"""

point_shader = """
#version 330
uniform mat4 view;
uniform mat4 projection;
in vec3 position;
void main()
{
    gl_PointSize = 5.0;
    gl_Position = projection * view * vec4(position, 1.0);
}
"""

point_fragment_shader = """
#version 330
out vec4 outColor;
void main()
{
    outColor = vec4(1.0, 1.0, 1.0, 1.0);
}
"""

class Ship:
    def __init__(self, *args, **kwargs):
        self.pipeline = shaders.compileProgram(
            shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        )

        self.point_pipeline = shaders.compileProgram(
            shaders.compileShader(point_shader, GL_VERTEX_SHADER),
            shaders.compileShader(point_fragment_shader, GL_FRAGMENT_SHADER),
        )
        

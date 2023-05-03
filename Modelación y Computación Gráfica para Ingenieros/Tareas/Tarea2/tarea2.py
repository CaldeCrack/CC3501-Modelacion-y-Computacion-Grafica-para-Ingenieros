# coding=utf-8
import sys
import os
import pyglet
import numpy as np

import libs.shaders as sh
import libs.transformations as tr

from libs.gpu_shape import createGPUShape
from libs.obj_handler import read_OBJ
from libs.assets_path import getAssetPath

from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WIDTH, HEIGHT = 800, 800

PERSPECTIVE_PROJECTION = 0
ORTOGRAPHIC_PROJECTION = 1

PROJECTIONS = [
    tr.perspective(60, float(WIDTH)/float(HEIGHT), 0.1, 100),  # PERSPECTIVE_PROJECTION
    tr.ortho(-8, 8, -8, 8, 0.1, 100)  # ORTOGRAPHIC_PROJECTION
]

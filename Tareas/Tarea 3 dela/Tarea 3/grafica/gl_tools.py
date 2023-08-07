from OpenGL.GL import *
import numpy as np
from PIL import Image

SIZE_IN_BYTES = 4

def prepare_gpu_buffer(pipeline, vertices, indices, normals=True, texture=True, colors=False):
    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)
    size = len(indices)

    vertex_len = 3
    pos_offset = 0
    normal_offset = 0
    color_offset = 0
    texture_offset = 0

    if normals:
        vertex_len += 3
        normal_offset += 3
        texture_offset += 3
        color_offset += 3
    if colors:
        vertex_len += 3
        texture_offset += 3
        color_offset += 3
    if texture:
        vertex_len += 2
        texture_offset += 3

    stride = SIZE_IN_BYTES * vertex_len

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)

    position = glGetAttribLocation(pipeline, "position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(pos_offset))
    glEnableVertexAttribArray(position)

    if colors:
        color = glGetAttribLocation(pipeline, "color")
        glVertexAttribPointer(
            color, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(color_offset * SIZE_IN_BYTES)
        )
        glEnableVertexAttribArray(color)       

    if texture:
        texCoords = glGetAttribLocation(pipeline, "texCoords")
        glVertexAttribPointer(
            texCoords, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(texture_offset * SIZE_IN_BYTES)
        )
        glEnableVertexAttribArray(texCoords)

    # Unbinding current vao
    glBindVertexArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(
        GL_ARRAY_BUFFER, len(vertices) * SIZE_IN_BYTES, vertices, GL_STATIC_DRAW
    )

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(
        GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW
    )
    return {"vbo": vbo, "vao": vao, "ebo": ebo, "size": size}





def texture_setup(image, sWrapMode, tWrapMode, minFilterMode, maxFilterMode):
    # wrapMode: GL_REPEAT, GL_CLAMP_TO_EDGE
    # filterMode: GL_LINEAR, GL_NEAREST
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, sWrapMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, tWrapMode)

    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minFilterMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, maxFilterMode)

    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = np.array(image, np.uint8)

    if image.mode == "RGB":
        internalFormat = GL_RGB
        format = GL_RGB
    elif image.mode == "RGBA":
        internalFormat = GL_RGBA
        format = GL_RGBA
    else:
        print("Image mode not supported.")
        raise Exception()

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        internalFormat,
        image.size[0],
        image.size[1],
        0,
        format,
        GL_UNSIGNED_BYTE,
        img_data,
    )

    return texture
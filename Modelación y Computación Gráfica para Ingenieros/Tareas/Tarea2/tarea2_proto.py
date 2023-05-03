from pyglet.gl import *

vertex_source = """#version 150 core
    in vec2 position;
    in vec4 colors;
    out vec4 vertex_colors;

    uniform mat4 projection;

    void main()
    {
        gl_Position = projection * vec4(position, 0.0, 1.0);
        vertex_colors = colors;
    }
"""

fragment_source = """#version 150 core
    in vec4 vertex_colors;
    out vec4 final_color;

    void main()
    {
        final_color = vertex_colors;
    }
"""

from pyglet.graphics.shader import Shader, ShaderProgram

vert_shader = Shader(vertex_source, 'vertex')
frag_shader = Shader(fragment_source, 'fragment')
program = ShaderProgram(vert_shader, frag_shader)

class Triangle:
    def __init__(self):
        self.vertices = program.vertex_list(6, GL_TRIANGLES, position=("f3", (-0.5, -0.5, 0.5, 0.5, 0.0, 0.5, 0.5, 0.5, 0.5)),
                                            colors=("f3", (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)))

class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(400, 300)
        glClearColor(0.05, 0.1, 0.05, 1.0)
        self.triangle = Triangle()

    def on_draw(self):
        self.clear()
        self.triangle.vertices.draw(GL_TRIANGLES)

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
    
    def update(self, dt):
        pass

if __name__ == "__main__":
    window = MyWindow(1280, 600, "Tarea 2", resizable=True)
    pyglet.clock.schedule_interval(window.update, 1/60.0)
    pyglet.app.run()
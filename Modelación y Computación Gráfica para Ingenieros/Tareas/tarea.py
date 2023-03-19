import pyglet
import random
from pyglet import shapes

# use this in the powershell terminal opened in the correct folder to activate the enviroment: graf\Scripts\Activate.ps1

# Window initialization
window = pyglet.window.Window(600, 600)
pyglet.gl.glClearColor(0, 0, 0.05, 1)
batch = pyglet.graphics.Batch()

right_central_triangle = shapes.Triangle(10, -50, 10, 50, 30, -0, color=(255, 255, 255), batch=batch)
left_central_triangle = shapes.Triangle(-10, -50, -10, 50, -30, -0, color=(255, 255, 255), batch=batch)

# Window draw
@window.event
def on_draw():
    window.clear()
    batch.draw()

pyglet.app.run()
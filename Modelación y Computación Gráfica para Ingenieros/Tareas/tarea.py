import pyglet
import random
from pyglet import shapes

# use this in the powershell terminal opened in the correct folder to activate the enviroment: graf\Scripts\Activate.ps1
white = (255,255,255)
light_grey = (150,150,150)
blue = (50, 50, 180)

# Window initialization
window = pyglet.window.Window(800, 600, "Spaceships")
pyglet.gl.glClearColor(0, 0, 0.05, 1)
batch = pyglet.graphics.Batch()

def draw_ship(posX, posY, sl, batch=None):
    # inferior , superior, lateral
    right_central_triangle = shapes.Triangle(posX+2, posY-50, posX+2, posY+50, posX+25, posY-15, color=light_grey, batch=batch)
    sl.append(right_central_triangle)
    left_central_triangle = shapes.Triangle(posX-2, posY-50, posX-2, posY+50, posX-25, posY-15, color=light_grey, batch=batch)
    sl.append(left_central_triangle)
    right_right = shapes.Triangle(posX+70, posY-70, posX+35, posY-10, posX+15, posY-20, color=light_grey, batch=batch)
    sl.append(right_right)
    left_left = shapes.Triangle(posX-70, posY-70, posX-35, posY-10, posX-15, posY-20, color=light_grey, batch=batch)
    sl.append(left_left)
    right_central = shapes.Triangle(posX+35, posY-70, posX+20, posY+25, posX+15, posY-30, color=blue, batch=batch)
    sl.append(right_central)
    left_central = shapes.Triangle(posX-35, posY-70, posX-20, posY+25, posX-15, posY-30, color=blue, batch=batch)
    sl.append(left_central)

def draw_star(posX, sl, batch=None):
    star = shapes.Star(posX,630,10,4,5,color=white,batch=batch)
    sl.append(star)

shape_list = []
draw_star(200, shape_list, batch=batch)
draw_ship(400,300, shape_list, batch=batch) # leader
draw_ship(400,100, shape_list, batch=batch) # back
draw_ship(250,200, shape_list, batch=batch) # left back 1
draw_ship(100,150, shape_list, batch=batch) # left back 2
draw_ship(550,200, shape_list, batch=batch) # right back 1
draw_ship(700,150, shape_list, batch=batch) # right back 2

# Window draw
@window.event
def on_draw():
    shape_list[0].y-=3
    window.clear()
    batch.draw()

pyglet.app.run()
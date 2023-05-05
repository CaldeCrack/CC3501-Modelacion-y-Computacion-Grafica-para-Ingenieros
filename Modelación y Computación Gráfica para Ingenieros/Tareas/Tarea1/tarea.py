import pyglet, random, math
from pyglet import clock, shapes

# Vars
moon_white, moon_grey, light_grey, blue, red, orange = (246,241,213), (138,127,141) , (100,100,100), (50, 50, 180), (250, 25, 25), (250, 110, 40)
bg = pyglet.graphics.Group(order=-1)

# Window initialization
window, batch = pyglet.window.Window(800, 600, "Spaceships"), pyglet.graphics.Batch()
pyglet.gl.glClearColor(0, 0, 0.05, 1)

# Useful functions
def draw_ship(posX, posY, sl, batch=None):
    #Red Fire
    red_left = shapes.Triangle(posX-40, posY-20, posX-10, posY-20, posX-25, posY-80, color=red, batch=batch)
    clock.schedule_interval(fire, 0.3, red_left, posY-80)
    sl.append(red_left)
    red_right = shapes.Triangle(posX+40, posY-20, posX+10, posY-20, posX+25, posY-80, color=red, batch=batch)
    clock.schedule_interval(fire, 0.3, red_right, posY-80)
    sl.append(red_right)
    # Orange Fire
    orange_left = shapes.Triangle(posX-32, posY-20, posX-18, posY-20, posX-25, posY-90, color=orange, batch=batch)
    clock.schedule_interval(fire, 0.3, orange_left, posY-90)
    sl.append(orange_left)
    orange_right = shapes.Triangle(posX+32, posY-20, posX+18, posY-20, posX+25, posY-90, color=orange, batch=batch)
    clock.schedule_interval(fire, 0.3, orange_right, posY-90)
    sl.append(orange_right)
    # Central triangles
    right_central_triangle = shapes.Triangle(posX+1, posY-50, posX+1, posY+50, posX+25, posY-15, color=light_grey, batch=batch)
    sl.append(right_central_triangle)
    left_central_triangle = shapes.Triangle(posX-1, posY-50, posX-1, posY+50, posX-25, posY-15, color=light_grey, batch=batch)
    sl.append(left_central_triangle)
    #Middle triangles
    right_right = shapes.Triangle(posX+70, posY-70, posX+35, posY-10, posX+15, posY-20, color=light_grey, batch=batch)
    sl.append(right_right)
    left_left = shapes.Triangle(posX-70, posY-70, posX-35, posY-10, posX-15, posY-20, color=light_grey, batch=batch)
    sl.append(left_left)
    # Outer triangles
    right_central = shapes.Triangle(posX+35, posY-70, posX+20, posY+25, posX+15, posY-30, color=blue, batch=batch)
    sl.append(right_central)
    left_central = shapes.Triangle(posX-35, posY-70, posX-20, posY+25, posX-15, posY-30, color=blue, batch=batch)
    sl.append(left_central)

def generate_stars(dt, sl, batch):
    pos, rot = random.randint(-11,811), random.random()*2*math.pi*(-1)**random.randint(0,1)
    draw_star(dt, pos, rot, sl, batch)

def draw_star(dt, posX, rot, sl, batch=None):
    outr, intr, spikes, vel, freq, sign, rc = random.randint(8,12), random.randint(3,5), random.randint(4,5), random.randint(200,300), random.random()*0.03, (-1)**random.randint(0,1), (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    star = shapes.Star(posX,630,outr,intr,spikes,color=rc,batch=batch,group=bg)
    clock.schedule(move, vel, rot, star, freq, sign, posX)
    sl.append(star)

def move(dt, vel, rot, shape, freq, sign, posX):
    shape.x=posX+sign*math.sin(time(dt)+shape.y*freq)*3
    shape.y-=dt*vel
    shape.rotation+=dt*rot*30
    if shape.y <= -15:
        del shape

def fire(dt, fire, y):
    real_y=0
    if fire.y3 in [90,100]: real_y=15
    elif fire.y3 in [190,200]: real_y=115
    elif fire.y3 in [290,300]: real_y=165
    elif fire.y3 in [490, 500]: real_y=215
    if real_y >= y-5:
        fire.y3=y+20
        real_y+=20
    else:
        fire.y3=y
        real_y-=20

def time(dt):
    time=0
    time+=dt
    return time

# Current time on-window
clock.schedule(time)

# Draw moon
moon_vel = 23
sign = (-1)**random.randint(0,1)
big = shapes.Circle(sign*460+400, 900, 300, color=moon_white, batch=batch, group=bg)
c1 = shapes.Circle(sign*460+400+50, 1000, 80, color=moon_grey, batch=batch, group=bg)
c2 = shapes.Circle(sign*460+400-150, 940, 40, color=moon_grey, batch=batch, group=bg)
c3 = shapes.Circle(sign*460+400+110, 870, 50, color=moon_grey, batch=batch, group=bg)
c4 = shapes.Circle(sign*460+400-20, 980, 60, color=moon_grey, batch=batch, group=bg)
c5 = shapes.Circle(sign*460+400-180, 760, 70, color=moon_grey, batch=batch, group=bg)
c6 = shapes.Circle(sign*460+400+190, 740, 45, color=moon_grey, batch=batch, group=bg)
c7 = shapes.Circle(sign*460+400, 800, 75, color=moon_grey, batch=batch, group=bg)

# Generate multiple stars
star_list = []
clock.schedule_interval(generate_stars, 0.2, star_list, batch)
clock.schedule_interval(generate_stars, 0.35, star_list, batch)
clock.schedule_interval(generate_stars, 0.5, star_list, batch)

# Draw spaceships
shape_list = []
draw_ship(400,300, shape_list, batch=batch) # leader
draw_ship(400,100, shape_list, batch=batch) # back
draw_ship(250,200, shape_list, batch=batch) # left back 1
draw_ship(100,150, shape_list, batch=batch) # left back 2
draw_ship(550,200, shape_list, batch=batch) # right back 1
draw_ship(700,150, shape_list, batch=batch) # right back 2

# Window draw
@window.event
def on_draw():
    window.clear()
    batch.draw()

def update(dt):
    big.y-=dt*moon_vel
    c1.y-=dt*moon_vel
    c2.y-=dt*moon_vel
    c3.y-=dt*moon_vel
    c4.y-=dt*moon_vel
    c5.y-=dt*moon_vel
    c6.y-=dt*moon_vel
    c7.y-=dt*moon_vel

pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()
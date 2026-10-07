from pico2d import *
import math

def move_top():
    for x in range(50,751,5):
        draw_boy(x,550)

def move_right():
    for y in range(550,49,-5):
        draw_boy(750,y)

def move_bottom():
    for x in range(750,49,-5):
        draw_boy(x,50)

def move_left():
    for y in range(50,551,5):
         draw_boy(50,y)

def move_AB():
    n=120
    for step in range(n+1):
        t=step/n 
        x=100+600*t
        y=100
        draw_boy(x,y)

def move_BC():
       n=120
       for step in range(n+1):
           t=step/n
           x=700-300*t
           y=100+400*t
           draw_boy(x,y)

def move_CA():
       n=120
       for step in range(n + 1):
        t = step / n
        x = 400 - 300 * t
        y = 500 - 400 * t
        draw_boy(x, y)

def draw_boy(x,y):
    clear_canvas()
    boy.draw(x,y)
    update_canvas()
    delay(0.01)

def move_circle():
    for degree in range(360):
        theta=math.radians(degree)
        x=400+200*math.cos(theta)
        y=300+200*math.sin(theta)
        draw_boy(x,y)

def move_rectangle():
    move_top()
    move_right()
    move_bottom()
    move_left()

def move_triangle():
       move_AB()
       move_BC()
       move_CA()
 
open_canvas(800,600)
boy=load_image('character.png')

while True:
     move_circle()
     move_rectangle()
     move_triangle()
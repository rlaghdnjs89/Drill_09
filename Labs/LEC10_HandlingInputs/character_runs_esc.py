from pico2d import *

open_canvas()
grass = load_image('grass.png')
character = load_image('animation_sheet.png')


# fill here
running=True
x=800//2
frame=0
dir=0


def handle_events():
   global running,x,dir #전역변수 사용하기
   
   events=get_events()
   for event in events:
       if event.type==SDL_QUIT:
           running=False
       elif event.type==SDL_KEYDOWN:
           if event.key==SDLK_RIGHT:
               dir+=1
           elif event.key==SDLK_LEFT:
               dir-=1
           elif event.key==SDLK_ESCAPE:
               running=False
       elif event.type==SDL_KEYUP:
           if event.key==SDLK_RIGHT:
               dir-=1
           elif event.key==SDLK_LEFT:
               dir+=1



   while running:
       clear_canvas()
       grass.draw(400, 30)
       character.clip_draw(frame * 100, 0, 100, 100, x, 90)
       update_canvas()
       handle_events()
       frame = (frame + 1) % 8
       x += dir*5
       delay(0.05)


frame = 0
for x in range(0, 800, 5):

    clear_canvas()
    grass.draw(400, 30)
    character.clip_draw(frame * 100, 100, 100, 100, x, 90)
    update_canvas()


    handle_events()
    if not running:
       break



    frame = (frame + 1) % 8
    delay(0.05)


close_canvas()

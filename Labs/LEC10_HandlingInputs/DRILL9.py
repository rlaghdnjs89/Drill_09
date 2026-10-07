import os
from pico2d import *

# 캔버스 크기 정의 (TUK_GROUND.png 해상도)
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 1024

open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

# 리소스 경로 설정 및 로드
RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
ground_image = load_image(os.path.join(RESOURCE_DIR, 'TUK_GROUND.png'))

running = True


def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


# 메인 루프
while running:
    handle_events()

    clear_canvas()
    # 배경 화면 전체 렌더링
    ground_image.draw(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)
    update_canvas()

    delay(0.01)

close_canvas()

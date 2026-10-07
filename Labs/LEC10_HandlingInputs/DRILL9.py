import os
from pico2d import *

# 캔버스 크기 정의 (TUK_GROUND.png 해상도)
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 1024

# 스프라이트 프레임 크기 상수
FRAME_WIDTH = 100
FRAME_HEIGHT = 100

open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

# 리소스 경로 설정 및 로드
RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
ground_image = load_image(os.path.join(RESOURCE_DIR, 'TUK_GROUND.png'))
character_sheet = load_image(os.path.join(RESOURCE_DIR, 'animation_sheet.png'))

running = True

# 캐릭터 초기 위치 (화면 중앙)
x = CANVAS_WIDTH // 2
y = CANVAS_HEIGHT // 2

# 애니메이션 프레임 인덱스
frame = 0


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
    # 대기 상태 8프레임 제자리 애니메이션 렌더링
    character_sheet.clip_draw(frame * FRAME_WIDTH, 200, FRAME_WIDTH, FRAME_HEIGHT, x, y)
    update_canvas()

    # 프레임 순환 갱신 (8프레임)
    frame = (frame + 1) % 8

    delay(0.01)

close_canvas()

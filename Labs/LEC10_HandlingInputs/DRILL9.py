import os
from pico2d import *

# 캔버스 크기 정의 (TUK_GROUND.png 해상도)
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 1024

# 스프라이트 프레임 크기 상수
FRAME_WIDTH = 100
FRAME_HEIGHT = 100

# 화면 경계 여백 (스프라이트 중심 기준)
HALF_WIDTH = FRAME_WIDTH // 2
HALF_HEIGHT = FRAME_HEIGHT // 2

# 애니메이션 시트 행 좌표(bottom) 상수
ANIM_RUN_LEFT = 0
ANIM_RUN_RIGHT = 100
ANIM_IDLE_RIGHT = 200
ANIM_IDLE_LEFT = 300

# 캐릭터 이동 속도
SPEED = 5

open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

# 리소스 경로 설정 및 로드
RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
ground_image = load_image(os.path.join(RESOURCE_DIR, 'TUK_GROUND.png'))
character_sheet = load_image(os.path.join(RESOURCE_DIR, 'animation_sheet.png'))

running = True

# 캐릭터 초기 위치 (화면 중앙)
x = CANVAS_WIDTH // 2
y = CANVAS_HEIGHT // 2

# 이동 방향 벡터 (-1, 0, 1)
dir_x = 0
dir_y = 0

# 캐릭터가 마지막으로 바라보던 방향 ('RIGHT' 또는 'LEFT')
face_dir = 'RIGHT'

# 애니메이션 프레임 인덱스
frame = 0


def handle_events():
    global running, dir_x, dir_y
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False
            elif event.key == SDLK_RIGHT:
                dir_x += 1
            elif event.key == SDLK_LEFT:
                dir_x -= 1
            elif event.key == SDLK_UP:
                dir_y += 1
            elif event.key == SDLK_DOWN:
                dir_y -= 1
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                dir_x -= 1
            elif event.key == SDLK_LEFT:
                dir_x += 1
            elif event.key == SDLK_UP:
                dir_y -= 1
            elif event.key == SDLK_DOWN:
                dir_y += 1


# 메인 루프
while running:
    handle_events()

    # 캐릭터 위치 이동 및 화면 경계 클램핑 (상하좌우 4방향 이탈 방지)
    x = max(HALF_WIDTH, min(CANVAS_WIDTH - HALF_WIDTH, x + dir_x * SPEED))
    y = max(HALF_HEIGHT, min(CANVAS_HEIGHT - HALF_HEIGHT, y + dir_y * SPEED))

    # 시선 방향 추적 및 애니메이션 행(bottom) 결정
    if dir_x > 0:
        face_dir = 'RIGHT'
        anim_row = ANIM_RUN_RIGHT
    elif dir_x < 0:
        face_dir = 'LEFT'
        anim_row = ANIM_RUN_LEFT
    elif dir_y != 0:
        # 상/하 이동 시에는 기존 좌/우 바라보는 방향을 유지하며 달리기 애니메이션 재생
        if face_dir == 'RIGHT':
            anim_row = ANIM_RUN_RIGHT
        else:
            anim_row = ANIM_RUN_LEFT
    else:
        # 완전히 정지했을 때 (dir_x == 0, dir_y == 0): 기존 방향 대기 애니메이션 재생
        if face_dir == 'RIGHT':
            anim_row = ANIM_IDLE_RIGHT
        else:
            anim_row = ANIM_IDLE_LEFT

    clear_canvas()
    # 배경 화면 전체 렌더링
    ground_image.draw(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)
    # 결정된 애니메이션 행으로 캐릭터 렌더링
    character_sheet.clip_draw(frame * FRAME_WIDTH, anim_row, FRAME_WIDTH, FRAME_HEIGHT, x, y)
    update_canvas()

    # 프레임 순환 갱신 (8프레임)
    frame = (frame + 1) % 8

    # 자연스러운 애니메이션 재생 주기 (초당 약 20fps 갱신)
    delay(0.05)

close_canvas()

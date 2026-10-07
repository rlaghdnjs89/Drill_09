"""
===============================================================================
과제: Drill #9. 소년 상하 좌우 이동 및 방향 바꾸기 (5점)
-------------------------------------------------------------------------------
[채점 기준 및 구현 사양]
1. 상하좌우 이동 (3점):
   - 상/하/좌/우 방향키를 이용한 4방향 및 대각선 이동
   - 이동 시 해당 방향 달리기 애니메이션 재생
   - 위/아래 이동 시에는 기존 바라보던 좌/우 시선 방향 유지
2. IDLE 애니메이션 (1점):
   - 키 입력이 없는 대기 상태에서 제자리 8프레임 순환 애니메이션 재생
   - 이동 멈춤 시 마지막 시선 방향(좌/우) 유지
3. 화면 경계면 벗어나지 않음 (1점):
   - 1280 x 1024 해상도 경계면 밖으로 캐릭터가 나가지 않도록 클램핑
===============================================================================
"""

import os
from pico2d import *

# -----------------------------------------------------------------------------
# 1. 환경 및 리소스 상수 정의
# -----------------------------------------------------------------------------
# 캔버스 크기 (TUK_GROUND.png 원본 해상도 1280 x 1024)
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 1024

# 스프라이트 프레임 크기 (animation_sheet.png: 802 x 402, 셀 크기 100 x 100)
FRAME_WIDTH = 100
FRAME_HEIGHT = 100

# 화면 경계 여백 (스프라이트 중심 좌표 기준, 반폭 50px)
HALF_WIDTH = FRAME_WIDTH // 2
HALF_HEIGHT = FRAME_HEIGHT // 2

# 스프라이트 시트 행(bottom) 매핑 상수
ANIM_RUN_LEFT = 0     # bottom = 0   : 왼쪽 달리기 (8프레임)
ANIM_RUN_RIGHT = 100  # bottom = 100 : 오른쪽 달리기 (8프레임)
ANIM_IDLE_RIGHT = 200 # bottom = 200 : 오른쪽 대기 (8프레임)
ANIM_IDLE_LEFT = 300  # bottom = 300 : 왼쪽 대기 (8프레임)

# 캐릭터 이동 속도 및 프레임 딜레이
MOVE_SPEED = 7
FRAME_DELAY = 0.04

# -----------------------------------------------------------------------------
# 2. 캔버스 초기화 및 리소스 로드
# -----------------------------------------------------------------------------
open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
ground_image = load_image(os.path.join(RESOURCE_DIR, 'TUK_GROUND.png'))
character_sheet = load_image(os.path.join(RESOURCE_DIR, 'animation_sheet.png'))

# -----------------------------------------------------------------------------
# 3. 게임 상태 변수
# -----------------------------------------------------------------------------
running = True

# 캐릭터 초기 위치 (화면 정중앙)
x = CANVAS_WIDTH // 2
y = CANVAS_HEIGHT // 2

# 이동 방향 벡터 (-1, 0, 1)
dir_x = 0
dir_y = 0

# 캐릭터가 마지막으로 바라보던 방향 ('RIGHT' 또는 'LEFT')
face_dir = 'RIGHT'

# 애니메이션 8프레임 인덱스 (0 ~ 7)
frame = 0


# -----------------------------------------------------------------------------
# 4. 이벤트 처리 함수
# -----------------------------------------------------------------------------
def handle_events():
    """키보드 입력(상/하/좌/우/ESC) 및 윈도우 종료 이벤트 처리"""
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


# -----------------------------------------------------------------------------
# 5. 애니메이션 및 게임 로직 갱신 함수
# -----------------------------------------------------------------------------
def get_animation_row(dx, dy, current_face_dir):
    """
    현재 이동 방향 및 시선 방향에 따라 출력할 스프라이트 행(bottom) 반환
    - 상/하 이동 시에는 기존 좌/우 시선 방향을 유지하며 달리기 애니메이션 재생
    - 정지 시에는 마지막 시선 방향의 IDLE 애니메이션 재생
    """
    if dx > 0:
        return ANIM_RUN_RIGHT
    elif dx < 0:
        return ANIM_RUN_LEFT
    elif dy != 0:
        # 상/하 이동 시 기존 바라보던 좌/우 방향 유지 달리기
        return ANIM_RUN_RIGHT if current_face_dir == 'RIGHT' else ANIM_RUN_LEFT
    else:
        # 정지(IDLE) 상태: 마지막 시선 방향 유지 대기
        return ANIM_IDLE_RIGHT if current_face_dir == 'RIGHT' else ANIM_IDLE_LEFT


def update():
    """캐릭터 위치 갱신, 화면 경계 클램핑, 시선 방향 갱신, 프레임 카운팅"""
    global x, y, face_dir, frame

    # 위치 이동 및 화면 경계 클램핑 (1280x1024 해상도 이탈 방지)
    x = max(HALF_WIDTH, min(CANVAS_WIDTH - HALF_WIDTH, x + dir_x * MOVE_SPEED))
    y = max(HALF_HEIGHT, min(CANVAS_HEIGHT - HALF_HEIGHT, y + dir_y * MOVE_SPEED))

    # 좌/우 이동 시 시선 방향 갱신
    if dir_x > 0:
        face_dir = 'RIGHT'
    elif dir_x < 0:
        face_dir = 'LEFT'

    # 8프레임 순환 카운팅
    frame = (frame + 1) % 8


# -----------------------------------------------------------------------------
# 6. 화면 렌더링 함수
# -----------------------------------------------------------------------------
def render():
    """배경 화면 및 캐릭터 애니메이션 프레임 렌더링"""
    anim_row = get_animation_row(dir_x, dir_y, face_dir)

    clear_canvas()
    # 배경 화면 전체 출력 (중앙 좌표 640, 512)
    ground_image.draw(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)
    # 현재 상태에 맞는 캐릭터 스프라이트 렌더링
    character_sheet.clip_draw(frame * FRAME_WIDTH, anim_row, FRAME_WIDTH, FRAME_HEIGHT, x, y)
    update_canvas()


# -----------------------------------------------------------------------------
# 7. 메인 루프 실행 진입점
# -----------------------------------------------------------------------------
def main():
    """게임 메인 루프 실행 및 종료 제어"""
    while running:
        handle_events()
        update()
        render()
        delay(FRAME_DELAY)

    close_canvas()


if __name__ == '__main__':
    main()


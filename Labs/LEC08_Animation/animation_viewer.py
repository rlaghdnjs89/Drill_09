from dataclasses import dataclass
from pathlib import Path
from time import monotonic

from pico2d import (
    SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE,
    clear_canvas, close_canvas, delay, get_events,
    load_image, open_canvas, update_canvas,
)

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
SHEET_COLUMNS = 6
SHEET_ROWS = 4
CELL_SIZE = 256
DRAW_SIZE = 592
LOOPS_PER_ACTION = 5
PAUSE_SECONDS = 1.0
ASSET_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Animation:
    name: str
    row: int  # zero is the top row of the PNG
    frames: tuple[int, ...]
    fps: float


WALK = Animation('Walk', 0, (0, 1, 2, 3, 4, 5), 8.0)
RUN = Animation('Run', 1, (0, 1, 2, 3, 4, 5), 11.0)
JUMP = Animation('Jump', 2, (0, 1, 2, 3, 4, 5), 8.0)
ATTACK = Animation('Attack', 3, (0, 1, 2, 3, 4), 10.0)
ANIMATIONS = (WALK, RUN, JUMP, ATTACK)

# Opaque bounds relative to each cell; some sword tips extend into the next cell.
# Computed from alpha > 8; source_rect adds a one-pixel safety margin.
FRAME_BOUNDS = {
    0: (
        (35, 48, 228, 238), (31, 47, 227, 238),
        (30, 47, 228, 238), (28, 48, 227, 238),
        (33, 48, 226, 238), (33, 48, 224, 238),
    ),
    1: (
        (35, 41, 253, 227), (39, 40, 255, 227),
        (30, 42, 251, 228), (32, 38, 257, 255),
        (40, 41, 256, 228), (39, 42, 237, 228),
    ),
    2: (
        (41, 81, 239, 247), (39, 40, 245, 255),
        (33, 13, 235, 204), (23, 0, 221, 177),
        (18, 25, 243, 231), (40, 77, 236, 247),
    ),
    3: (
        (33, 35, 234, 221), (27, 0, 201, 221),
        (4, 34, 250, 221), (43, 36, 281, 221),
        (38, 35, 289, 221), (35, 35, 224, 221),
    ),
}

def source_rect(animation: Animation, frame_index: int) -> tuple[int, int, int, int]:
    column = animation.frames[frame_index]
    left, top, right, bottom = FRAME_BOUNDS[animation.row][column]
    left = max(0, left - 1)
    top = max(0, top - 1)
    right = min(SHEET_COLUMNS * CELL_SIZE - 1 - column * CELL_SIZE, right + 1)
    bottom = min(CELL_SIZE - 1, bottom + 1)
    return (
        column * CELL_SIZE + left,
        (SHEET_ROWS - 1 - animation.row) * CELL_SIZE + CELL_SIZE - 1 - bottom,
        right - left + 1,
        bottom - top + 1,
    )


def target_rect(animation: Animation, frame_index: int) -> tuple[int, int, int, int]:
    column = animation.frames[frame_index]
    left, bottom, width, height = source_rect(animation, frame_index)
    scale = DRAW_SIZE / CELL_SIZE
    cell_left = column * CELL_SIZE
    cell_bottom = (SHEET_ROWS - 1 - animation.row) * CELL_SIZE
    center_x = CANVAS_WIDTH / 2 + (left - cell_left + width / 2 - CELL_SIZE / 2) * scale
    center_y = CANVAS_HEIGHT / 2 + (bottom - cell_bottom + height / 2 - CELL_SIZE / 2) * scale
    return round(center_x), round(center_y), round(width * scale), round(height * scale)


def playback_indices(animation: Animation) -> tuple[int, ...]:
    return tuple(range(len(animation.frames))) * LOOPS_PER_ACTION


def exit_requested() -> bool:
    for event in get_events():
        if event.type == SDL_QUIT:
            return True
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return True
    return False


def wait_or_exit(seconds: float) -> bool:
    deadline = monotonic() + seconds
    while True:
        if exit_requested():
            return False
        remaining = deadline - monotonic()
        if remaining <= 0:
            return True
        delay(min(1 / 60, remaining))


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        grass = load_image(str(ASSET_DIR / 'grass.png'))
        character = load_image(str(ASSET_DIR / 'hero_sprite_sheet.png'))

        if (character.w, character.h) != (SHEET_COLUMNS * CELL_SIZE, SHEET_ROWS * CELL_SIZE):
            raise ValueError('hero_sprite_sheet.png must be a 6 x 4 sheet of 256 px cells')

        while True:
            for animation in ANIMATIONS:
                for frame in playback_indices(animation):
                    if exit_requested():
                        return
                    clear_canvas()
                    grass.draw(CANVAS_WIDTH // 2, 30)
                    character.clip_draw(
                        *source_rect(animation, frame),
                        *target_rect(animation, frame),
                    )
                    update_canvas()
                    if not wait_or_exit(1 / animation.fps):
                        return
                if not wait_or_exit(PAUSE_SECONDS):
                    return
    finally:
        close_canvas()


if __name__ == '__main__':
    main()

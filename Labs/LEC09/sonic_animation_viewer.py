"""소닉 스프라이트 시트 애니메이션 뷰어."""

import os
from dataclasses import dataclass
from math import pi, sin
from pathlib import Path
from time import monotonic
from typing import Callable, Literal

from pico2d import (
    SDL_KEYDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    close_canvas,
    delay,
    draw_line,
    get_events,
    load_font,
    load_image,
    open_canvas,
    update_canvas,
)


CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 600
BASELINE_Y = CANVAS_HEIGHT / 2
SPRITE_SCALE = 4.0
LOOPS_PER_ACTION = 5
PAUSE_SECONDS = 1.0
RENDER_HZ = 60.0
EXPECTED_ACTION_COUNT = 10
EXPECTED_FRAME_COUNT = 76
EXPECTED_MOVING_ACTION_COUNT = 8
ASSET_DIR = Path(__file__).resolve().parent
SPRITE_PATH = ASSET_DIR / "sonic-sprite.png"
FONT_PATH = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "malgun.ttf"


@dataclass(frozen=True)
class Animation:
    """One ordered action and its source rectangles in pico2d coordinates."""

    name: str
    frames: tuple[tuple[int, int, int, int], ...]
    fps: float
    anchor: Literal["center", "bottom"] = "center"
    movement: Literal["stationary", "horizontal", "jump"] = "stationary"
    speed: float = 0.0
    jump_height: float = 0.0


@dataclass
class MotionState:
    x: float = CANVAS_WIDTH / 2
    y: float = CANVAS_HEIGHT / 2
    direction: int = 1


# Rectangles are opaque sprite bounds in pico2d's bottom-left source coordinates.
# The sheet contains 10 action sequences with 76 animation frames in total.
ANIMATIONS: tuple[Animation, ...] = (
    Animation(
        "idle",
        (
            (1, 447, 29, 39), (31, 447, 26, 38), (58, 447, 28, 39),
            (86, 447, 30, 38), (118, 447, 30, 38), (150, 447, 30, 38),
            (182, 447, 29, 38), (211, 448, 29, 38), (240, 448, 29, 38),
            (270, 448, 24, 32), (302, 448, 29, 26),
        ),
        10.0,
        "bottom",
    ),
    Animation(
        "walk",
        (
            (8, 408, 26, 37), (37, 408, 27, 37), (65, 407, 31, 38),
            (97, 408, 37, 37), (135, 410, 32, 35), (170, 408, 32, 38),
            (206, 408, 26, 38), (238, 408, 24, 37), (263, 408, 30, 37),
            (295, 408, 36, 37), (334, 409, 32, 36), (370, 408, 29, 38),
        ),
        10.0,
        "bottom",
        movement="horizontal",
        speed=100.0,
    ),
    Animation(
        "run",
        (
            (1, 361, 33, 40), (39, 362, 35, 39), (89, 362, 35, 38),
            (130, 362, 34, 42), (181, 362, 34, 41), (228, 363, 33, 40),
        ),
        10.0,
        "bottom",
        movement="horizontal",
        speed=220.0,
    ),
    Animation(
        "jump_roll",
        (
            (1, 326, 29, 30), (35, 327, 29, 31), (67, 327, 30, 29),
            (98, 327, 31, 29), (131, 327, 29, 30), (162, 326, 29, 31),
            (193, 326, 30, 29), (230, 326, 31, 29), (268, 325, 30, 30),
        ),
        10.0,
        movement="jump",
        speed=140.0,
        jump_height=120.0,
    ),
    Animation(
        "skid_push",
        (
            (1, 292, 30, 27), (36, 292, 29, 27), (70, 292, 29, 27),
            (105, 292, 29, 27), (139, 292, 29, 27), (174, 292, 29, 27),
        ),
        10.0,
        "bottom",
        movement="horizontal",
        speed=80.0,
    ),
    Animation(
        "action_06",
        (
            (1, 251, 29, 35), (36, 251, 30, 35), (74, 251, 31, 35),
            (111, 251, 31, 36), (149, 251, 30, 35), (186, 251, 31, 36),
        ),
        10.0,
        movement="horizontal",
        speed=140.0,
    ),
    Animation(
        "action_07",
        (
            (1, 207, 29, 35), (36, 207, 30, 35), (72, 208, 39, 31),
            (123, 208, 39, 32), (172, 208, 39, 31), (218, 208, 38, 32),
        ),
        10.0,
        movement="horizontal",
        speed=180.0,
    ),
    Animation(
        "action_08",
        (
            (1, 154, 24, 45), (31, 154, 29, 44), (65, 154, 20, 44),
            (90, 155, 25, 43), (119, 155, 25, 43), (149, 154, 20, 44),
            (184, 156, 40, 28), (232, 157, 39, 27),
        ),
        10.0,
        movement="horizontal",
        speed=100.0,
    ),
    Animation(
        "action_09",
        (
            (1, 108, 27, 38), (31, 110, 31, 36), (64, 110, 31, 36),
            (99, 110, 33, 38), (136, 110, 32, 36), (176, 110, 33, 36),
            (217, 110, 33, 36), (254, 111, 33, 36),
        ),
        10.0,
        movement="horizontal",
        speed=120.0,
    ),
    Animation(
        "action_10",
        (
            (6, 65, 34, 31), (49, 65, 34, 34),
            (96, 65, 23, 33), (125, 59, 23, 39),
        ),
        10.0,
        "bottom",
    ),
)


def exit_requested() -> bool:
    """Return True when the user asks to close the viewer."""
    for event in get_events():
        if event.type == SDL_QUIT:
            return True
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return True
    return False


def animation_scale(animation: Animation) -> float:
    max_width = max(frame[2] for frame in animation.frames)
    max_height = max(frame[3] for frame in animation.frames)
    return min(
        SPRITE_SCALE,
        CANVAS_WIDTH / max_width,
        CANVAS_HEIGHT / max_height,
    )


def draw_centered_frame(
    sprite_sheet: object,
    animation: Animation,
    source_rect: tuple[int, int, int, int],
    position: tuple[float, float] = (CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2),
) -> None:
    """Draw one frame in its action's fixed box and pivot."""
    left, bottom, width, height = source_rect
    max_height = max(frame[3] for frame in animation.frames)
    scale = animation_scale(animation)
    center_y = position[1]
    if animation.anchor == "bottom":
        center_y += round((height - max_height) * scale / 2)
    sprite_sheet.clip_draw(
        left,
        bottom,
        width,
        height,
        round(position[0]),
        center_y,
        round(width * scale),
        round(height * scale),
    )


def wait_or_exit(
    seconds: float,
    on_start: Callable[[], None] | None = None,
) -> bool:
    """Wait for the requested duration while continuing to process exit events."""
    if on_start is not None:
        on_start()
    deadline = monotonic() + seconds
    while True:
        if exit_requested():
            return False
        remaining = deadline - monotonic()
        if remaining <= 0:
            return True
        delay(min(1.0 / 60.0, remaining))


def wait_until(deadline: float) -> bool:
    """Wait for a frame deadline while remaining responsive to exit events."""
    while True:
        if exit_requested():
            return False
        remaining = deadline - monotonic()
        if remaining <= 0:
            return True
        delay(min(1.0 / 60.0, remaining))


def draw_status(
    font: object,
    animation: Animation,
    cycle_number: int,
    status: str,
    position: tuple[float, float] = (CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2),
) -> None:
    text = (
        f"동작: {animation.name}    반복: {cycle_number}/{LOOPS_PER_ACTION}"
        f"    위치: ({round(position[0])}, {round(position[1])})    상태: {status}"
    )
    font.draw(24, 24, text, (35, 45, 60))


def draw_background() -> None:
    """Clear to pico2d's light neutral background and draw a ground guide."""
    clear_canvas()
    draw_line(24, 210, CANVAS_WIDTH - 24, 210, 130, 145, 160, 255)


def draw_paused_frame(
    sprite_sheet: object,
    font: object,
    animation: Animation,
    motion: MotionState,
) -> None:
    draw_background()
    position = (motion.x, motion.y)
    draw_centered_frame(sprite_sheet, animation, animation.frames[-1], position)
    draw_status(font, animation, LOOPS_PER_ACTION, "대기", position)
    update_canvas()


def advance_horizontal_motion(
    animation: Animation,
    motion: MotionState,
    delta_time: float,
    action_progress: float,
) -> None:
    """Advance a moving action and wrap it to the opposite canvas edge."""
    if animation.movement == "stationary" or delta_time <= 0:
        return
    scale = animation_scale(animation)
    half_width = max(frame[2] for frame in animation.frames) * scale / 2
    min_x = half_width
    max_x = CANVAS_WIDTH - half_width
    next_x = motion.x + motion.direction * animation.speed * delta_time
    travel_width = max_x - min_x
    motion.x = min_x + (next_x - min_x) % travel_width
    if animation.movement == "jump":
        progress = min(1.0, max(0.0, action_progress))
        motion.y = BASELINE_Y + animation.jump_height * sin(pi * progress)
    else:
        motion.y = BASELINE_Y


def play_cycle(
    sprite_sheet: object,
    font: object,
    animation: Animation,
    cycle_number: int,
    motion: MotionState,
) -> bool:
    """Play frames and update the position smoothly until the cycle ends."""
    cycle_duration = len(animation.frames) / animation.fps
    cycle_started = monotonic()
    previous_time = cycle_started
    while True:
        if exit_requested():
            return False
        now = monotonic()
        elapsed = min(now - cycle_started, cycle_duration)
        delta_time = max(0.0, now - previous_time)
        action_progress = elapsed / cycle_duration
        frame_index = min(int(elapsed * animation.fps), len(animation.frames) - 1)
        advance_horizontal_motion(animation, motion, delta_time, action_progress)
        draw_background()
        position = (motion.x, motion.y)
        draw_centered_frame(sprite_sheet, animation, animation.frames[frame_index], position)
        draw_status(font, animation, cycle_number, "재생", position)
        update_canvas()
        previous_time = now
        if elapsed >= cycle_duration:
            return True
        if not wait_until(now + min(1.0 / RENDER_HZ, cycle_duration - elapsed)):
            return False


def play_action(
    sprite_sheet: object,
    font: object,
    animation: Animation,
    motion: MotionState,
) -> bool:
    """Play one action five times, pause, then let the caller advance."""
    motion.x = CANVAS_WIDTH / 2
    motion.y = BASELINE_Y
    motion.direction = 1
    for cycle_number in range(1, LOOPS_PER_ACTION + 1):
        if not play_cycle(sprite_sheet, font, animation, cycle_number, motion):
            return False
    return wait_or_exit(
        PAUSE_SECONDS,
        lambda: draw_paused_frame(sprite_sheet, font, animation, motion),
    )


def validate_animations(sprite_sheet: object) -> None:
    """Reject incomplete animation data or source rectangles outside the sheet."""
    if not ANIMATIONS:
        raise ValueError("At least one animation must be defined")
    if len(ANIMATIONS) != EXPECTED_ACTION_COUNT:
        raise ValueError(f"Expected {EXPECTED_ACTION_COUNT} action sequences")
    for animation in ANIMATIONS:
        if not animation.frames:
            raise ValueError(f"Animation {animation.name!r} has no frames")
        if animation.fps <= 0:
            raise ValueError(f"Animation {animation.name!r} must have positive FPS")
        if animation.anchor not in {"center", "bottom"}:
            raise ValueError(f"Animation {animation.name!r} has an invalid anchor")
        if animation.movement not in {"stationary", "horizontal", "jump"}:
            raise ValueError(f"Animation {animation.name!r} has an invalid movement type")
        if animation.movement == "stationary" and animation.speed != 0:
            raise ValueError(f"Stationary animation {animation.name!r} cannot have speed")
        if animation.movement != "stationary" and animation.speed <= 0:
            raise ValueError(f"Moving animation {animation.name!r} needs positive speed")
        if animation.movement == "jump" and animation.jump_height <= 0:
            raise ValueError(f"Jump animation {animation.name!r} needs a positive jump height")
        for index, (left, bottom, width, height) in enumerate(animation.frames):
            if (
                left < 0
                or bottom < 0
                or width <= 0
                or height <= 0
                or left + width > sprite_sheet.w
                or bottom + height > sprite_sheet.h
            ):
                raise ValueError(
                    f"Frame {index} in {animation.name!r} is outside the sprite sheet"
                )
    frame_count = sum(len(animation.frames) for animation in ANIMATIONS)
    if frame_count != EXPECTED_FRAME_COUNT:
        raise ValueError(f"Expected {EXPECTED_FRAME_COUNT} frames, found {frame_count}")
    moving_count = sum(animation.movement != "stationary" for animation in ANIMATIONS)
    if moving_count != EXPECTED_MOVING_ACTION_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_MOVING_ACTION_COUNT} moving actions, found {moving_count}"
        )


def main() -> None:
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        sprite_sheet = load_image(str(SPRITE_PATH))
        validate_animations(sprite_sheet)
        font = load_font(str(FONT_PATH), 18)
        motion = MotionState()
        while True:
            for animation in ANIMATIONS:
                if not play_action(sprite_sheet, font, animation, motion):
                    return
    finally:
        close_canvas()


if __name__ == "__main__":
    main()

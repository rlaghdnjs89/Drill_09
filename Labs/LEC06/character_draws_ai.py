"""Move a character around a circle, rectangle, and triangle forever."""

import math
from pathlib import Path

from pico2d import clear_canvas, delay, load_image, open_canvas, update_canvas


FRAME_DELAY = 0.01


def draw_at(image, x, y):
    clear_canvas()
    image.draw(x, y)
    update_canvas()
    delay(FRAME_DELAY)


def move_line(image, start, end, steps):
    start_x, start_y = start
    end_x, end_y = end
    for step in range(steps + 1):
        progress = step / steps
        x = start_x + (end_x - start_x) * progress
        y = start_y + (end_y - start_y) * progress
        draw_at(image, x, y)


def move_circle(image):
    for degree in range(361):
        angle = math.radians(degree)
        x = 400 + 200 * math.cos(angle)
        y = 300 + 200 * math.sin(angle)
        draw_at(image, x, y)


def move_rectangle(image):
    corners = ((50, 550), (750, 550), (750, 50), (50, 50), (50, 550))
    for start, end in zip(corners, corners[1:]):
        steps = int(max(abs(end[0] - start[0]), abs(end[1] - start[1])) / 5)
        move_line(image, start, end, steps)


def move_triangle(image):
    corners = ((100, 100), (700, 100), (400, 500), (100, 100))
    for start, end in zip(corners, corners[1:]):
        move_line(image, start, end, 120)


def main():
    open_canvas(800, 600)
    image_path = Path(__file__).resolve().with_name("character.png")
    image = load_image(str(image_path))

    while True:
        move_circle(image)
        move_rectangle(image)
        move_triangle(image)


if __name__ == "__main__":
    main()

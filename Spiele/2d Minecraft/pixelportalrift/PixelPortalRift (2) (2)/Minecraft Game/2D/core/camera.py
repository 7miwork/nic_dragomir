from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Camera:
    x: float = 0.0
    y: float = 0.0

    def update(self, target_x: float, target_y: float, screen_width: int, screen_height: int, world_pixel_width: int, world_pixel_height: int, lerp: float) -> None:
        desired_x = target_x - screen_width / 2
        desired_y = target_y - screen_height / 2

        self.x += (desired_x - self.x) * lerp
        self.y += (desired_y - self.y) * lerp

        max_x = max(0, world_pixel_width - screen_width)
        max_y = max(0, world_pixel_height - screen_height)

        if self.x < 0:
            self.x = 0
        elif self.x > max_x:
            self.x = max_x

        if self.y < 0:
            self.y = 0
        elif self.y > max_y:
            self.y = max_y

    def world_to_screen(self, world_x: float, world_y: float) -> tuple[int, int]:
        return int(world_x - self.x), int(world_y - self.y)

from __future__ import annotations

from dataclasses import dataclass
import random
import math

import pygame


@dataclass
class Mob:
    mob_id: str
    rect: pygame.Rect
    color: tuple[int, int, int]
    speed: float
    damage_per_second: float

    _dir: int = 1
    _time_to_turn: float = 0.0
    _detection_range: float = 200.0  # Pixels

    def update(self, dt: float, solid_rects: list[pygame.Rect], player_rect: pygame.Rect | None = None) -> None:
        # Check if player is in detection range
        if player_rect is not None:
            dist_x = abs(self.rect.centerx - player_rect.centerx)
            dist_y = abs(self.rect.centery - player_rect.centery)
            distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
            
            if distance < self._detection_range:
                # Chase player
                if player_rect.centerx > self.rect.centerx:
                    self._dir = 1
                else:
                    self._dir = -1
                self._time_to_turn = 10.0  # Keep chasing
            else:
                # Random patrol
                self._time_to_turn -= dt
                if self._time_to_turn <= 0:
                    self._dir = random.choice([-1, 1])
                    self._time_to_turn = random.uniform(0.8, 2.0)
        else:
            # Random patrol (fallback)
            self._time_to_turn -= dt
            if self._time_to_turn <= 0:
                self._dir = random.choice([-1, 1])
                self._time_to_turn = random.uniform(0.8, 2.0)

        self.rect.x += int(self._dir * self.speed * dt)
        for tile_rect in solid_rects:
            if self.rect.colliderect(tile_rect):
                if self._dir > 0:
                    self.rect.right = tile_rect.left
                else:
                    self.rect.left = tile_rect.right
                self._dir *= -1
                self._time_to_turn = random.uniform(0.4, 1.2)

    def touches_player(self, player_rect: pygame.Rect) -> bool:
        return self.rect.colliderect(player_rect)

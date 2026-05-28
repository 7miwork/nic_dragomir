from __future__ import annotations

from dataclasses import dataclass

import pygame

from core.constants import SOLID_TILES, TILE_SIZE


@dataclass(frozen=True)
class BaseWorld:
    name: str
    tilemap: list[str]
    spawn_point: tuple[int, int]
    background_color: tuple[int, int, int]

    @property
    def width_in_tiles(self) -> int:
        if not self.tilemap:
            return 0
        return max(len(row) for row in self.tilemap)

    @property
    def height_in_tiles(self) -> int:
        return len(self.tilemap)

    @property
    def width_in_pixels(self) -> int:
        return self.width_in_tiles * TILE_SIZE

    @property
    def height_in_pixels(self) -> int:
        return self.height_in_tiles * TILE_SIZE

    def spawn_in_pixels(self) -> tuple[int, int]:
        tile_x, tile_y = self.spawn_point
        return tile_x * TILE_SIZE, tile_y * TILE_SIZE

    def iter_solid_tile_rects(self) -> list[pygame.Rect]:
        solids: list[pygame.Rect] = []
        for y, row in enumerate(self.tilemap):
            for x, ch in enumerate(row):
                if ch in SOLID_TILES:
                    solids.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return solids

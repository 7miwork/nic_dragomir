from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class Item:
    item_id: str
    rect: pygame.Rect
    color: tuple[int, int, int]

    def try_pickup(self, player_rect: pygame.Rect) -> bool:
        return self.rect.colliderect(player_rect)

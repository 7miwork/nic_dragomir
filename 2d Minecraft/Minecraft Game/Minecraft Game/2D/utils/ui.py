from __future__ import annotations

import pygame

from core.constants import COLOR_TEXT


class Ui:
    def __init__(self, font: pygame.font.Font) -> None:
        self._font = font

    def draw_text(self, surface: pygame.Surface, text: str, x: int, y: int) -> None:
        img = self._font.render(text, True, COLOR_TEXT)
        surface.blit(img, (x, y))

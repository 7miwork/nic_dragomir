from __future__ import annotations

import sys

import pygame

import config
from core.renderer2d import Renderer2D
from core.scene import Scene
from utils.ui import Ui


class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.CAPTION)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 22)
        self.ui = Ui(self.font)

        self.scene = Scene.new("grassland")
        self.renderer = Renderer2D(self.ui)

        self._world_hotkeys: list[tuple[int, str]] = [
            (pygame.K_1, "grassland"),
            (pygame.K_2, "stoneworld"),
            (pygame.K_3, "waterworld"),
            (pygame.K_4, "lavaworld"),
            (pygame.K_5, "richworld"),
            (pygame.K_6, "nukeworld"),
        ]

    def run(self) -> None:
        while True:
            dt = self.clock.tick(config.FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if not self.scene.crafting_open:
                    for key, world_id in self._world_hotkeys:
                        if event.key == key:
                            self.scene.switch_world(world_id)
                            break

            self.scene.handle_event(event)

    def _update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        self.scene.handle_input(keys)
        self.scene.update(dt)

    def _draw(self) -> None:
        fps = int(self.clock.get_fps())
        self.renderer.draw(self.screen, self.scene, fps)
        pygame.display.flip()

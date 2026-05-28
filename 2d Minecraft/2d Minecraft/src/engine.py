# src/engine.py

import pygame
from constants import TILE_SIZE, COLORS

COLORS = {
    "grass": (34, 177, 76),
    "dirt": (185, 122, 87),
    "stone": (127, 127, 127),
    # weitere Tile-Typen nach Bedarf
}

class GameEngine:
    def __init__(self, screen, world, player):
        self.screen = screen
        self.world = world
        self.player = player

    def draw_world(self):
        self.world.draw(self.screen)

    def draw_player(self):
        self.player.draw(self.screen)

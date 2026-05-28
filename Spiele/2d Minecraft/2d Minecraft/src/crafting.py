# src/engine.py

import pygame
from constants import *

class GameEngine:
    def __init__(self, screen, world, player):
        self.screen = screen
        self.world = world
        self.player = player

    def draw_world(self):
        for x in range(self.world.width):
            for y in range(self.world.height):
                tile = self.world.tiles[x][y]
                color = COLORS.get(tile.type, (255, 255, 255))
                pygame.draw.rect(self.screen, color, pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def draw_player(self):
        if self.player.image:
            self.screen.blit(self.player.image, (self.player.x * TILE_SIZE, self.player.y * TILE_SIZE))
        else:
            pygame.draw.rect(self.screen, (255, 255, 0), pygame.Rect(self.player.x*TILE_SIZE, self.player.y*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def update(self):
        self.draw_world()
        self.draw_player()
        pygame.display.flip()
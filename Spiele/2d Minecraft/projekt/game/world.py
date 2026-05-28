# src/world.py

import pygame
from constants import *
from tiles import Tile
import random

class World:
    def __init__(self, width, height, world_type="grassland"):
        self.width = width
        self.height = height
        self.world_type = world_type
        self.tiles = [[None for _ in range(height)] for _ in range(width)]
        self.generate_world()

    def generate_world(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.world_type == "grassland":
                    if y > self.height // 2:
                        self.tiles[x][y] = Tile(DIRT)
                    else:
                        self.tiles[x][y] = Tile(GRASS)
                elif self.world_type == "stoneworld":
                    self.tiles[x][y] = Tile(STONE)

    def is_walkable(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y].type != STONE
        return False
    
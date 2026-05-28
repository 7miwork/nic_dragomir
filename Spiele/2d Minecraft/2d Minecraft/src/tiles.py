# src/tiles.py

import pygame
from constants import *

class Tile:
    def __init__(self, tile_type, image=None):
        self.type = tile_type
        self.image = image or self.load_default_image(tile_type)
    
    def load_default_image(self, tile_type):
        """Erzeugung einfache Platzhalterblockbilder."""
        surface = pygame.Surface((32, 32)) #Standartgroesse
        
        color_map = {
            GRASS: (80, 200, 80),
            DIRT: (120, 72, 0),
            STONE: (130, 130, 130),
            GRAVEL: (100, 100, 100),
            SAND: (220, 210, 130),
            WATER: (60, 120, 220),
            GOLD: (255, 215, 0),
            DIAMOND: (0, 240, 255),
            RADIOACTIVE_SOIL: (110, 255, 110),
            ASH: (70, 70, 70),
            NUCLEAR_WASTE: (50, 255, 0),
            WOOD: (139, 69, 19),
            LEAVES: (34, 139, 34),
        }

        color = color_map.get(tile_type, (255, 0, 255)) # Pink Block
        surface.fill(color)
        return surface
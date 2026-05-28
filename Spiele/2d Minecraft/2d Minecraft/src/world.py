



# src/world.py

import pygame
import random
from constants import TILE_SIZE, SCREEN_TILES_X, SCREEN_TILES_Y, ASSETS_DIR
import assets

# Tile IDs
TILE_AIR = 0
TILE_GRASS = 1
TILE_DIRT = 2

class World:
    def __init__(self, width=SCREEN_TILES_X, height=SCREEN_TILES_Y, theme="grassland"):
        self.width = width
        self.height = height
        self.theme = theme
        self.tiles = [[TILE_AIR for _ in range(width)] for _ in range(height)]
        self._load_textures()
        self.generate_terrain()

    def _load_textures(self):
        self.tex_grass = assets.load_tile("grass", TILE_SIZE, ASSETS_DIR)
        self.tex_dirt = assets.load_tile("dirt", TILE_SIZE, ASSETS_DIR)
        # Fallback simple colored tiles if placeholder detected
        if self.tex_grass.get_at((0,0)) == (200,50,200,255):
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill((80, 180, 80))
            self.tex_grass = surf
        if self.tex_dirt.get_at((0,0)) == (200,50,200,255):
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill((120, 80, 40))
            self.tex_dirt = surf

    def generate_terrain(self):
        """Erzeuge eine geglättete Zufalls-Höhenlinie (Grassland) und fülle Gras/Boden."""
        base = int(self.height * 0.55)
        heights = [base] * self.width

        # Erzeuge initialen Random-Walk mit gelegentlichen größeren Hügeln/Tälern
        for x in range(1, self.width):
            step = random.choice([-2, -1, 0, 1, 2])
            # seltener größere Änderung
            if random.random() < 0.08:
                step += random.choice([-2, 2])
            heights[x] = max(2, min(self.height - 3, heights[x-1] + step))

        # Glätten (mehrfache Moving-Average-Pässe)
        for _ in range(3):
            new = heights.copy()
            for i in range(self.width):
                left = heights[i-1] if i-1 >= 0 else heights[i]
                right = heights[i+1] if i+1 < self.width else heights[i]
                new[i] = int((left + heights[i] + right) / 3)
            heights = new

        # Optional: kleine Täler oder Hügel nachbearbeiten (fügt Variation)
        for i in range(self.width):
            if random.random() < 0.03:
                heights[i] = max(2, heights[i] + random.choice([-2, 2]))

        # Fülle Tiles: oberste sichtbare Reihe = GRASS, darunter mehrere Reihen = DIRT
        for x in range(self.width):
            g = heights[x]
            for y in range(self.height):
                if y < g:
                    self.tiles[y][x] = TILE_AIR
                elif y == g:
                    self.tiles[y][x] = TILE_GRASS
                else:
                    self.tiles[y][x] = TILE_DIRT

        # Sicherstellen, dass untere Zeile immer Dirt ist (Rand)
        for x in range(self.width):
            self.tiles[self.height - 1][x] = TILE_DIRT

    def in_bounds(self, tx, ty):
        return 0 <= tx < self.width and 0 <= ty < self.height

    def get_tile(self, tx, ty):
        if not self.in_bounds(tx, ty):
            return TILE_AIR
        return self.tiles[ty][tx]

    def set_tile(self, tx, ty, tile_id):
        if not self.in_bounds(tx, ty):
            return False
        self.tiles[ty][tx] = tile_id
        return True

    def is_solid(self, tx, ty):
        """True wenn Tilesolid (nicht AIR)."""
        if not self.in_bounds(tx, ty):
            return False
        return self.tiles[ty][tx] != TILE_AIR

    def surface_y(self, tx):
        """Gibt y-Index der Oberfläche (grass) für x zurück oder None."""
        if not (0 <= tx < self.width):
            return None
        for y in range(self.height):
            if self.tiles[y][tx] == TILE_GRASS:
                return y
        return None

    def draw(self, surface):
        # draw tiles; sky wird in main gezeichnet
        for y in range(self.height):
            for x in range(self.width):
                t = self.tiles[y][x]
                px, py = x * TILE_SIZE, y * TILE_SIZE
                if t == TILE_AIR:
                    continue
                if t == TILE_GRASS:
                    surface.blit(self.tex_grass, (px, py))
                elif t == TILE_DIRT:
                    surface.blit(self.tex_dirt, (px, py))

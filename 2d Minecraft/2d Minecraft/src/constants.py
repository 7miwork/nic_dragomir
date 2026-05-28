# src/constants.py

SCREEN_TILES_X = 25
SCREEN_TILES_Y = 18
TILE_SIZE = 32
SCREEN_WIDTH = SCREEN_TILES_X * TILE_SIZE
SCREEN_HEIGHT = SCREEN_TILES_Y * TILE_SIZE
FPS = 60
ASSETS_DIR = "assets"

# Block Types
DIRT = "dirt"
GRASS = "grass"
WOOD = "wood"
STONE = "stone"
GRAVEL = "gravel"
SAND = "sand"
WATER = "water"
GOLD = "gold"
DIAMOND = "diamond"
RADIOACTIVE_SOIL = "radioactive_soil"
ASH = "ash"
NUCLEAR_BOMB = "nuclear_bomb"
NUCLEAR_WASTE = "nuclear_waste"
APPLE = "apple"
MUSHROOM = "mushroom"
NUCLEAR_FISH = "nuclear_fish"
GOLD_SUSHI = "gold_sushi"
PORTAL_ACTIVATOR = "portal_activator"

# Colors (Fallback if images missing)
COLORS = {
    DIRT: (139, 69, 19),
    GRASS: (34, 139, 34),
    WOOD: (160, 82, 45),
    STONE: (128, 128, 128),
    APPLE: (255, 0, 0),
    MUSHROOM: (255, 0, 255),
    PORTAL_ACTIVATOR: (0, 0, 255),
}

# src/items.py

class Item:
    def __init__(self, name, image=None):
        self.name = name
        self.image = image or self.load_default_image(name)

    def load_default_image(self, name):
        """Platzhalter fuer Itembilder."""
        surface = pygame.Surface((24, 24))
        
        color_map = {
            APPLE: (255, 0, 0),
            MUSHROOM: (200, 100, 200),
            GOLD: (255, 215, 0),
            DIAMOND: (0, 255, 255),
            NUCLEAR_FISH: (0, 255, 100),
            GOLD_SUSHI: (255, 255, 150),
            PORTAL_ACTIVATOR: (200, 0, 255),
            NUCLEAR_BOMB: (50, 50, 50),
            NUCLEAR_WASTE: (0, 255, 0),
            MINI_CAR: (0, 0, 255),
            NUCLEAR_MEAT: (150, 0, 0),
            SANDWICH: (255, 200, 100),
            FISH: (0, 150, 255),
        }
        
        color = color_map.get(name, (255, 0, 255))  # Pinke = Unbekannt
        surface.fill(color)
        return surface
    
# Beispiel Registrierung von Items
ITEM_REGISTRY = {
    DIRT: Item(DIRT),
    GRASS: Item(GRASS),
    WOOD: Item(WOOD),
    STONE: Item(STONE),
    GRAVEL: Item(GRAVEL),
    SAND: Item(SAND),
    WATER: Item(WATER),
    GOLD: Item(GOLD),
    DIAMOND: Item(DIAMOND),
    RADIOACTIVE_SOIL: Item(RADIOACTIVE_SOIL),
    ASH: Item(ASH),
    NUCLEAR_BOMB: Item(NUCLEAR_BOMB),
    NUCLEAR_WASTE: Item(NUCLEAR_WASTE),
    APPLE: Item(APPLE),
    MUSHROOM: Item(MUSHROOM),
    NUCLEAR_FISH: Item(NUCLEAR_FISH),
    GOLD_SUSHI: Item(GOLD_SUSHI),
    PORTAL_ACTIVATOR: Item(PORTAL_ACTIVATOR),
}
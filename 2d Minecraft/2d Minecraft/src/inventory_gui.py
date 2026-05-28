# src/inventory_gui.py

import pygame
from constants import TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from world import TILE_GRASS, TILE_DIRT

class InventoryGUI:
    def __init__(self, player):
        self.player = player
        self.font = None
        self.selected_tile = TILE_GRASS

    def draw(self, screen):
        if self.font is None:
            self.font = pygame.font.Font(None, 20)
        # Einfaches Inventar-Panel unten
        h = TILE_SIZE + 10
        rect = pygame.Rect(5, SCREEN_HEIGHT - h - 5, SCREEN_WIDTH - 10, h)
        pygame.draw.rect(screen, (30,30,30), rect)
        pygame.draw.rect(screen, (200,200,200), rect, 2)
        txt = f"Player tile pos: ({self.player.x//TILE_SIZE}, {self.player.y//TILE_SIZE})"
        surf = self.font.render(txt, True, (220,220,220))
        screen.blit(surf, (rect.x + 8, rect.y + 8))

        # Selected block preview
        preview_rect = pygame.Rect(rect.right - 100, rect.y + 6, TILE_SIZE, TILE_SIZE)
        if self.selected_tile == TILE_GRASS:
            color = (80,180,80)
            label = "Grass (1)"
        else:
            color = (120,80,40)
            label = "Dirt (2)"
        pygame.draw.rect(screen, color, preview_rect)
        pygame.draw.rect(screen, (255,255,255), preview_rect, 2)
        label_s = self.font.render(label, True, (220,220,220))
        screen.blit(label_s, (preview_rect.x - 80, preview_rect.y + (TILE_SIZE//2 - 8)))

    def update(self, screen):
        self.draw(screen)
        pygame.display.flip()
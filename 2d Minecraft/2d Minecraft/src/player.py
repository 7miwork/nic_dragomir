# src/player.py

import pygame
import math
from constants import TILE_SIZE
from world import TILE_AIR

GRAVITY = 1000    # pixels/s^2
MOVE_SPEED = 140  # pixels/s
JUMP_SPEED = 360  # pixels/s

class Player:
    def __init__(self, tile_x=5, tile_y=5):
        # position in pixels (top-left)
        self.w = TILE_SIZE
        self.h = TILE_SIZE
        self.x = tile_x * TILE_SIZE
        self.y = tile_y * TILE_SIZE
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self._make_sprite()

    def _make_sprite(self):
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        surf.fill((50, 120, 220))
        pygame.draw.rect(surf, (255,255,255), surf.get_rect(), 2)
        self.sprite = surf

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def apply_input(self, left, right):
        self.vx = 0
        if left:
            self.vx = -MOVE_SPEED
        if right:
            self.vx = MOVE_SPEED

    def jump(self):
        if self.on_ground:
            self.vy = -JUMP_SPEED
            self.on_ground = False

    def update(self, dt, world):
        # dt in seconds
        # apply gravity
        self.vy += GRAVITY * dt

        # desired movement
        dx = self.vx * dt
        dy = self.vy * dt

        # move horizontally and resolve collisions
        self._move_axis(dx, 0, world)
        # move vertically and resolve collisions
        self._move_axis(0, dy, world)

    def _tiles_overlapping(self, rect):
        left = rect.left // TILE_SIZE
        right = (rect.right - 1) // TILE_SIZE
        top = rect.top // TILE_SIZE
        bottom = (rect.bottom - 1) // TILE_SIZE
        tiles = []
        for tx in range(left, right + 1):
            for ty in range(top, bottom + 1):
                tiles.append((tx, ty))
        return tiles

    def _move_axis(self, dx, dy, world):
        rect = self.rect()
        rect.x += int(round(dx))
        rect.y += int(round(dy))

        collided = False
        for tx, ty in self._tiles_overlapping(rect):
            if world.is_solid(tx, ty):
                collided = True
                if dx > 0:  # moving right, place player to left of block
                    rect.right = tx * TILE_SIZE
                elif dx < 0:  # moving left
                    rect.left = (tx + 1) * TILE_SIZE
                elif dy > 0:  # moving down, place player on top
                    rect.bottom = ty * TILE_SIZE
                    self.vy = 0
                    self.on_ground = True
                elif dy < 0:  # moving up, hit head
                    rect.top = (ty + 1) * TILE_SIZE
                    self.vy = 0
        if not collided and dy != 0:
            # if we moved vertically and no collision, not grounded
            self.on_ground = False

        # commit
        self.x = rect.x
        self.y = rect.y

    def draw(self, surface):
        surface.blit(self.sprite, (int(self.x), int(self.y)))

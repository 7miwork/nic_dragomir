from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from core.inventory import Inventory
from core.constants import (
    GRAVITY,
    LIQUID_GRAVITY_MULTIPLIER,
    LIQUID_JUMP_MULTIPLIER,
    LIQUID_MOVE_MULTIPLIER,
    MAX_FALL_SPEED,
    PLAYER_HEIGHT,
    PLAYER_JUMP_SPEED,
    PLAYER_MAX_HP,
    PLAYER_MOVE_SPEED,
    PLAYER_WIDTH,
)


@dataclass
class Player:
    rect: pygame.Rect
    vel_x: float = 0.0
    vel_y: float = 0.0
    on_ground: bool = False
    in_liquid: bool = False
    max_hp: int = PLAYER_MAX_HP
    hp: float = float(PLAYER_MAX_HP)
    inventory: Inventory = field(default_factory=Inventory)

    @classmethod
    def at_spawn(cls, spawn_pixel_x: int, spawn_pixel_y: int) -> "Player":
        rect = pygame.Rect(spawn_pixel_x, spawn_pixel_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        return cls(rect=rect)

    @property
    def center(self) -> tuple[float, float]:
        return float(self.rect.centerx), float(self.rect.centery)

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        move_dir = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_dir -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_dir += 1

        move_speed = PLAYER_MOVE_SPEED
        if self.in_liquid:
            move_speed *= LIQUID_MOVE_MULTIPLIER

        self.vel_x = move_dir * move_speed

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            jump_speed = PLAYER_JUMP_SPEED
            if self.in_liquid:
                jump_speed *= LIQUID_JUMP_MULTIPLIER

            self.vel_y = -jump_speed
            self.on_ground = False

    def apply_gravity(self, dt: float) -> None:
        gravity = GRAVITY
        if self.in_liquid:
            gravity *= LIQUID_GRAVITY_MULTIPLIER

        self.vel_y += gravity * dt
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

    def take_damage(self, amount: float) -> None:
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def move_and_collide(self, dt: float, solid_rects: list[pygame.Rect]) -> None:
        self.rect.x += int(self.vel_x * dt)
        for tile_rect in solid_rects:
            if self.rect.colliderect(tile_rect):
                if self.vel_x > 0:
                    self.rect.right = tile_rect.left
                elif self.vel_x < 0:
                    self.rect.left = tile_rect.right

        self.rect.y += int(self.vel_y * dt)
        self.on_ground = False
        for tile_rect in solid_rects:
            if self.rect.colliderect(tile_rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile_rect.top
                    self.vel_y = 0.0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = tile_rect.bottom
                    self.vel_y = 0.0

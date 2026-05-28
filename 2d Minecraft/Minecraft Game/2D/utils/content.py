from __future__ import annotations

import pygame

from core.constants import TILE_SIZE
from core.items import Item
from core.mobs import Mob


def build_world_content(world_id: str) -> tuple[list[Mob], list[Item]]:
    mobs: list[Mob] = []
    items: list[Item] = []

    if world_id == "grassland":
        mobs.append(Mob("slime", pygame.Rect(12 * TILE_SIZE, 14 * TILE_SIZE, 24, 18), (30, 180, 60), 70.0, 4.0))
        items.append(Item("apple", pygame.Rect(20 * TILE_SIZE, 13 * TILE_SIZE, 16, 16), (220, 40, 40)))

    elif world_id == "stoneworld":
        mobs.append(Mob("rock_golem", pygame.Rect(18 * TILE_SIZE, 14 * TILE_SIZE, 26, 30), (90, 90, 90), 55.0, 8.0))
        items.append(Item("stone_pickaxe", pygame.Rect(6 * TILE_SIZE, 13 * TILE_SIZE, 16, 16), (170, 170, 170)))

    elif world_id == "waterworld":
        mobs.append(Mob("piranha", pygame.Rect(18 * TILE_SIZE, 14 * TILE_SIZE, 22, 14), (240, 240, 255), 90.0, 10.0))
        items.append(Item("water_boots", pygame.Rect(8 * TILE_SIZE, 13 * TILE_SIZE, 16, 16), (50, 90, 220)))

    elif world_id == "lavaworld":
        mobs.append(Mob("fire_imp", pygame.Rect(15 * TILE_SIZE, 14 * TILE_SIZE, 20, 22), (220, 80, 40), 85.0, 12.0))
        items.append(Item("fire_resist", pygame.Rect(7 * TILE_SIZE, 13 * TILE_SIZE, 16, 16), (255, 170, 60)))

    elif world_id == "richworld":
        mobs.append(Mob("miner", pygame.Rect(22 * TILE_SIZE, 14 * TILE_SIZE, 22, 30), (160, 110, 70), 60.0, 6.0))
        items.append(Item("coin", pygame.Rect(30 * TILE_SIZE, 13 * TILE_SIZE, 14, 14), (235, 205, 70)))
        items.append(Item("coin", pygame.Rect(34 * TILE_SIZE, 13 * TILE_SIZE, 14, 14), (235, 205, 70)))

    elif world_id == "nukeworld":
        mobs.append(Mob("mutant", pygame.Rect(20 * TILE_SIZE, 14 * TILE_SIZE, 26, 30), (70, 120, 70), 75.0, 10.0))
        items.append(Item("gas_mask", pygame.Rect(6 * TILE_SIZE, 13 * TILE_SIZE, 16, 16), (40, 40, 40)))

    return mobs, items

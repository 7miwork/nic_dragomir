from __future__ import annotations

from dataclasses import dataclass

from core.constants import (
    SOLID_TILES,
    TILE_DIRT,
    TILE_EMPTY,
    TILE_GRASS,
    TILE_LAVA,
    TILE_NUKE,
    TILE_ORE,
    TILE_PORTAL,
    TILE_STONE,
    TILE_WATER,
)


@dataclass(frozen=True)
class BlockDrop:
    tile: str
    item_id: str
    amount: int = 1


TILE_TO_ITEM_DROP: dict[str, BlockDrop] = {
    TILE_GRASS: BlockDrop(TILE_GRASS, "grass_block", 1),
    TILE_DIRT: BlockDrop(TILE_DIRT, "dirt_block", 1),
    TILE_STONE: BlockDrop(TILE_STONE, "stone_block", 1),
    TILE_ORE: BlockDrop(TILE_ORE, "ore_chunk", 1),
    TILE_NUKE: BlockDrop(TILE_NUKE, "nuke_chunk", 1),
    TILE_PORTAL: BlockDrop(TILE_PORTAL, "portal_block", 1),
}


ITEM_TO_PLACE_TILE: dict[str, str] = {
    "grass_block": TILE_GRASS,
    "dirt_block": TILE_DIRT,
    "stone_block": TILE_STONE,
    "portal_block": TILE_PORTAL,
}


def is_breakable(tile: str) -> bool:
    if tile == TILE_EMPTY:
        return False
    if tile == TILE_WATER:
        return True
    if tile == TILE_LAVA:
        return True
    if tile == TILE_PORTAL:
        return True
    return tile in SOLID_TILES


def drop_for_tile(tile: str) -> BlockDrop | None:
    return TILE_TO_ITEM_DROP.get(tile)


def is_placeable(tile: str) -> bool:
    return tile != TILE_EMPTY

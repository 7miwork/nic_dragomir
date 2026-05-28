from __future__ import annotations

from typing import Callable

from worlds.grassland import GrasslandWorld
from worlds.lavaworld import LavaWorld
from worlds.nukeworld import NukeWorld
from worlds.richworld import RichWorld
from worlds.stoneworld import StoneWorld
from worlds.waterworld import WaterWorld
from worlds.base_world import BaseWorld


def get_world_factories() -> dict[str, Callable[[], BaseWorld]]:
    return {
        "grassland": GrasslandWorld,
        "stoneworld": StoneWorld,
        "waterworld": WaterWorld,
        "lavaworld": LavaWorld,
        "richworld": RichWorld,
        "nukeworld": NukeWorld,
    }


def load_world(world_id: str) -> BaseWorld:
    factories = get_world_factories()
    if world_id not in factories:
        raise KeyError(f"Unknown world_id: {world_id}")
    return factories[world_id]()

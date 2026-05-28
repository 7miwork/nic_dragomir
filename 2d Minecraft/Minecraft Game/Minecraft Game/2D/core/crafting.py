from __future__ import annotations

from dataclasses import dataclass

from core.inventory import Inventory


@dataclass(frozen=True)
class Recipe:
    recipe_id: str
    name: str
    inputs: dict[str, int]
    output_item_id: str
    output_amount: int = 1


def get_recipes() -> list[Recipe]:
    return [
        Recipe(
            "craft_portal_block",
            "Craft Portal Block",
            {"stone_block": 6, "ore_chunk": 2},
            "portal_block",
            1,
        ),
        Recipe(
            "key_stone",
            "Portal Activator: StoneWorld",
            {"grass_block": 4, "dirt_block": 4},
            "portal_key_stoneworld",
            1,
        ),
        Recipe(
            "key_water",
            "Portal Activator: WaterWorld",
            {"stone_block": 6, "ore_chunk": 1},
            "portal_key_waterworld",
            1,
        ),
        Recipe(
            "key_lava",
            "Portal Activator: LavaWorld",
            {"stone_block": 8, "ore_chunk": 3},
            "portal_key_lavaworld",
            1,
        ),
        Recipe(
            "key_rich",
            "Portal Activator: RichWorld",
            {"stone_block": 10, "ore_chunk": 6},
            "portal_key_richworld",
            1,
        ),
        Recipe(
            "key_nuke",
            "Portal Activator: NukeWorld",
            {"coin": 6, "ore_chunk": 3},
            "portal_key_nukeworld",
            1,
        ),
        Recipe(
            "key_grass",
            "Portal Activator: Grassland",
            {"stone_block": 4},
            "portal_key_grassland",
            1,
        ),
    ]


def can_craft(inventory: Inventory, recipe: Recipe) -> bool:
    for item_id, amount in recipe.inputs.items():
        if inventory.count(item_id) < amount:
            return False
    return True


def craft(inventory: Inventory, recipe: Recipe) -> bool:
    if not can_craft(inventory, recipe):
        return False

    for item_id, amount in recipe.inputs.items():
        if not inventory.remove(item_id, amount):
            return False

    inventory.add(recipe.output_item_id, recipe.output_amount)
    return True

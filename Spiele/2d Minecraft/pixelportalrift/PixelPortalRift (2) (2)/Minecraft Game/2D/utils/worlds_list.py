WORLD_IDS: list[str] = [
    "grassland",
    "stoneworld",
    "waterworld",
    "lavaworld",
    "richworld",
    "nukeworld",
]

WORLD_NAMES: dict[str, str] = {
    "grassland": "Grassland",
    "stoneworld": "StoneWorld",
    "waterworld": "WaterWorld",
    "lavaworld": "LavaWorld",
    "richworld": "RichWorld",
    "nukeworld": "NukeWorld",
}


def portal_key_for_world(world_id: str) -> str:
    return f"portal_key_{world_id}"

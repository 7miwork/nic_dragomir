from __future__ import annotations

from dataclasses import dataclass, field

import pygame

import config
from core.camera import Camera
from core.blocks import ITEM_TO_PLACE_TILE, drop_for_tile, is_breakable
from core.constants import (
    CAMERA_LERP,
    HAZARD_DAMAGE_PER_SECOND,
    HAZARD_TILES,
    INTERACTION_RANGE_TILES,
    LIQUID_TILES,
    TILE_LAVA,
    TILE_EMPTY,
    TILE_NUKE,
    TILE_PORTAL,
    TILE_SIZE,
    TILE_WATER,
)
from core.crafting import can_craft, craft, get_recipes
from core.items import Item
from core.mobs import Mob
from core.particles import ParticleSystem
from core.player import Player
from utils.content import build_world_content
from utils.loader import load_world
from utils.worlds_list import WORLD_IDS, portal_key_for_world
from worlds.base_world import BaseWorld


@dataclass
class Scene:
    world_id: str
    world: BaseWorld
    tilemap: list[list[str]]
    player: Player
    camera: Camera
    mobs: list[Mob]
    items: list[Item]
    solid_rects: list[pygame.Rect]

    crafting_open: bool = False
    crafting_ui_lines: list[str] = field(default_factory=list)

    status_message: str = ""
    _status_timer: float = 0.0

    _place_items: list[str] = field(default_factory=lambda: ["dirt_block", "stone_block", "grass_block", "portal_block"])
    _selected_place_index: int = 0
    
    # Hotbar/Tools
    _equippable_items: list[str] = field(default_factory=lambda: ["stone_pickaxe", "wood_pickaxe", "shovel"])
    _selected_tool_index: int = 0
    current_tool: str = ""

    portal_target_world_id: str = "stoneworld"
    
    # Breaking/Mining
    current_breaking_tile: tuple[int, int] | None = None
    current_breaking_progress: float = 0.0
    breaking_duration: float = 0.5  # Default 0.5 seconds
    
    # Particles
    particle_system: ParticleSystem = field(default_factory=ParticleSystem)

    @classmethod
    def new(cls, world_id: str) -> "Scene":
        world = load_world(world_id)
        spawn_x, spawn_y = world.spawn_in_pixels()
        player = Player.at_spawn(spawn_x, spawn_y)
        camera = Camera()
        tilemap = [list(row) for row in world.tilemap]
        solid_rects = cls._build_solid_rects(tilemap)
        mobs, items = build_world_content(world_id)
        scene = cls(
            world_id=world_id,
            world=world,
            tilemap=tilemap,
            player=player,
            camera=camera,
            mobs=mobs,
            items=items,
            solid_rects=solid_rects,
        )
        scene._set_default_portal_target()
        scene._ensure_portal_exists()
        scene._refresh_crafting_ui()
        return scene

    def switch_world(self, world_id: str) -> None:
        inventory = self.player.inventory
        fresh = Scene.new(world_id)
        self.world_id = fresh.world_id
        self.world = fresh.world
        self.tilemap = fresh.tilemap
        self.player = fresh.player
        self.player.inventory = inventory
        self.camera = fresh.camera
        self.mobs = fresh.mobs
        self.items = fresh.items
        self.solid_rects = fresh.solid_rects
        self.particle_system = fresh.particle_system

        self.crafting_open = False
        self._set_default_portal_target()
        self._refresh_crafting_ui()

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        self.player.handle_input(keys)
        
        # Check for continuous breaking while mouse is held
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Left mouse button
            tx, ty = self._mouse_to_tile()
            if self.current_breaking_tile != (tx, ty):
                self.current_breaking_tile = (tx, ty)
                self.current_breaking_progress = 0.0
            self._try_break_at_mouse()

    @property
    def selected_place_item(self) -> str:
        if not self._place_items:
            return ""
        return self._place_items[self._selected_place_index % len(self._place_items)]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                self.crafting_open = not self.crafting_open
                self._refresh_crafting_ui()
                self._set_status("Crafting opened" if self.crafting_open else "Crafting closed")
                return

            if event.key == pygame.K_q:
                self._cycle_place(-1)
            elif event.key == pygame.K_e:
                self._cycle_place(1)
            elif event.key == pygame.K_t:
                self._cycle_tool(-1)
            elif event.key == pygame.K_y:
                self._cycle_tool(1)
            elif event.key == pygame.K_r:
                self._cycle_portal_target()
            elif event.key == pygame.K_f:
                self._try_use_portal()

            if self.crafting_open:
                self._handle_crafting_key(event.key)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Start breaking
                tx, ty = self._mouse_to_tile()
                self.current_breaking_tile = (tx, ty)
                self.current_breaking_progress = 0.0
            elif event.button == 3:
                self._try_place_at_mouse()
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                # Stop breaking
                self.current_breaking_tile = None
                self.current_breaking_progress = 0.0

    def update(self, dt: float) -> None:
        if self._status_timer > 0:
            self._status_timer -= dt
            if self._status_timer <= 0:
                self.status_message = ""

        if self.player.hp <= 0:
            self._respawn()
            return

        # Update particles
        self.particle_system.update(dt)

        # Update breaking progress
        if self.current_breaking_tile is not None:
            # Check if tile is still valid
            tx, ty = self.current_breaking_tile
            if self._tile_in_bounds(tx, ty) and is_breakable(self._get_tile(tx, ty)):
                self.current_breaking_progress += dt / self.breaking_duration
                
                if self.current_breaking_progress >= 1.0:
                    # Block is broken!
                    tile = self._get_tile(tx, ty)
                    
                    # Get tile color for particles
                    from core.constants import (
                        COLOR_GRASS, COLOR_DIRT, COLOR_STONE, COLOR_ORE, 
                        COLOR_NUKE, COLOR_LAVA, COLOR_WATER, TILE_GRASS, TILE_DIRT,
                        TILE_STONE, TILE_ORE, TILE_NUKE, TILE_LAVA, TILE_WATER
                    )
                    
                    tile_color_map = {
                        TILE_GRASS: COLOR_GRASS,
                        TILE_DIRT: COLOR_DIRT,
                        TILE_STONE: COLOR_STONE,
                        TILE_ORE: COLOR_ORE,
                        TILE_NUKE: COLOR_NUKE,
                        TILE_LAVA: COLOR_LAVA,
                        TILE_WATER: COLOR_WATER,
                    }
                    
                    tile_color = tile_color_map.get(tile, (200, 200, 200))
                    self.particle_system.emit_block_break(tx * TILE_SIZE, ty * TILE_SIZE, tile_color, 12)
                    
                    drop = drop_for_tile(tile)
                    self._set_tile(tx, ty, TILE_EMPTY)
                    if drop is not None:
                        self.player.inventory.add(drop.item_id, drop.amount)
                        if self.crafting_open:
                            self._refresh_crafting_ui()
                    self._rebuild_solids()
                    self._set_status(f"Broke {tile}")
                    self.current_breaking_tile = None
                    self.current_breaking_progress = 0.0
            else:
                self.current_breaking_tile = None
                self.current_breaking_progress = 0.0

        self.player.apply_gravity(dt)
        self.player.move_and_collide(dt, self.solid_rects)

        for mob in self.mobs:
            mob.update(dt, self.solid_rects, self.player.rect)
            if mob.touches_player(self.player.rect):
                self.player.take_damage(mob.damage_per_second * dt)

        remaining_items: list[Item] = []
        for item in self.items:
            if item.try_pickup(self.player.rect):
                self.player.inventory.add(item.item_id)
                if self.crafting_open:
                    self._refresh_crafting_ui()
            else:
                remaining_items.append(item)
        self.items = remaining_items

        self._apply_tile_effects(dt)

        if self.player.hp <= 0:
            self._respawn()
            return

        cx, cy = self.player.center
        self.camera.update(
            target_x=cx,
            target_y=cy,
            screen_width=config.SCREEN_WIDTH,
            screen_height=config.SCREEN_HEIGHT,
            world_pixel_width=self.world.width_in_pixels,
            world_pixel_height=self.world.height_in_pixels,
            lerp=CAMERA_LERP,
        )

    def _apply_tile_effects(self, dt: float) -> None:
        tile_x = int(self.player.rect.centerx // TILE_SIZE)
        tile_y = int(self.player.rect.centery // TILE_SIZE)
        if tile_y < 0 or tile_y >= self.world.height_in_tiles:
            return
        row = self.tilemap[tile_y]
        if tile_x < 0 or tile_x >= len(row):
            return

        ch = row[tile_x]

        if ch in LIQUID_TILES:
            self.player.in_liquid = True
            if ch == TILE_WATER and self.player.inventory.has("water_boots"):
                self.player.in_liquid = False
        else:
            self.player.in_liquid = False

        if ch in HAZARD_TILES:
            if ch == TILE_LAVA and self.player.inventory.has("fire_resist"):
                return
            if ch == TILE_NUKE and self.player.inventory.has("gas_mask"):
                return
            self.player.take_damage(HAZARD_DAMAGE_PER_SECOND * dt)

    def _respawn(self) -> None:
        spawn_x, spawn_y = self.world.spawn_in_pixels()
        self.player.rect.x = spawn_x
        self.player.rect.y = spawn_y
        self.player.vel_x = 0.0
        self.player.vel_y = 0.0
        self.player.hp = float(self.player.max_hp)
        self._set_status("Respawned")

    @staticmethod
    def _build_solid_rects(tilemap: list[list[str]]) -> list[pygame.Rect]:
        from core.constants import SOLID_TILES

        solids: list[pygame.Rect] = []
        for y, row in enumerate(tilemap):
            for x, ch in enumerate(row):
                if ch in SOLID_TILES:
                    solids.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return solids

    def _rebuild_solids(self) -> None:
        self.solid_rects = self._build_solid_rects(self.tilemap)

    def _cycle_place(self, direction: int) -> None:
        if not self._place_items:
            return
        self._selected_place_index = (self._selected_place_index + direction) % len(self._place_items)
        self._set_status(f"Selected: {self.selected_place_item}")

    def _cycle_tool(self, direction: int) -> None:
        if not self._equippable_items:
            return
        self._selected_tool_index = (self._selected_tool_index + direction) % len(self._equippable_items)
        self.current_tool = self._equippable_items[self._selected_tool_index]
        if self.player.inventory.has(self.current_tool):
            self._set_status(f"Equipped: {self.current_tool}")
        else:
            self._set_status(f"Don't have: {self.current_tool}")

    def _set_default_portal_target(self) -> None:
        if self.world_id in WORLD_IDS:
            idx = WORLD_IDS.index(self.world_id)
            self.portal_target_world_id = WORLD_IDS[(idx + 1) % len(WORLD_IDS)]
        else:
            self.portal_target_world_id = WORLD_IDS[0]

    def _cycle_portal_target(self) -> None:
        if self.portal_target_world_id not in WORLD_IDS:
            self.portal_target_world_id = WORLD_IDS[0]
            return
        idx = WORLD_IDS.index(self.portal_target_world_id)
        self.portal_target_world_id = WORLD_IDS[(idx + 1) % len(WORLD_IDS)]
        self._set_status(f"Portal target: {self.portal_target_world_id}")

    def _set_status(self, text: str, duration: float = 1.8) -> None:
        self.status_message = text
        self._status_timer = duration

    def _mouse_to_tile(self) -> tuple[int, int]:
        mx, my = pygame.mouse.get_pos()
        world_x = mx + int(self.camera.x)
        world_y = my + int(self.camera.y)
        return int(world_x // TILE_SIZE), int(world_y // TILE_SIZE)

    def _in_range(self, tx: int, ty: int) -> bool:
        px = int(self.player.rect.centerx // TILE_SIZE)
        py = int(self.player.rect.centery // TILE_SIZE)
        return abs(tx - px) + abs(ty - py) <= INTERACTION_RANGE_TILES

    def _get_tile(self, tx: int, ty: int) -> str:
        if ty < 0 or ty >= len(self.tilemap):
            return TILE_EMPTY
        row = self.tilemap[ty]
        if tx < 0 or tx >= len(row):
            return TILE_EMPTY
        return row[tx]

    def _tile_in_bounds(self, tx: int, ty: int) -> bool:
        if ty < 0 or ty >= len(self.tilemap):
            return False
        row = self.tilemap[ty]
        if tx < 0 or tx >= len(row):
            return False
        return True

    def _set_tile(self, tx: int, ty: int, ch: str) -> None:
        self.tilemap[ty][tx] = ch

    def _try_break_at_mouse(self) -> None:
        tx, ty = self._mouse_to_tile()
        if not self._in_range(tx, ty):
            return

        if not self._tile_in_bounds(tx, ty):
            return

        tile = self._get_tile(tx, ty)
        if not is_breakable(tile):
            self.current_breaking_tile = None
            self.current_breaking_progress = 0.0
            return

        # Breaking-Zeit je nach Material
        base_duration = 0.5
        if tile == TILE_STONE:
            base_duration = 1.2
        elif tile == TILE_ORE:
            base_duration = 2.5
        elif tile == TILE_NUKE:
            base_duration = 3.0
        
        # Tool multiplier
        tool_multiplier = 1.0
        if self.player.inventory.has("stone_pickaxe"):
            tool_multiplier = 0.5  # 50% faster
        elif self.player.inventory.has("wood_pickaxe"):
            tool_multiplier = 0.7  # 30% faster
        elif self.player.inventory.has("shovel"):
            if tile in [TILE_DIRT, TILE_GRASS]:
                tool_multiplier = 0.4  # 60% faster for dirt/grass
        
        self.breaking_duration = base_duration * tool_multiplier

    def _try_place_at_mouse(self) -> None:
        tx, ty = self._mouse_to_tile()
        if not self._in_range(tx, ty):
            self._set_status("Too far")
            return

        if not self._tile_in_bounds(tx, ty):
            return

        if self._get_tile(tx, ty) != TILE_EMPTY:
            return

        item_id = self.selected_place_item
        if item_id not in ITEM_TO_PLACE_TILE:
            return

        if not self.player.inventory.remove(item_id, 1):
            self._set_status(f"Missing: {item_id}")
            return

        if self.crafting_open:
            self._refresh_crafting_ui()

        place_tile = ITEM_TO_PLACE_TILE[item_id]

        world_rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if world_rect.colliderect(self.player.rect):
            self.player.inventory.add(item_id, 1)
            return

        # Get tile color for particles
        from core.constants import (
            COLOR_GRASS, COLOR_DIRT, COLOR_STONE, COLOR_PORTAL, 
            TILE_GRASS, TILE_DIRT, TILE_STONE, TILE_PORTAL
        )
        
        tile_color_map = {
            TILE_GRASS: COLOR_GRASS,
            TILE_DIRT: COLOR_DIRT,
            TILE_STONE: COLOR_STONE,
            TILE_PORTAL: COLOR_PORTAL,
        }
        
        tile_color = tile_color_map.get(place_tile, (200, 200, 200))
        self.particle_system.emit_place_block(tx * TILE_SIZE, ty * TILE_SIZE, tile_color)
        
        self._set_tile(tx, ty, place_tile)
        self._rebuild_solids()
        self._set_status(f"Placed {place_tile}")

    def _ensure_portal_exists(self) -> None:
        for row in self.tilemap:
            if TILE_PORTAL in row:
                return

        sx, sy = self.world.spawn_point
        py = min(max(sy, 0), len(self.tilemap) - 1)
        row = self.tilemap[py]
        px = min(max(sx + 2, 0), len(row) - 1)
        for dx in range(2, 10):
            cx = min(max(sx + dx, 0), len(row) - 1)
            if row[cx] == TILE_EMPTY:
                row[cx] = TILE_PORTAL
                break

    def _standing_on_portal(self) -> bool:
        tx = int(self.player.rect.centerx // TILE_SIZE)
        ty = int(self.player.rect.centery // TILE_SIZE)
        return self._get_tile(tx, ty) == TILE_PORTAL

    def _try_use_portal(self) -> None:
        if not self._standing_on_portal():
            self._set_status("Stand on a portal")
            return

        target = self.portal_target_world_id
        needed_key = portal_key_for_world(target)
        if not self.player.inventory.has(needed_key):
            self._set_status(f"Need activator: {needed_key}")
            return

        self.switch_world(target)
        self._set_status(f"Traveled to {target}")

    def _refresh_crafting_ui(self) -> None:
        recipes = get_recipes()
        lines: list[str] = []
        for recipe in recipes:
            ok = can_craft(self.player.inventory, recipe)
            parts = [f"{item_id}x{amount}" for item_id, amount in recipe.inputs.items()]
            need = " + ".join(parts)
            tag = "OK" if ok else "NO"
            lines.append(f"{recipe.name} [{need}] -> {recipe.output_item_id} ({tag})")
        self.crafting_ui_lines = lines

    def _handle_crafting_key(self, key: int) -> None:
        idx_map = {
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
            pygame.K_4: 3,
            pygame.K_5: 4,
            pygame.K_6: 5,
            pygame.K_7: 6,
            pygame.K_8: 7,
            pygame.K_9: 8,
        }
        if key not in idx_map:
            return

        recipes = get_recipes()
        idx = idx_map[key]
        if idx < 0 or idx >= len(recipes):
            return
        recipe = recipes[idx]
        if craft(self.player.inventory, recipe):
            self._set_status(f"Crafted: {recipe.output_item_id}")
        else:
            self._set_status("Not enough items")
        self._refresh_crafting_ui()

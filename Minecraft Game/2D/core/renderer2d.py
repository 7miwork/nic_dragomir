from __future__ import annotations

import pygame

import config
from core.constants import (
    COLOR_DIRT,
    COLOR_GRASS,
    COLOR_LAVA,
    COLOR_NUKE,
    COLOR_ORE,
    COLOR_PORTAL,
    COLOR_PLAYER,
    COLOR_STONE,
    COLOR_WATER,
    TILE_DIRT,
    TILE_GRASS,
    TILE_LAVA,
    TILE_NUKE,
    TILE_ORE,
    TILE_PORTAL,
    TILE_SIZE,
    TILE_STONE,
    TILE_WATER,
)
from core.scene import Scene
from utils.worlds_list import WORLD_NAMES
from utils.ui import Ui


class Renderer2D:
    def __init__(self, ui: Ui) -> None:
        self._ui = ui

    def draw(self, screen: pygame.Surface, scene: Scene, fps: int) -> None:
        screen.fill(getattr(scene.world, "background_color", (0, 0, 0)))
        self._draw_tiles(screen, scene)
        self._draw_items(screen, scene)
        self._draw_mobs(screen, scene)
        self._draw_player(screen, scene)
        self._draw_particles(screen, scene)
        self._draw_hud(screen, scene, fps)

    def _draw_tiles(self, screen: pygame.Surface, scene: Scene) -> None:
        start_x = int(scene.camera.x) // TILE_SIZE
        start_y = int(scene.camera.y) // TILE_SIZE
        end_x = (int(scene.camera.x) + config.SCREEN_WIDTH) // TILE_SIZE + 2
        end_y = (int(scene.camera.y) + config.SCREEN_HEIGHT) // TILE_SIZE + 2

        end_x = min(end_x, scene.world.width_in_tiles)
        end_y = min(end_y, scene.world.height_in_tiles)

        for ty in range(max(0, start_y), max(0, end_y)):
            row = scene.tilemap[ty]
            for tx in range(max(0, start_x), max(0, end_x)):
                ch = row[tx] if tx < len(row) else "."
                if ch == ".":
                    continue

                world_x = tx * TILE_SIZE
                world_y = ty * TILE_SIZE
                sx, sy = scene.camera.world_to_screen(world_x, world_y)
                rect = pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE)

                if ch == TILE_GRASS:
                    pygame.draw.rect(screen, COLOR_GRASS, rect)
                elif ch == TILE_DIRT:
                    pygame.draw.rect(screen, COLOR_DIRT, rect)
                elif ch == TILE_STONE:
                    pygame.draw.rect(screen, COLOR_STONE, rect)
                elif ch == TILE_WATER:
                    pygame.draw.rect(screen, COLOR_WATER, rect)
                elif ch == TILE_LAVA:
                    pygame.draw.rect(screen, COLOR_LAVA, rect)
                elif ch == TILE_ORE:
                    pygame.draw.rect(screen, COLOR_ORE, rect)
                elif ch == TILE_NUKE:
                    pygame.draw.rect(screen, COLOR_NUKE, rect)
                elif ch == TILE_PORTAL:
                    pygame.draw.rect(screen, COLOR_PORTAL, rect)

    def _draw_player(self, screen: pygame.Surface, scene: Scene) -> None:
        px, py = scene.camera.world_to_screen(scene.player.rect.x, scene.player.rect.y)
        pygame.draw.rect(screen, COLOR_PLAYER, pygame.Rect(px, py, scene.player.rect.width, scene.player.rect.height))

    def _draw_mobs(self, screen: pygame.Surface, scene: Scene) -> None:
        for mob in scene.mobs:
            mx, my = scene.camera.world_to_screen(mob.rect.x, mob.rect.y)
            pygame.draw.rect(screen, mob.color, pygame.Rect(mx, my, mob.rect.width, mob.rect.height))

    def _draw_items(self, screen: pygame.Surface, scene: Scene) -> None:
        for item in scene.items:
            ix, iy = scene.camera.world_to_screen(item.rect.x, item.rect.y)
            pygame.draw.rect(screen, item.color, pygame.Rect(ix, iy, item.rect.width, item.rect.height))

    def _draw_particles(self, screen: pygame.Surface, scene: Scene) -> None:
        scene.particle_system.draw(screen, scene.camera.x, scene.camera.y)

    def _draw_hud(self, screen: pygame.Surface, scene: Scene, fps: int) -> None:
        self._ui.draw_text(screen, f"World: {scene.world.name}", 10, 10)
        self._ui.draw_text(screen, f"FPS: {fps}", 10, 30)
        self._ui.draw_text(screen, f"HP: {int(scene.player.hp)}/{scene.player.max_hp}", 10, 50)
        
        # Hotbar & Tools
        if scene.current_tool:
            tool_status = "✓" if scene.player.inventory.has(scene.current_tool) else "✗"
            self._ui.draw_text(screen, f"[Tool: {scene.current_tool}] {tool_status} (T/Y to change)", 10, 70)
        
        # Platzierungs-Blöcke
        if scene.selected_place_item:
            self._ui.draw_text(screen, f"[Selected: {scene.selected_place_item}] (Q/E to change)", 10, 90)
        
        inv_preview = scene.player.inventory.snapshot_for_ui(6)
        self._ui.draw_text(screen, f"Inv: {inv_preview}", 10, 110)
        
        # Status message
        if scene.status_message:
            self._ui.draw_text(screen, f"> {scene.status_message}", 10, 130)
        
        # Crafting UI
        if scene.crafting_open:
            self._draw_crafting_menu(screen, scene)
        
        # Abbau-Fortschritt
        if scene.current_breaking_progress > 0:
            progress_bar = "█" * int(scene.current_breaking_progress * 20)
            self._ui.draw_text(screen, f"Breaking: {progress_bar} {int(scene.current_breaking_progress * 100)}%", 10, 150)
    
    def _draw_crafting_menu(self, screen: pygame.Surface, scene: Scene) -> None:
        start_x = config.SCREEN_WIDTH - 400
        start_y = 10
        menu_width = 390
        
        # Crafting Panel Background
        pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(start_x, start_y, menu_width, 500))
        pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(start_x, start_y, menu_width, 500), 2)
        
        self._ui.draw_text(screen, "CRAFTING RECIPES (Press 1-9)", start_x + 10, start_y + 5)
        
        y_offset = start_y + 25
        for i, line in enumerate(scene.crafting_ui_lines[:10]):
            color = (100, 255, 100) if "OK" in line else (255, 100, 100)
            text_color = (100, 255, 100) if "OK" in line else (200, 100, 100)
            
            # Draw recipe background
            pygame.draw.rect(screen, (40, 40, 40), pygame.Rect(start_x + 5, y_offset - 2, menu_width - 10, 18))
            
            # Display shortened version
            if len(line) > 50:
                short_line = line[:47] + "..."
            else:
                short_line = line
            
            self._ui.draw_text(screen, f"{i+1}: {short_line}", start_x + 10, y_offset)
            y_offset += 20

        selected = scene.selected_place_item
        self._ui.draw_text(screen, f"Build: {selected} (Q/E) | Break: LMB | Place: RMB", 10, 90)

        target = WORLD_NAMES.get(scene.portal_target_world_id, scene.portal_target_world_id)
        self._ui.draw_text(screen, f"Portal Target: {target} (R) | Use Portal: F", 10, 110)

        self._ui.draw_text(screen, "Crafting: C (toggle) | Craft: 1-9 when open | Worlds: 1-6 | Quit: Esc", 10, 130)

        if scene.crafting_open:
            y = 160
            for idx, line in enumerate(scene.crafting_ui_lines[:9], start=1):
                self._ui.draw_text(screen, f"{idx}. {line}", 10, y)
                y += 18

        if scene.status_message:
            self._ui.draw_text(screen, scene.status_message, 10, config.SCREEN_HEIGHT - 24)

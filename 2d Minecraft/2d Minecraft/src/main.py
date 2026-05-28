import sys
import os
import pygame

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import constants
from world import World, TILE_AIR, TILE_GRASS, TILE_DIRT
from player import Player
from engine import GameEngine
from inventory_gui import InventoryGUI

pygame.init()
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("2D Minecraft School Project")

clock = pygame.time.Clock()

world = World(constants.SCREEN_TILES_X, constants.SCREEN_TILES_Y, "grassland")
# spawn player on top of ground near center
spawn_x = world.width // 2
# find topmost solid tile in that column
for y in range(world.height):
    if world.is_solid(spawn_x, y):
        spawn_y = y - 1
        break
else:
    spawn_y = 5
player = Player(spawn_x, max(0, spawn_y))

engine = GameEngine(screen, world, player)
inventory_gui = InventoryGUI(player)

selected_tile = TILE_GRASS

running = True
while running:
    dt = clock.tick(constants.FPS) / 1000.0
    left = right = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            tx = mx // constants.TILE_SIZE
            ty = my // constants.TILE_SIZE
            # left click: remove block (abbauen)
            if event.button == 1:
                # don't remove tile player occupies
                player_tile_x = player.x // constants.TILE_SIZE
                player_tile_y = player.y // constants.TILE_SIZE
                if not (tx == player_tile_x and ty == player_tile_y):
                    world.set_tile(tx, ty, TILE_AIR)
            # right click: place selected
            elif event.button == 3:
                player_tile_x = player.x // constants.TILE_SIZE
                player_tile_y = player.y // constants.TILE_SIZE
                if not (tx == player_tile_x and ty == player_tile_y):
                    world.set_tile(tx, ty, selected_tile)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                selected_tile = TILE_GRASS
            elif event.key == pygame.K_2:
                selected_tile = TILE_DIRT
            elif event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP:
                player.jump()

        # keyup/down handled below by get_pressed

    keys = pygame.key.get_pressed()
    left = keys[pygame.K_a] or keys[pygame.K_LEFT]
    right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

    player.apply_input(left, right)
    player.update(dt, world)

    # draw: sky, world, player, GUI
    screen.fill((135, 206, 235))  # sky blue
    engine.draw_world()
    engine.draw_player()
    inventory_gui.selected_tile = selected_tile
    inventory_gui.draw(screen)

    pygame.display.flip()

pygame.quit()

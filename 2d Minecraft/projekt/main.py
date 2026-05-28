import pygame
import sys
from game.world import World
from game.player import Player
from config import SCREEN_WIDHT, SCREEN_HEIGHT, FRAME_RATE

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
    pygame.display.set_caption("2D Minecraft-style Game")

    clock = pygame.time.Clock()
    world = World()
    player = Player("Steve", world)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.Quit:
                pygame.quit()
                sys.exit()

        player.update()
        world.update()

        screen.fill((135, 206, 235))
        world.draw(screen)
        player.draw(screen)

        pygame.display.flip()
        clock.tick(FRAME_RATE)

if __name__ == "__main__":
    main()

    
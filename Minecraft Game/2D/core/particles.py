from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class Particle:
    x: float
    y: float
    vel_x: float
    vel_y: float
    lifetime: float
    max_lifetime: float
    color: tuple[int, int, int]
    size: int = 4

    def update(self, dt: float) -> bool:
        """Update particle. Returns True if still alive, False if dead."""
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """Draw particle with fade effect."""
        alpha = self.lifetime / self.max_lifetime
        size = int(self.size * alpha)
        if size > 0:
            screen_x = int(self.x - camera_x)
            screen_y = int(self.y - camera_y)
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), size)


class ParticleSystem:
    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def emit_block_break(self, x: float, y: float, color: tuple[int, int, int], count: int = 8) -> None:
        """Emit particles when a block is broken."""
        import random
        for _ in range(count):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(50, 150)
            vel_x = speed * (angle ** 0.5) if angle < 3.14159 else -speed * ((2 * 3.14159 - angle) ** 0.5)
            vel_y = speed * (angle ** 0.5) - 100
            
            particle = Particle(
                x=x + 16,
                y=y + 16,
                vel_x=vel_x,
                vel_y=vel_y,
                lifetime=0.8,
                max_lifetime=0.8,
                color=color,
                size=5
            )
            self.particles.append(particle)

    def emit_place_block(self, x: float, y: float, color: tuple[int, int, int]) -> None:
        """Emit particles when a block is placed."""
        import random
        for _ in range(3):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(30, 80)
            vel_x = speed * (angle ** 0.5) if angle < 3.14159 else -speed * ((2 * 3.14159 - angle) ** 0.5)
            vel_y = -speed * 0.5
            
            particle = Particle(
                x=x + 16,
                y=y + 16,
                vel_x=vel_x,
                vel_y=vel_y,
                lifetime=0.5,
                max_lifetime=0.5,
                color=color,
                size=3
            )
            self.particles.append(particle)

    def update(self, dt: float) -> None:
        """Update all particles."""
        remaining: list[Particle] = []
        for particle in self.particles:
            if particle.update(dt):
                remaining.append(particle)
        self.particles = remaining

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(screen, camera_x, camera_y)

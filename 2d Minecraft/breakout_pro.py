import pygame
import random
import sys

# --- KONFIGURATION & KONSTANTEN ---
pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (100, 100, 100)

# PowerUp Farben
PU_WIDE = GREEN
PU_NARROW = RED
PU_MULTIBALL = CYAN
PU_LASER = ORANGE
PU_SLOW = BLUE
PU_FAST = PURPLE
PU_LIFE = WHITE
PU_SCORE = YELLOW
PU_STICKY = GRAY
PU_PIERCING = (255, 105, 180) # Hot Pink

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Breakout Python")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48, bold=True)

# --- KLASSEN ---

class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 15
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 40
        self.speed = 8
        self.color = WHITE
        self.sticky = False # PowerUp Effekt
        self.laser_active = False
        self.lasers = []
        self.laser_timer = 0

    def move(self, direction):
        self.x += direction * self.speed
        # Grenzen
        if self.x < 0: self.x = 0
        if self.x + self.width > WIDTH: self.x = WIDTH - self.width

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        # Laser zeichnen
        if self.laser_active:
            for laser in self.lasers:
                pygame.draw.rect(surface, ORANGE, laser)

    def shoot(self):
        if self.laser_active:
            self.lasers.append(pygame.Rect(self.x + self.width // 2 - 2, self.y, 4, 10))

    def update_lasers(self, bricks):
        if self.laser_active:
            self.laser_timer -= 1
            if self.laser_timer <= 0:
                self.laser_active = False
            
            # Laser bewegen
            for laser in self.lasers[:]:
                laser.y -= 10
                if laser.y < 0:
                    self.lasers.remove(laser)
                else:
                    # Kollision mit Steinen
                    for brick in bricks[:]:
                        if laser.colliderect(brick.rect):
                            brick.hit()
                            if laser in self.lasers: self.lasers.remove(laser)
                            break

class Ball:
    def __init__(self, x, y, speed_factor=1.0):
        self.radius = 8
        self.x = x
        self.y = y
        self.base_speed = 5 * speed_factor
        self.dx = random.choice([-1, 1]) * self.base_speed
        self.dy = -self.base_speed
        self.active = True
        self.stuck_to_paddle = False
        self.piercing = False # PowerUp Effekt
        self.piercing_timer = 0

    def move(self):
        if self.stuck_to_paddle:
            return # Bewegt sich mit dem Paddle in der Hauptlogik

        self.x += self.dx
        self.y += self.dy

        # Wände
        if self.x <= 0 or self.x >= WIDTH:
            self.dx *= -1
        if self.y <= 0:
            self.dy *= -1
        
        # Piercing Timer
        if self.piercing:
            self.piercing_timer -= 1
            if self.piercing_timer <= 0:
                self.piercing = False

    def draw(self, surface):
        color = PURPLE if self.piercing else WHITE
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)

    def reset(self, paddle_x, paddle_width):
        self.x = paddle_x + paddle_width // 2
        self.y = HEIGHT - 50
        self.dx = random.choice([-1, 1]) * self.base_speed
        self.dy = -self.base_speed
        self.active = True
        self.stuck_to_paddle = False
        self.piercing = False

class Brick:
    def __init__(self, x, y, w, h, color, hits=1):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hits = hits
        self.max_hits = hits
        self.active = True

    def draw(self, surface):
        if self.active:
            # Farbe basierend auf Leben ändern
            c = self.color
            if self.hits == 2: c = (200, 200, 200)
            elif self.hits == 3: c = (100, 100, 100)
            pygame.draw.rect(surface, c, self.rect)
            pygame.draw.rect(surface, BLACK, self.rect, 2)

    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            self.active = False
            return True # Zerstört
        return False # Nur beschädigt

class PowerUp:
    TYPES = [
        ("WIDE", PU_WIDE), ("NARROW", PU_NARROW), ("MULTI", PU_MULTIBALL),
        ("LASER", PU_LASER), ("SLOW", PU_SLOW), ("FAST", PU_FAST),
        ("LIFE", PU_LIFE), ("SCORE", PU_SCORE), ("STICKY", PU_STICKY),
        ("PIERCING", PU_PIERCING)
    ]

    def __init__(self, x, y):
        self.type_name, self.color = random.choice(self.TYPES)
        self.rect = pygame.Rect(x, y, 20, 20)
        self.dy = 3
        self.active = True

    def move(self):
        self.rect.y += self.dy
        if self.rect.y > HEIGHT:
            self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, self.rect)
            # Erster Buchstabe als Label
            txt = font.render(self.type_name[0], True, BLACK)
            surface.blit(txt, (self.rect.x + 5, self.rect.y - 2))

# --- HAUPT SPIEL KLASSE ---

class Game:
    def __init__(self):
        self.state = "MENU" # MENU, PLAYING, GAMEOVER, LEVEL_TRANSITION
        self.difficulty = "NORMAL" # EASY, NORMAL, HARD
        self.level_mode = "CLASSIC" # CLASSIC, ENDLESS
        self.score = 0
        self.lives = 3
        self.level = 1
        
        self.paddle = Paddle()
        self.balls = []
        self.bricks = []
        self.powerups = []
        
        self.endless_timer = 0
        self.endless_speed = 60 # Frames bis neuer Row kommt

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.paddle = Paddle()
        self.balls = [Ball(WIDTH//2, HEIGHT-50, self.get_speed_factor())]
        self.powerups = []
        self.create_level()

    def get_speed_factor(self):
        if self.difficulty == "EASY": return 0.8
        if self.difficulty == "HARD": return 1.3
        return 1.0

    def create_level(self):
        self.bricks = []
        self.balls = [Ball(WIDTH//2, HEIGHT-50, self.get_speed_factor())]
        self.paddle.laser_active = False
        self.paddle.sticky = False
        self.paddle.width = 100 # Reset Paddle size

        if self.level_mode == "CLASSIC":
            rows = 5 + self.level
            cols = 8
            brick_w = WIDTH // cols - 10
            brick_h = 20
            
            for r in range(rows):
                for c in range(cols):
                    # Zufällige Farben und Hits basierend auf Level
                    hits = 1
                    if self.level > 2 and r % 2 == 0: hits = 2
                    if self.level > 4: hits = 3
                    
                    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                    b = Brick(c * (brick_w + 10) + 5, r * (brick_h + 10) + 50, brick_w, brick_h, color, hits)
                    self.bricks.append(b)
        
        elif self.level_mode == "ENDLESS":
            # Endlos startet leer, Blöcke kommen von oben
            pass

    def spawn_endless_row(self):
        cols = 6
        brick_w = WIDTH // cols - 20
        brick_h = 20
        for c in range(cols):
            if random.random() > 0.2: # 20% Chance auf Lücke
                hits = 1 + (self.score // 500) # Wird härter mit der Zeit
                color = RED if hits > 1 else BLUE
                b = Brick(c * (brick_w + 20) + 10, -30, brick_w, brick_h, color, hits)
                self.bricks.append(b)

    def apply_powerup(self, p_type):
        if p_type == "WIDE":
            self.paddle.width = min(200, self.paddle.width + 40)
        elif p_type == "NARROW":
            self.paddle.width = max(40, self.paddle.width - 40)
        elif p_type == "MULTI":
            if len(self.balls) < 5:
                for b in self.balls[:]:
                    new_b = Ball(b.x, b.y, 1.0)
                    new_b.dx = -b.dx
                    new_b.dy = b.dy
                    self.balls.append(new_b)
        elif p_type == "LASER":
            self.paddle.laser_active = True
            self.paddle.laser_timer = 600 # 10 Sekunden
        elif p_type == "SLOW":
            for b in self.balls:
                b.dx *= 0.6
                b.dy *= 0.6
        elif p_type == "FAST":
            for b in self.balls:
                b.dx *= 1.4
                b.dy *= 1.4
        elif p_type == "LIFE":
            self.lives += 1
        elif p_type == "SCORE":
            self.score += 500
        elif p_type == "STICKY":
            self.paddle.sticky = True
        elif p_type == "PIERCING":
            for b in self.balls:
                b.piercing = True
                b.piercing_timer = 600

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.paddle.move(-1)
        if keys[pygame.K_RIGHT]:
            self.paddle.move(1)
        if keys[pygame.K_SPACE]:
            if self.paddle.sticky:
                for b in self.balls:
                    if b.stuck_to_paddle:
                        b.stuck_to_paddle = False
                        b.dy = -abs(b.dy) # Nach oben schießen
            else:
                self.paddle.shoot()

    def update(self):
        if self.state != "PLAYING":
            return

        self.paddle.update_lasers(self.bricks)

        # Endless Mode Logic
        if self.level_mode == "ENDLESS":
            self.endless_timer += 1
            if self.endless_timer > self.endless_speed:
                self.spawn_endless_row()
                self.endless_timer = 0
                # Speed up slightly
                if self.endless_speed > 20:
                    self.endless_speed -= 0.1
                # Check Game Over (Bricks am Boden)
                for b in self.bricks:
                    if b.rect.y + b.rect.h > HEIGHT - 50:
                        self.lives = 0
                        self.state = "GAMEOVER"

        # Balls Update
        for ball in self.balls[:]:
            ball.move()
            
            # Paddle Collision
            paddle_rect = pygame.Rect(self.paddle.x, self.paddle.y, self.paddle.width, self.paddle.height)
            if ball.active and not ball.stuck_to_paddle and paddle_rect.collidepoint(ball.x, ball.y + ball.radius):
                if ball.dy > 0: # Nur wenn er von oben kommt
                    ball.dy *= -1
                    # Winkel ändern basierend auf Trefferpunkt
                    hit_pos = (ball.x - self.paddle.x) / self.paddle.width
                    ball.dx = (hit_pos - 0.5) * 10 * self.get_speed_factor()
                    
                    if self.paddle.sticky:
                        ball.stuck_to_paddle = True
            
            # Ball out of bounds
            if ball.y > HEIGHT:
                ball.active = False
            
            # Brick Collision
            if ball.active and not ball.stuck_to_paddle:
                for brick in self.bricks[:]:
                    if brick.active and brick.rect.collidepoint(ball.x, ball.y):
                        if not ball.piercing:
                            ball.dy *= -1
                        destroyed = brick.hit()
                        if destroyed:
                            self.bricks.remove(brick)
                            self.score += 10 * brick.max_hits
                            # PowerUp Chance (10%)
                            if random.random() < 0.10:
                                self.powerups.append(PowerUp(brick.rect.centerx, brick.rect.centery))
                        break # Nur einen Brick pro Frame pro Ball

        # Clean up dead balls
        dead_balls = [b for b in self.balls if not b.active]
        for b in dead_balls:
            if b in self.balls:
                self.balls.remove(b)
        
        # Sync balls to paddle if sticky or only one ball left at start
        if len(self.balls) == 0:
            self.lives -= 1
            if self.lives > 0:
                self.balls = [Ball(WIDTH//2, HEIGHT-50, self.get_speed_factor())]
            else:
                self.state = "GAMEOVER"
        else:
            # Wenn Sticky aktiv ist oder nur 1 Ball und noch nicht gestartet (hier vereinfacht: immer syncen wenn sticky)
            # Für dieses Spiel: Wenn Sticky, ball folgt paddle.
            for b in self.balls:
                if b.stuck_to_paddle:
                    b.x = self.paddle.x + self.paddle.width // 2
                    b.y = self.paddle.y - b.radius

        # PowerUps Update
        for p in self.powerups[:]:
            p.move()
            if p.rect.colliderect(paddle_rect):
                self.apply_powerup(p.type_name)
                self.powerups.remove(p)
            elif not p.active:
                if p in self.powerups: self.powerups.remove(p)

        # Level Complete (Classic)
        if self.level_mode == "CLASSIC" and len(self.bricks) == 0:
            self.level += 1
            self.create_level()

    def draw_menu(self):
        screen.fill(BLACK)
        title = big_font.render("BREAKOUT ULTRA", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        # Difficulty Selection
        diff_text = f"Schwierigkeit: {self.difficulty} (Pfeiltasten Links/Rechts)"
        d_surf = font.render(diff_text, True, YELLOW)
        screen.blit(d_surf, (WIDTH//2 - d_surf.get_width()//2, 250))

        # Mode Selection
        mode_text = f"Modus: {self.level_mode} (Oben/Unten)"
        m_surf = font.render(mode_text, True, CYAN)
        screen.blit(m_surf, (WIDTH//2 - m_surf.get_width()//2, 300))

        start_text = "Drücke ENTER zum Starten"
        s_surf = font.render(start_text, True, GREEN)
        screen.blit(s_surf, (WIDTH//2 - s_surf.get_width()//2, 400))

        # Controls Info
        ctrl_text = "Steuerung: Pfeiltasten bewegen, SPACE schießen/loswerfen"
        c_surf = font.render(ctrl_text, True, GRAY)
        screen.blit(c_surf, (WIDTH//2 - c_surf.get_width()//2, 500))

    def draw_game(self):
        screen.fill(BLACK)
        
        # UI
        score_txt = font.render(f"Score: {self.score}", True, WHITE)
        lives_txt = font.render(f"Leben: {self.lives}", True, RED)
        level_txt = font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(score_txt, (10, 10))
        screen.blit(lives_txt, (WIDTH - 120, 10))
        screen.blit(level_txt, (WIDTH//2 - 30, 10))

        # Objects
        self.paddle.draw(screen)
        for b in self.balls:
            b.draw(screen)
        for brick in self.bricks:
            brick.draw(screen)
        for p in self.powerups:
            p.draw(screen)

    def draw_gameover(self):
        screen.fill(BLACK)
        txt = big_font.render("GAME OVER", True, RED)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 50))
        sub = font.render(f"Final Score: {self.score}", True, WHITE)
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 10))
        restart = font.render("Drücke ENTER für Menü", True, GRAY)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 60))

    def run(self):
        running = True
        while running:
            clock.tick(FPS)
            
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if self.state == "MENU":
                        if event.key == pygame.K_LEFT:
                            diffs = ["EASY", "NORMAL", "HARD"]
                            idx = diffs.index(self.difficulty)
                            self.difficulty = diffs[(idx - 1) % 3]
                        if event.key == pygame.K_RIGHT:
                            diffs = ["EASY", "NORMAL", "HARD"]
                            idx = diffs.index(self.difficulty)
                            self.difficulty = diffs[(idx + 1) % 3]
                        if event.key == pygame.K_UP:
                            self.level_mode = "ENDLESS" if self.level_mode == "CLASSIC" else "CLASSIC"
                        if event.key == pygame.K_DOWN:
                            self.level_mode = "ENDLESS" if self.level_mode == "CLASSIC" else "CLASSIC"
                        if event.key == pygame.K_RETURN:
                            self.reset_game()
                            self.state = "PLAYING"
                    
                    elif self.state == "GAMEOVER":
                        if event.key == pygame.K_RETURN:
                            self.state = "MENU"

            if self.state == "MENU":
                self.handle_input() # Nur für visuelles Feedback im Menü falls nötig
                self.draw_menu()
            elif self.state == "PLAYING":
                self.handle_input()
                self.update()
                self.draw_game()
            elif self.state == "GAMEOVER":
                self.draw_gameover()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()


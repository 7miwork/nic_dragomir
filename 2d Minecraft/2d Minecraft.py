import pygame                  # Library Pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
BLOCK_SIZE = 32
WORLD_WIDTH = 200
WORLD_HEIGHT = 100
FPS = 60                        # Frames Per Second -> Bilder pro Sekunde

# Farben
COLORS = {
    'air': None,
    'grass': (34, 139, 34),  #michael@learnist.de      
    'dirt': (139, 69, 19),
    'stone': (105, 105, 105),
    'wood': (222, 184, 135),
    'leaves': (50, 205, 50),
    'coal': (47, 79, 79),
    'iron': (192, 192, 192),
    'gold': (255, 215, 0),
    'diamond': (0, 206, 209),
    'bedrock': (64, 64, 64)
}

BLOCK_HARDNESS = {
    'grass': 0.6,
    'dirt': 0.5,
    'stone': 1.5,
    'wood': 2.0,
    'leaves': 0.2,
    'coal': 3.0,
    'iron': 5.0,
    'gold': 3.0,
    'diamond': 15.0,
    'bedrock': -1  # Unbreakable
}

class Block:
    def __init__(self, block_type):
        self.type = block_type
        self.color = COLORS.get(block_type)
        self.hardness = BLOCK_HARDNESS.get(block_type, 1.0)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 48
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.speed = 5
        self.jump_strength = -12
        
    def update(self, keys, world):
        # Horizontal movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -self.speed
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = self.speed
        else:
            self.vx *= 0.8  # Friction
            
        # Jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.vy = self.jump_strength
            self.on_ground = False
            
        # Apply gravity
        self.vy += 0.5
        if self.vy > 15:  # Terminal velocity
            self.vy = 15
            
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Collision detection
        self.handle_collisions(world)
        
        # Keep player in world bounds
        self.x = max(self.width//2, min(self.x, WORLD_WIDTH * BLOCK_SIZE - self.width//2))
        
    def handle_collisions(self, world):
        self.on_ground = False
        
        # Get player bounds
        left = int((self.x - self.width//2) // BLOCK_SIZE)
        right = int((self.x + self.width//2) // BLOCK_SIZE)
        top = int((self.y - self.height//2) // BLOCK_SIZE)
        bottom = int((self.y + self.height//2) // BLOCK_SIZE)
        
        # Check for collisions
        for block_x in range(max(0, left), min(WORLD_WIDTH, right + 1)):
            for block_y in range(max(0, top), min(WORLD_HEIGHT, bottom + 1)):
                if world.get_block(block_x, block_y).type != 'air':
                    block_left = block_x * BLOCK_SIZE
                    block_right = (block_x + 1) * BLOCK_SIZE
                    block_top = block_y * BLOCK_SIZE
                    block_bottom = (block_y + 1) * BLOCK_SIZE
                    
                    player_left = self.x - self.width//2
                    player_right = self.x + self.width//2
                    player_top = self.y - self.height//2
                    player_bottom = self.y + self.height//2
                    
                    # Vertical collision
                    if player_left < block_right and player_right > block_left:
                        if self.vy > 0 and player_top < block_top:  # Falling down
                            self.y = block_top - self.height//2
                            self.vy = 0
                            self.on_ground = True
                        elif self.vy < 0 and player_bottom > block_bottom:  # Jumping up
                            self.y = block_bottom + self.height//2
                            self.vy = 0
                            
                    # Horizontal collision
                    if player_top < block_bottom and player_bottom > block_top:
                        if self.vx > 0 and player_left < block_left:  # Moving right
                            self.x = block_left - self.width//2
                            self.vx = 0
                        elif self.vx < 0 and player_right > block_right:  # Moving left
                            self.x = block_right + self.width//2
                            self.vx = 0
                            
    def draw(self, screen, camera):
        screen_x = self.x - camera.x - self.width//2
        screen_y = self.y - camera.y - self.height//2
        
        # Draw player body
        pygame.draw.rect(screen, (255, 107, 107), (screen_x, screen_y, self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (screen_x, screen_y, self.width, self.height), 2)
        
        # Draw simple face
        pygame.draw.circle(screen, (0, 0, 0), (int(screen_x + 8), int(screen_y + 12)), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(screen_x + 16), int(screen_y + 12)), 2)

class World:
    def __init__(self):
        self.blocks = {}
        self.generate_world()
        
    def generate_world(self):
        print("Generating world...")
        
        # Generate terrain using Perlin-like noise simulation
        surface_heights = []
        for x in range(WORLD_WIDTH):
            # Simple height variation
            height = 25 + int(10 * math.sin(x * 0.1) + 5 * math.sin(x * 0.05))
            surface_heights.append(height)
        
        for x in range(WORLD_WIDTH):
            surface_height = surface_heights[x]
            
            for y in range(WORLD_HEIGHT):
                if y < surface_height - 15:
                    # Sky
                    self.set_block(x, y, Block('air'))
                elif y < surface_height:
                    # Above ground - trees occasionally
                    if y == surface_height - 1 and random.random() < 0.05:
                        self.set_block(x, y, Block('wood'))
                        # Add leaves
                        for ly in range(max(0, y-3), y):
                            for lx in range(max(0, x-2), min(WORLD_WIDTH, x+3)):
                                if random.random() < 0.7:
                                    self.set_block(lx, ly, Block('leaves'))
                    else:
                        self.set_block(x, y, Block('air'))
                elif y == surface_height:
                    # Surface
                    self.set_block(x, y, Block('grass'))
                elif y < surface_height + 5:
                    # Dirt layer
                    self.set_block(x, y, Block('dirt'))
                elif y < surface_height + 25:
                    # Stone layer with ores
                    rand = random.random()
                    if rand < 0.02:
                        self.set_block(x, y, Block('coal'))
                    elif rand < 0.025:
                        self.set_block(x, y, Block('iron'))
                    else:
                        self.set_block(x, y, Block('stone'))
                elif y < WORLD_HEIGHT - 5:
                    # Deep stone with rare ores
                    rand = random.random()
                    if rand < 0.002:
                        self.set_block(x, y, Block('diamond'))
                    elif rand < 0.005:
                        self.set_block(x, y, Block('gold'))
                    elif rand < 0.02:
                        self.set_block(x, y, Block('iron'))
                    elif rand < 0.03:
                        self.set_block(x, y, Block('coal'))
                    else:
                        self.set_block(x, y, Block('stone'))
                else:
                    # Bedrock layer
                    self.set_block(x, y, Block('bedrock'))
        
        print("World generation complete!")
    
    def get_block(self, x, y):
        if 0 <= x < WORLD_WIDTH and 0 <= y < WORLD_HEIGHT:
            return self.blocks.get((x, y), Block('air'))
        return Block('air')
    
    def set_block(self, x, y, block):
        if 0 <= x < WORLD_WIDTH and 0 <= y < WORLD_HEIGHT:
            self.blocks[(x, y)] = block
    
    def break_block(self, x, y):
        if 0 <= x < WORLD_WIDTH and 0 <= y < WORLD_HEIGHT:
            block = self.get_block(x, y)
            if block.type != 'air' and block.type != 'bedrock':
                self.set_block(x, y, Block('air'))
                return block.type
        return None
    
    def place_block(self, x, y, block_type):
        if 0 <= x < WORLD_WIDTH and 0 <= y < WORLD_HEIGHT:
            if self.get_block(x, y).type == 'air':
                self.set_block(x, y, Block(block_type))
                return True
        return False

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        
    def update(self, player):
        # Follow player
        self.x = player.x - SCREEN_WIDTH // 2
        self.y = player.y - SCREEN_HEIGHT // 2
        
        # Keep camera in bounds
        self.x = max(0, min(self.x, WORLD_WIDTH * BLOCK_SIZE - SCREEN_WIDTH))
        self.y = max(0, min(self.y, WORLD_HEIGHT * BLOCK_SIZE - SCREEN_HEIGHT))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D Minecraft - Python Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        
        # Game objects
        self.world = World()
        self.player = Player(WORLD_WIDTH * BLOCK_SIZE // 2, 100)
        self.camera = Camera()
        
        # Game state
        self.inventory = {
            'dirt': 0, 'stone': 0, 'wood': 0, 'grass': 0, 'leaves': 0,
            'coal': 0, 'iron': 0, 'gold': 0, 'diamond': 0
        }
        self.selected_block = 'dirt'
        self.block_types = ['dirt', 'stone', 'wood', 'grass', 'coal', 'iron', 'gold', 'diamond']
        self.selected_index = 0
        
        # Mining
        self.mining_progress = 0
        self.mining_block = None
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                # Change selected block type
                if event.key >= pygame.K_1 and event.key <= pygame.K_8:
                    self.selected_index = event.key - pygame.K_1
                    if self.selected_index < len(self.block_types):
                        self.selected_block = self.block_types[self.selected_index]
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = int((mouse_x + self.camera.x) // BLOCK_SIZE)
                world_y = int((mouse_y + self.camera.y) // BLOCK_SIZE)
                
                if event.button == 1:  # Left click - mine
                    self.start_mining(world_x, world_y)
                elif event.button == 3:  # Right click - place
                    self.place_block(world_x, world_y)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Stop mining
                    self.mining_progress = 0
                    self.mining_block = None
        
        return True
    
    def start_mining(self, x, y):
        block = self.world.get_block(x, y)
        if block.type != 'air':
            self.mining_block = (x, y)
            self.mining_progress = 0
    
    def update_mining(self):
        if self.mining_block:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:  # Still holding left mouse button
                x, y = self.mining_block
                block = self.world.get_block(x, y)
                
                if block.hardness > 0:
                    self.mining_progress += 1
                    if self.mining_progress >= block.hardness * 30:  # Mining speed
                        # Break the block
                        broken_block = self.world.break_block(x, y)
                        if broken_block:
                            self.inventory[broken_block] += 1
                        self.mining_progress = 0
                        self.mining_block = None
            else:
                self.mining_progress = 0
                self.mining_block = None
    
    def place_block(self, x, y):
        if self.inventory[self.selected_block] > 0:
            # Check if player is not in the way
            player_block_x = int(self.player.x // BLOCK_SIZE)
            player_block_y = int(self.player.y // BLOCK_SIZE)
            
            if not (abs(x - player_block_x) <= 1 and abs(y - player_block_y) <= 2):
                if self.world.place_block(x, y, self.selected_block):
                    self.inventory[self.selected_block] -= 1
    
    def update(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.world)
        self.camera.update(self.player)
        self.update_mining()
    
    def draw_world(self):
        # Calculate visible blocks
        start_x = max(0, int(self.camera.x // BLOCK_SIZE) - 1)
        end_x = min(WORLD_WIDTH, int((self.camera.x + SCREEN_WIDTH) // BLOCK_SIZE) + 2)
        start_y = max(0, int(self.camera.y // BLOCK_SIZE) - 1)
        end_y = min(WORLD_HEIGHT, int((self.camera.y + SCREEN_HEIGHT) // BLOCK_SIZE) + 2)
        
        # Draw blocks
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                block = self.world.get_block(x, y)
                if block.color:
                    screen_x = x * BLOCK_SIZE - self.camera.x
                    screen_y = y * BLOCK_SIZE - self.camera.y
                    
                    pygame.draw.rect(self.screen, block.color, 
                                   (screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE))
                    
                    # Draw block outline
                    pygame.draw.rect(self.screen, (0, 0, 0), 
                                   (screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE), 1)
                    
                    # Draw mining progress
                    if self.mining_block == (x, y) and self.mining_progress > 0:
                        block = self.world.get_block(x, y)
                        if block.hardness > 0:
                            progress = self.mining_progress / (block.hardness * 30)
                            crack_alpha = int(progress * 255)
                            crack_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                            crack_surface.set_alpha(crack_alpha)
                            crack_surface.fill((255, 255, 255))
                            self.screen.blit(crack_surface, (screen_x, screen_y))
    
    def draw_ui(self):
        # Draw inventory
        y_offset = 10
        text = self.font.render("Inventory:", True, (255, 255, 255))
        self.screen.blit(text, (10, y_offset))
        y_offset += 25
        
        for block_type, count in self.inventory.items():
            if count > 0:
                color = (255, 255, 0) if block_type == self.selected_block else (255, 255, 255)
                text = self.small_font.render(f"{block_type}: {count}", True, color)
                self.screen.blit(text, (10, y_offset))
                y_offset += 18
        
        # Draw coordinates
        coords_text = self.font.render(f"X: {int(self.player.x // BLOCK_SIZE)}, Y: {int(self.player.y // BLOCK_SIZE)}", 
                                     True, (255, 255, 255))
        self.screen.blit(coords_text, (SCREEN_WIDTH - 150, 10))
        
        # Draw controls
        controls = [
            "WASD/Arrow Keys: Move",
            "Space: Jump",
            "Left Click: Mine",
            "Right Click: Place",
            "1-8: Select Block"
        ]
        
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, (255, 255, 255))
            self.screen.blit(text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100 + i * 15))
        
        # Draw selected block
        selected_text = self.font.render(f"Selected: {self.selected_block}", True, (255, 255, 0))
        self.screen.blit(selected_text, (10, SCREEN_HEIGHT - 40))
        
        # Draw hotbar
        hotbar_x = SCREEN_WIDTH // 2 - len(self.block_types) * 25
        hotbar_y = SCREEN_HEIGHT - 60
        
        for i, block_type in enumerate(self.block_types):
            color = COLORS.get(block_type, (100, 100, 100))
            border_color = (255, 255, 255) if i == self.selected_index else (100, 100, 100)
            
            # Draw hotbar slot
            slot_rect = pygame.Rect(hotbar_x + i * 50, hotbar_y, 40, 40)
            pygame.draw.rect(self.screen, color, slot_rect)
            pygame.draw.rect(self.screen, border_color, slot_rect, 2)
            
            # Draw item count
            count = self.inventory.get(block_type, 0)
            if count > 0:
                count_text = self.small_font.render(str(count), True, (255, 255, 255))
                self.screen.blit(count_text, (slot_rect.right - 15, slot_rect.bottom - 15))
    
    def run(self):
        running = True
        print("Starting 2D Minecraft!")
        print("Controls:")
        print("- WASD or Arrow Keys: Move")
        print("- Space: Jump")
        print("- Left Click: Mine blocks")
        print("- Right Click: Place blocks")
        print("- Numbers 1-8: Select block type")
        
        while running:
            running = self.handle_events()
            self.update()
            
            # Draw everything
            self.screen.fill((135, 206, 235))  # Sky blue
            self.draw_world()
            self.player.draw(self.screen, self.camera)
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()   



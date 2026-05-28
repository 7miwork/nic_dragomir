import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
from collections import defaultdict
import math

# Konstanten
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FOV = 70
RENDER_DISTANCE = 8
CHUNK_SIZE = 16

# Blocktypen
AIR = 0
GRASS = 1
DIRT = 2
STONE = 3
WOOD = 4
LEAVES = 5
SAND = 6
WATER = 7

# Block-Farben (R, G, B)
BLOCK_COLORS = {
    GRASS: (0.2, 0.8, 0.2),
    DIRT: (0.6, 0.4, 0.2),
    STONE: (0.5, 0.5, 0.5),
    WOOD: (0.4, 0.25, 0.1),
    LEAVES: (0.1, 0.6, 0.1),
    SAND: (0.9, 0.9, 0.5),
    WATER: (0.2, 0.4, 0.8)
}

class SimplexNoise:
    """Einfache Perlin/Simplex Noise Implementation für Terrain-Generierung"""
    def __init__(self, seed=0):
        random.seed(seed)
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm *= 2
    
    def noise2d(self, x, y):
        # Vereinfachte 2D Noise Funktion
        xi = int(x) & 255
        yi = int(y) & 255
        
        xf = x - int(x)
        yf = y - int(y)
        
        u = self.fade(xf)
        v = self.fade(yf)
        
        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]
        
        x1 = self.lerp(self.grad(aa, xf, yf), self.grad(ba, xf - 1, yf), u)
        x2 = self.lerp(self.grad(ab, xf, yf - 1), self.grad(bb, xf - 1, yf - 1), u)
        
        return self.lerp(x1, x2, v)
    
    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def lerp(self, a, b, t):
        return a + t * (b - a)
    
    def grad(self, hash_val, x, y):
        h = hash_val & 3
        if h == 0: return x + y
        elif h == 1: return -x + y
        elif h == 2: return x - y
        else: return -x - y

class Chunk:
    """Repräsentiert einen 16x16x64 Chunk von Blöcken"""
    def __init__(self, chunk_x, chunk_z, noise):
        self.chunk_x = chunk_x
        self.chunk_z = chunk_z
        self.blocks = np.zeros((CHUNK_SIZE, 64, CHUNK_SIZE), dtype=np.uint8)
        self.modified = True
        self.display_list = None
        self.generate_terrain(noise)
    
    def generate_terrain(self, noise):
        """Generiert Terrain mit Simplex Noise"""
        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                world_x = self.chunk_x * CHUNK_SIZE + x
                world_z = self.chunk_z * CHUNK_SIZE + z
                
                # Höhe basierend auf Noise berechnen
                height = int(32 + noise.noise2d(world_x * 0.05, world_z * 0.05) * 15)
                height = max(10, min(60, height))
                
                # Blöcke platzieren
                for y in range(height):
                    if y == height - 1:
                        self.blocks[x, y, z] = GRASS
                    elif y > height - 4:
                        self.blocks[x, y, z] = DIRT
                    else:
                        self.blocks[x, y, z] = STONE
                
                # Wasser unter y=25
                for y in range(min(25, height)):
                    if self.blocks[x, y, z] == AIR:
                        self.blocks[x, y, z] = WATER
                
                # Bäume generieren (selten)
                if random.random() < 0.02 and height > 25:
                    self.generate_tree(x, height, z)
    
    def generate_tree(self, x, y, z):
        """Generiert einen einfachen Baum"""
        # Stamm
        for h in range(5):
            if y + h < 64:
                self.blocks[x, y + h, z] = WOOD
        
        # Blätter
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for dy in range(3, 6):
                    if (0 <= x + dx < CHUNK_SIZE and 
                        0 <= z + dz < CHUNK_SIZE and 
                        y + dy < 64):
                        if abs(dx) + abs(dz) < 4:
                            self.blocks[x + dx, y + dy, z + dz] = LEAVES
    
    def get_block(self, x, y, z):
        if 0 <= x < CHUNK_SIZE and 0 <= y < 64 and 0 <= z < CHUNK_SIZE:
            return self.blocks[x, y, z]
        return None
    
    def set_block(self, x, y, z, block_type):
        if 0 <= x < CHUNK_SIZE and 0 <= y < 64 and 0 <= z < CHUNK_SIZE:
            self.blocks[x, y, z] = block_type
            self.modified = True

class Camera:
    """First-Person Kamera mit Minecraft-ähnlicher Steuerung"""
    def __init__(self):
        self.pos = [0.0, 40.0, 0.0]
        self.rot = [0.0, 0.0]  # [yaw, pitch]
        self.velocity = [0.0, 0.0, 0.0]
        self.on_ground = False
        self.flying = False
    
    def update(self, keys, dt):
        speed = 10.0 if self.flying else 5.0
        
        # Bewegung
        dx, dz = 0, 0
        if keys[K_w]:
            dx += math.sin(math.radians(self.rot[0]))
            dz += -math.cos(math.radians(self.rot[0]))
        if keys[K_s]:
            dx -= math.sin(math.radians(self.rot[0]))
            dz -= -math.cos(math.radians(self.rot[0]))
        if keys[K_a]:
            dx += math.sin(math.radians(self.rot[0] - 90))
            dz += -math.cos(math.radians(self.rot[0] - 90))
        if keys[K_d]:
            dx += math.sin(math.radians(self.rot[0] + 90))
            dz += -math.cos(math.radians(self.rot[0] + 90))
        
        # Bewegung normalisieren
        if dx != 0 or dz != 0:
            length = math.sqrt(dx * dx + dz * dz)
            dx /= length
            dz /= length
        
        self.pos[0] += dx * speed * dt
        self.pos[2] += dz * speed * dt
        
        # Fliegen/Springen
        if self.flying:
            if keys[K_SPACE]:
                self.pos[1] += speed * dt
            if keys[K_LSHIFT]:
                self.pos[1] -= speed * dt
        else:
            # Gravitation
            self.velocity[1] -= 20.0 * dt
            if keys[K_SPACE] and self.on_ground:
                self.velocity[1] = 8.0
            
            self.pos[1] += self.velocity[1] * dt
            
            # Bodenkollision (vereinfacht)
            if self.pos[1] < 30:
                self.pos[1] = 30
                self.velocity[1] = 0
                self.on_ground = True
            else:
                self.on_ground = False
    
    def mouse_move(self, dx, dy):
        sensitivity = 0.2
        self.rot[0] += dx * sensitivity
        self.rot[1] -= dy * sensitivity
        self.rot[1] = max(-90, min(90, self.rot[1]))
    
    def apply(self):
        glRotatef(-self.rot[1], 1, 0, 0)
        glRotatef(-self.rot[0], 0, 1, 0)
        glTranslatef(-self.pos[0], -self.pos[1], -self.pos[2])

class World:
    """Verwaltet alle Chunks und Blöcke"""
    def __init__(self, seed=42):
        self.chunks = {}
        self.noise = SimplexNoise(seed)
        self.selected_block = GRASS
    
    def get_chunk(self, chunk_x, chunk_z):
        key = (chunk_x, chunk_z)
        if key not in self.chunks:
            self.chunks[key] = Chunk(chunk_x, chunk_z, self.noise)
        return self.chunks[key]
    
    def get_block(self, x, y, z):
        if y < 0 or y >= 64:
            return AIR
        
        chunk_x = x // CHUNK_SIZE
        chunk_z = z // CHUNK_SIZE
        local_x = x % CHUNK_SIZE
        local_z = z % CHUNK_SIZE
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        return chunk.get_block(local_x, y, local_z)
    
    def set_block(self, x, y, z, block_type):
        if y < 0 or y >= 64:
            return
        
        chunk_x = x // CHUNK_SIZE
        chunk_z = z // CHUNK_SIZE
        local_x = x % CHUNK_SIZE
        local_z = z % CHUNK_SIZE
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        chunk.set_block(local_x, y, local_z, block_type)
    
    def render_chunk(self, chunk):
        """Rendert einen Chunk mit optimiertem Culling"""
        if chunk.modified or chunk.display_list is None:
            if chunk.display_list is not None:
                glDeleteLists(chunk.display_list, 1)
            
            chunk.display_list = glGenLists(1)
            glNewList(chunk.display_list, GL_COMPILE)
            
            glBegin(GL_QUADS)
            
            for x in range(CHUNK_SIZE):
                for y in range(64):
                    for z in range(CHUNK_SIZE):
                        block = chunk.blocks[x, y, z]
                        if block == AIR:
                            continue
                        
                        world_x = chunk.chunk_x * CHUNK_SIZE + x
                        world_z = chunk.chunk_z * CHUNK_SIZE + z
                        
                        # Face Culling - nur sichtbare Flächen rendern
                        self.render_block(world_x, y, world_z, block, chunk, x, z)
            
            glEnd()
            glEndList()
            chunk.modified = False
        
        glCallList(chunk.display_list)
    
    def render_block(self, x, y, z, block_type, chunk, local_x, local_z):
        """Rendert einen einzelnen Block mit Face Culling"""
        color = BLOCK_COLORS.get(block_type, (1, 1, 1))
        
        # Prüfe benachbarte Blöcke für Culling
        neighbors = {
            'top': self.get_block(x, y + 1, z),
            'bottom': self.get_block(x, y - 1, z),
            'north': self.get_block(x, y, z - 1),
            'south': self.get_block(x, y, z + 1),
            'west': self.get_block(x - 1, y, z),
            'east': self.get_block(x + 1, y, z)
        }
        
        # Top Face
        if neighbors['top'] == AIR or neighbors['top'] == WATER:
            glColor3f(*color)
            glVertex3f(x, y + 1, z)
            glVertex3f(x + 1, y + 1, z)
            glVertex3f(x + 1, y + 1, z + 1)
            glVertex3f(x, y + 1, z + 1)
        
        # Bottom Face
        if neighbors['bottom'] == AIR or neighbors['bottom'] == WATER:
            glColor3f(color[0] * 0.6, color[1] * 0.6, color[2] * 0.6)
            glVertex3f(x, y, z)
            glVertex3f(x, y, z + 1)
            glVertex3f(x + 1, y, z + 1)
            glVertex3f(x + 1, y, z)
        
        # North Face
        if neighbors['north'] == AIR or neighbors['north'] == WATER:
            glColor3f(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8)
            glVertex3f(x, y, z)
            glVertex3f(x + 1, y, z)
            glVertex3f(x + 1, y + 1, z)
            glVertex3f(x, y + 1, z)
        
        # South Face
        if neighbors['south'] == AIR or neighbors['south'] == WATER:
            glColor3f(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8)
            glVertex3f(x, y, z + 1)
            glVertex3f(x, y + 1, z + 1)
            glVertex3f(x + 1, y + 1, z + 1)
            glVertex3f(x + 1, y, z + 1)
        
        # West Face
        if neighbors['west'] == AIR or neighbors['west'] == WATER:
            glColor3f(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7)
            glVertex3f(x, y, z)
            glVertex3f(x, y + 1, z)
            glVertex3f(x, y + 1, z + 1)
            glVertex3f(x, y, z + 1)
        
        # East Face
        if neighbors['east'] == AIR or neighbors['east'] == WATER:
            glColor3f(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7)
            glVertex3f(x + 1, y, z)
            glVertex3f(x + 1, y, z + 1)
            glVertex3f(x + 1, y + 1, z + 1)
            glVertex3f(x + 1, y + 1, z)

class MinecraftClone:
    """Hauptspiel-Klasse"""
    def __init__(self):
        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Minecraft Clone - Python")
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        # OpenGL Setup
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        gluPerspective(FOV, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 500.0)
        
        # Nebel für Render-Distanz
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, (0.5, 0.7, 1.0, 1.0))
        glFogf(GL_FOG_DENSITY, 0.02)
        glFogi(GL_FOG_MODE, GL_EXP2)
        
        self.camera = Camera()
        self.world = World()
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Crosshair vorbereiten
        self.setup_crosshair()
    
    def setup_crosshair(self):
        """Crosshair für Block-Auswahl"""
        pass
    
    def draw_crosshair(self):
        """Zeichnet Crosshair in der Mitte des Bildschirms"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glColor3f(1, 1, 1)
        glLineWidth(2)
        
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        size = 10
        
        glBegin(GL_LINES)
        glVertex2f(cx - size, cy)
        glVertex2f(cx + size, cy)
        glVertex2f(cx, cy - size)
        glVertex2f(cx, cy + size)
        glEnd()
        
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def get_targeted_block(self):
        """Raycast um Block zu finden, den der Spieler ansieht"""
        max_distance = 5.0
        step = 0.1
        
        # Richtung berechnen
        yaw = math.radians(self.camera.rot[0])
        pitch = math.radians(self.camera.rot[1])
        
        dx = math.sin(yaw) * math.cos(pitch)
        dy = -math.sin(pitch)
        dz = -math.cos(yaw) * math.cos(pitch)
        
        # Raycast
        for i in range(int(max_distance / step)):
            x = self.camera.pos[0] + dx * i * step
            y = self.camera.pos[1] + dy * i * step
            z = self.camera.pos[2] + dz * i * step
            
            block = self.world.get_block(int(x), int(y), int(z))
            if block != AIR:
                return (int(x), int(y), int(z))
        
        return None
    
    def handle_events(self):
        """Event-Handling"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_f:
                    self.camera.flying = not self.camera.flying
                    print(f"Flying: {'ON' if self.camera.flying else 'OFF'}")
                elif event.key == K_1:
                    self.world.selected_block = GRASS
                elif event.key == K_2:
                    self.world.selected_block = DIRT
                elif event.key == K_3:
                    self.world.selected_block = STONE
                elif event.key == K_4:
                    self.world.selected_block = WOOD
                elif event.key == K_5:
                    self.world.selected_block = SAND
            
            elif event.type == MOUSEMOTION:
                self.camera.mouse_move(event.rel[0], event.rel[1])
            
            elif event.type == MOUSEBUTTONDOWN:
                target = self.get_targeted_block()
                if target:
                    x, y, z = target
                    if event.button == 1:  # Linksklick - Block zerstören
                        self.world.set_block(x, y, z, AIR)
                    elif event.button == 3:  # Rechtsklick - Block platzieren
                        # Finde benachbarte Position
                        for dx, dy, dz in [(0,1,0), (0,-1,0), (1,0,0), (-1,0,0), (0,0,1), (0,0,-1)]:
                            nx, ny, nz = x + dx, y + dy, z + dz
                            if self.world.get_block(nx, ny, nz) == AIR:
                                self.world.set_block(nx, ny, nz, self.world.selected_block)
                                break
    
    def update(self, dt):
        """Update-Logik"""
        keys = pygame.key.get_pressed()
        self.camera.update(keys, dt)
    
    def render(self):
        """Rendering"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.5, 0.7, 1.0, 1.0)  # Himmelsfarbe
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        self.camera.apply()
        
        # Chunks um Spieler rendern
        player_chunk_x = int(self.camera.pos[0]) // CHUNK_SIZE
        player_chunk_z = int(self.camera.pos[2]) // CHUNK_SIZE
        
        for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
                chunk = self.world.get_chunk(player_chunk_x + dx, player_chunk_z + dz)
                self.world.render_chunk(chunk)
        
        self.draw_crosshair()
        
        pygame.display.flip()
    
    def run(self):
        """Hauptspiel-Loop"""
        print("=== Minecraft Clone ===")
        print("Steuerung:")
        print("  WASD - Bewegung")
        print("  Maus - Umschauen")
        print("  Leertaste - Springen")
        print("  F - Flugmodus umschalten")
        print("  Linksklick - Block zerstören")
        print("  Rechtsklick - Block platzieren")
        print("  1-5 - Blocktyp wählen")
        print("  ESC - Beenden")
        print()
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()

if __name__ == "__main__":
    game = MinecraftClone()
    game.run()

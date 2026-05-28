# src/mobs.py

class Mob:
    def __init__(self, x, y, health=50, image=None):
        self.x = x
        self.y = y
        self.health = health
        self.image = image

# Monsterliste
# Geist (unsichtbar, fliegt durch Wände, greift Spieler an)
class Ghost(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, health=30, image="ghost.png")

# Flussmonster (schwimmt im Wasser, greift Spieler an)
class RiverMonster(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, health=70, image="river_monster.png")

# Wüstenkreatur (lebt in der Wüste, greift Spieler an)
class DesertCreature(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, health=60, image="desert_creature.png")

# Portalwächter (bewacht den Portalaktivator, greift Spieler an)
class PortalGuardian(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, health=100, image="portal_guardian.png")

# Boeser Fisch (lebt im Wasser, greift Spieler an)
class EvilFish(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, health=40, image="evil_fish.png")

# Nuklearer Zombie (lebt in nuklearer Welt, greift Spieler an)
class NuclearZombie(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, health=80, image="nuclear_zombie.png")

# Nuklearer Fisch (lebt in nuklearer Welt, schaedigt Spieler passiv)
class NuclearFish(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, health=50, image="nuclear_fish.png")

# Goldfisch (lebt in reicher Welt, gibt Gold beim Besiegen)
class Goldfish(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, health=30, image="goldfish.png")

# Sandmonster (lebt in der Wüste, greift Spieler mit Sandstrahlen an)
class SandMonster(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, health=70, image="sand_monster.png")
        
# Cars Monster (lebt in der Graswelt, greift Spieler mit Geschwindigkeit an)
class CarsMonster(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, health=90, image="cars_monster.png")

# Fisch (greift Spieler nicht an, schwimmt im Wasser)
class Fish(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, health=20, image="fish.png")
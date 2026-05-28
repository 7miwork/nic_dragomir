#!/usr/bin/env python3
“””
╔══════════════════════════════════════════════════════════════════════╗
║          GALACTIC SIEGE  v2.0 — Ultimate Edition                    ║
║          Modern Neon/Cyberpunk  |  tkinter                          ║
║                                                                      ║
║  NEW in v2:                                                          ║
║  • Roguelike Upgrade System (choose 1 of 3 between levels)          ║
║  • Destructible Bunkers (tactical cover)                             ║
║  • UFO Mystery Ship (random bonus drops)                             ║
║  • Achievement System (15 achievements)                              ║
║  • Enemy Formation Patterns (V, X, spiral, zigzag, diamond)         ║
║  • Endless / Survival Mode                                           ║
║  • Weather/Environment Events (asteroid, nebula, gravity, storm)     ║
║  • Chain Explosion System                                            ║
║  • Ship Skin Unlock System (6 skins)                                 ║
║  • Dynamic Speed-Up Pulse (fewer enemies = faster + visual pulse)    ║
║  • Ship Customization Screen                                         ║
╚══════════════════════════════════════════════════════════════════════╝
“””

import tkinter as tk
import random, math, time, json, os, colorsys

# ══════════════════════════════════════════════════════

# CONSTANTS

# ══════════════════════════════════════════════════════

W, H = 960, 720
FPS  = 60
SAVE_FILE = “galactic_siege_v2.json”

C = {
“bg”:      “#040412”, “grid”:   “#080825”, “cyan”:    “#00ffff”,
“magenta”: “#ff00ff”, “yellow”: “#ffff00”, “green”:   “#00ff88”,
“orange”:  “#ff8800”, “red”:    “#ff2244”, “purple”:  “#aa00ff”,
“white”:   “#ffffff”, “dim”:    “#2a3a55”, “player”:  “#00eeff”,
“bullet”:  “#00ffaa”, “enemy1”: “#ff4488”, “enemy2”:  “#ff8800”,
“enemy3”:  “#aa44ff”, “boss”:   “#ff0055”, “shield”:  “#0088ff”,
“bunker”:  “#44ff88”, “ufo”:    “#ff00cc”, “chain”:   “#ffaa00”,
}

# ── Power-ups ──────────────────────────────────────────

POWERUPS = [
{“id”:“triple”,  “name”:“TRIPLE SHOT”,    “color”:”#00ffff”,“sym”:”❯❯❯”,“dur”:8},
{“id”:“rapid”,   “name”:“RAPID FIRE”,     “color”:”#ffff00”,“sym”:“⚡”,  “dur”:6},
{“id”:“shield”,  “name”:“ENERGY SHIELD”,  “color”:”#0088ff”,“sym”:“🛡”,  “dur”:10},
{“id”:“wide”,    “name”:“WIDE BEAM”,      “color”:”#ff00ff”,“sym”:“═══”, “dur”:7},
{“id”:“laser”,   “name”:“LASER CANNON”,   “color”:”#ff0088”,“sym”:“▌”,   “dur”:5},
{“id”:“bomb”,    “name”:“NOVA BOMB”,      “color”:”#ff8800”,“sym”:“💥”,  “dur”:0},
{“id”:“dual”,    “name”:“DUAL CANNON”,    “color”:”#88ff00”,“sym”:“⫾”,   “dur”:9},
{“id”:“homing”,  “name”:“HOMING MISSILE”, “color”:”#ff4400”,“sym”:“◈”,   “dur”:8},
{“id”:“slowmo”,  “name”:“TIME WARP”,      “color”:”#cc00ff”,“sym”:“⏱”,   “dur”:5},
{“id”:“magnet”,  “name”:“POWER MAGNET”,   “color”:”#ffcc00”,“sym”:“⬡”,   “dur”:12},
{“id”:“life”,    “name”:“EXTRA LIFE”,     “color”:”#ff2244”,“sym”:“❤”,   “dur”:0},
{“id”:“score2x”, “name”:“SCORE ×2”,       “color”:”#ffffff”,“sym”:“×2”,  “dur”:10},
]

# ── Roguelike permanent upgrades ──────────────────────

ALL_UPGRADES = [
{“id”:“fire_rate”,    “name”:“OVERCLOCKED”,     “desc”:“Fire rate +15%”,    “color”:”#ffff00”,“sym”:“⚡”,“max”:5},
{“id”:“bullet_dmg”,   “name”:“PENETRATOR”,      “desc”:“Bullet damage +1”,  “color”:”#ff4400”,“sym”:“▲”,“max”:4},
{“id”:“move_speed”,   “name”:“AFTERBURNER”,     “desc”:“Move speed +0.8”,   “color”:”#00ff88”,“sym”:“▶”,“max”:5},
{“id”:“shield_regen”, “name”:“NANO-REPAIR”,     “desc”:“Shield regen on kill”,“color”:”#0088ff”,“sym”:“🛡”,“max”:3},
{“id”:“luck”,         “name”:“FORTUNE MODULE”,  “desc”:“Power-up drop +20%”,“color”:”#ffcc00”,“sym”:“⬡”,“max”:4},
{“id”:“piercing”,     “name”:“RAILGUN”,         “desc”:“Bullets pierce enemies”,“color”:”#ff00ff”,“sym”:“→”,“max”:1},
{“id”:“multishot”,    “name”:“SCATTER GUN”,     “desc”:“Spread shot always”, “color”:”#00ffcc”,“sym”:“✦”,“max”:2},
{“id”:“score_boost”,  “name”:“GOLD CHIP”,       “desc”:“Base score +25%”,   “color”:”#ffd700”,“sym”:“★”,“max”:4},
{“id”:“auto_shield”,  “name”:“AEGIS”,           “desc”:“Auto-shield on low HP”,“color”:”#44aaff”,“sym”:“⬡”,“max”:1},
{“id”:“chain_power”,  “name”:“CHAIN REACTOR”,   “desc”:“Chain bonus +50%”,  “color”:”#ff8800”,“sym”:“⛓”,“max”:3},
{“id”:“crit_chance”,  “name”:“TARGETING AI”,    “desc”:“10% crit chance”,   “color”:”#ff2244”,“sym”:“◎”,“max”:5},
{“id”:“cooldown_red”, “name”:“QUANTUM CORE”,    “desc”:“All cooldowns -10%”,“color”:”#cc00ff”,“sym”:“◈”,“max”:4},
]

# ── Achievements ───────────────────────────────────────

ACHIEVEMENTS = [
{“id”:“first_kill”,  “name”:“First Blood”,      “desc”:“Destroy first enemy”,          “sym”:“🩸”,“color”:”#ff4444”},
{“id”:“combo_10”,    “name”:“Combo Artist”,      “desc”:“Reach ×10 combo”,              “sym”:“🎨”,“color”:”#ff8800”},
{“id”:“combo_50”,    “name”:“Unstoppable”,       “desc”:“Reach ×50 combo”,              “sym”:“🌪”,“color”:”#ff0088”},
{“id”:“ufo_kill”,    “name”:“UFO Hunter”,        “desc”:“Destroy the Mystery Ship”,     “sym”:“🛸”,“color”:”#ff00cc”},
{“id”:“boss_kill”,   “name”:“Boss Slayer”,       “desc”:“Defeat first boss”,            “sym”:“💀”,“color”:”#ff0055”},
{“id”:“no_damage”,   “name”:“Ghost Pilot”,       “desc”:“Clear a level without damage”, “sym”:“👻”,“color”:”#aaffff”},
{“id”:“bunker_last”, “name”:“Last Shelter”,      “desc”:“Bunker saves you from death”,  “sym”:“🏰”,“color”:”#44ff88”},
{“id”:“chain_5”,     “name”:“Chain Reaction”,    “desc”:“5-enemy chain explosion”,      “sym”:“💥”,“color”:”#ffaa00”},
{“id”:“endless_10”,  “name”:“Survivor”,          “desc”:“Reach wave 10 in Endless”,     “sym”:“🏆”,“color”:”#ffdd00”},
{“id”:“all_skins”,   “name”:“Collector”,         “desc”:“Unlock all ship skins”,        “sym”:“🎖”,“color”:”#ffd700”},
{“id”:“max_upgrade”, “name”:“Fully Upgraded”,    “desc”:“Max out any upgrade”,          “sym”:“⚙”,“color”:”#00ffcc”},
{“id”:“score_100k”,  “name”:“Legend”,            “desc”:“Reach 100,000 score”,          “sym”:“🌟”,“color”:”#ffffff”},
{“id”:“level_15”,    “name”:“Galaxy Conqueror”,  “desc”:“Clear all 15 levels”,         “sym”:“🌌”,“color”:”#aa00ff”},
{“id”:“weather_boss”,“name”:“Storm Rider”,       “desc”:“Kill boss during weather event”,“sym”:“⚡”,“color”:”#ffff00”},
{“id”:“speedrun_1”,  “name”:“Warp Speed”,        “desc”:“Clear level 1 in under 30s”,  “sym”:“🚀”,“color”:”#00eeff”},
]

# ── Ship skins ──────────────────────────────────────────

SKINS = [
{“id”:“default”,  “name”:“VIPER”,      “color”:”#00eeff”,“unlock”:“Start”},
{“id”:“fire”,     “name”:“INFERNO”,    “color”:”#ff4400”,“unlock”:“Score 10,000”},
{“id”:“phantom”,  “name”:“PHANTOM”,    “color”:”#aa00ff”,“unlock”:“Ghost Pilot”},
{“id”:“golden”,   “name”:“GOLD EAGLE”, “color”:”#ffd700”,“unlock”:“Score 50,000”},
{“id”:“neon”,     “name”:“NEON GOD”,   “color”:”#ff00ff”,“unlock”:“Reach Level 10”},
{“id”:“storm”,    “name”:“STORM”,      “color”:”#00ff88”,“unlock”:“Survive 10 waves”},
]

# ── Weather events ──────────────────────────────────────

WEATHER_EVENTS = [
{“id”:“asteroid”,  “name”:“ASTEROID FIELD”,   “color”:”#aa8844”,“desc”:“Dodge falling rocks!”},
{“id”:“nebula”,    “name”:“NEBULA CLOUD”,      “color”:”#8844ff”,“desc”:“Reduced visibility”},
{“id”:“gravity”,   “name”:“GRAVITY WELL”,      “color”:”#4488ff”,“desc”:“Bullets curve downward”},
{“id”:“storm”,     “name”:“PLASMA STORM”,      “color”:”#ff4400”,“desc”:“Random lightning strikes!”},
{“id”:“emp”,       “name”:“EMP PULSE”,         “color”:”#ffff00”,“desc”:“Weapons temporarily offline”},
{“id”:“wormhole”,  “name”:“WORMHOLE”,          “color”:”#ff00ff”,“desc”:“Enemies teleport randomly”},
]

# ── Enemy formation patterns ───────────────────────────

FORMATIONS = [“grid”,“v_shape”,“diamond”,“x_shape”,“zigzag”,“spiral”,“wings”,“double_arc”]

# ══════════════════════════════════════════════════════

# SAVE / LOAD

# ══════════════════════════════════════════════════════

def load_save():
if os.path.exists(SAVE_FILE):
try:
with open(SAVE_FILE) as f:
return json.load(f)
except: pass
return {
“highscores”: [],
“achievements”: [],
“unlocked_skins”: [“default”],
“total_score”: 0,
“endless_best”: 0,
}

def write_save(data):
with open(SAVE_FILE,“w”) as f:
json.dump(data, f, indent=2)

def add_highscore(save, name, score, level, mode=“story”):
save[“highscores”].append({“name”:name,“score”:score,“level”:level,
“date”:time.strftime(”%Y-%m-%d”),“mode”:mode})
save[“highscores”].sort(key=lambda x:x[“score”],reverse=True)
save[“highscores”] = save[“highscores”][:12]
save[“total_score”] = save.get(“total_score”,0) + score

# ══════════════════════════════════════════════════════

# LEVEL CONFIG

# ══════════════════════════════════════════════════════

def make_level(n, endless=False):
if endless:
tier = min(4, n // 5)
return {
“level”: n, “tier”: tier,
“tier_name”: [“☆ ROOKIE”,“★ SOLDIER”,“★★ ELITE”,“★★★ COMMANDER”,“★★★★ OVERLORD”][tier],
“is_boss”: n % 8 == 0,
“cols”: min(4 + n//2, 12), “rows”: min(2 + n//4, 6),
“enemy_speed”: 0.4 + n * 0.12,
“enemy_drop”: 10 + tier*2,
“shoot_chance”: 0.0006 + n*0.00025,
“boss_hp”: 150 + n*60,
“enemy_types”: min(1+tier,3),
“powerup_freq”: max(0.001, 0.003 - n*0.0001),
“bg_speed”: 0.4 + tier*0.2,
“formation”: random.choice(FORMATIONS),
“weather”: random.choice(WEATHER_EVENTS) if n % 3 == 0 else None,
}
tier = (n-1)//3
tier_names = [“☆ ROOKIE”,“★ SOLDIER”,“★★ ELITE”,“★★★ COMMANDER”,“★★★★ OVERLORD”]
formations_by_level = [“grid”,“grid”,“v_shape”,“grid”,“boss”,
“diamond”,“x_shape”,“zigzag”,“grid”,“boss”,
“spiral”,“wings”,“double_arc”,“zigzag”,“boss”]
weathers = [None,None,“nebula”,None,None, “asteroid”,None,“gravity”,None,None,
“storm”,None,“emp”,“wormhole”,None]
return {
“level”: n, “tier”: tier,
“tier_name”: tier_names[min(tier,4)],
“is_boss”: n%5==0,
“cols”: min(3+n,11), “rows”: min(1+tier,5),
“enemy_speed”: 0.5 + tier*0.4 + n*0.08,
“enemy_drop”: 12 + tier*3,
“shoot_chance”: 0.0008 + tier*0.0006 + n*0.00015,
“boss_hp”: 200 + n*80 if n%5==0 else 0,
“enemy_types”: min(1+tier,3),
“powerup_freq”: max(0.0008, 0.002 - n*0.00005),
“bg_speed”: 0.3 + tier*0.2,
“formation”: formations_by_level[n-1] if n<=15 else “grid”,
“weather”: WEATHER_EVENTS[[i for i,w in enumerate(weathers) if w and weathers[i-1 if i>0 else 0]==w.get(“id”,””)][0]] if False else (
next((w for w in WEATHER_EVENTS if w[“id”]==(weathers[n-1] if n<=15 else None)), None)
),
}

# ══════════════════════════════════════════════════════

# PARTICLES

# ══════════════════════════════════════════════════════

class Particle:
**slots** = (“x”,“y”,“vx”,“vy”,“life”,“max_life”,“size”,“r”,“g”,“b”)
def **init**(self,x,y,color,vx=None,vy=None,life=None,size=None):
self.x,self.y = x,y
self.vx = vx if vx is not None else random.uniform(-4,4)
self.vy = vy if vy is not None else random.uniform(-5,1)
self.life = life if life is not None else random.randint(20,50)
self.max_life = self.life
self.size = size if size is not None else random.uniform(1.5,4)
c = color.lstrip(”#”)
self.r,self.g,self.b = int(c[0:2],16),int(c[2:4],16),int(c[4:6],16)
def update(self):
self.x+=self.vx; self.y+=self.vy
self.vy+=0.12; self.vx*=0.97; self.life-=1
def alive(self): return self.life>0
def draw_color(self):
ratio=self.life/self.max_life
return f”#{int(self.r*ratio):02x}{int(self.g*ratio):02x}{int(self.b*ratio):02x}”

def explode(parts,x,y,color,count=20):
for _ in range(count):
a=random.uniform(0,math.tau); s=random.uniform(1,6)
parts.append(Particle(x,y,color,math.cos(a)*s,math.sin(a)*s,
random.randint(25,60),random.uniform(1.5,5)))
for i in range(10):
a=math.tau*i/10; s=random.uniform(3,8)
parts.append(Particle(x,y,”#ffffff”,math.cos(a)*s,math.sin(a)*s,
random.randint(8,22),random.uniform(1,2.5)))

# ══════════════════════════════════════════════════════

# BUNKER

# ══════════════════════════════════════════════════════

class Bunker:
SEG_W, SEG_H = 12, 10
def **init**(self, cx, y):
# Grid of segments: True=intact
self.cx = cx; self.y = y
self.cols = 7; self.rows = 3
# Classic bunker shape (arch)
self.segs = []
arch_mask = [
[1,1,1,1,1,1,1],
[1,1,1,1,1,1,1],
[1,1,0,0,0,1,1],
]
for r in range(self.rows):
row=[]
for c2 in range(self.cols):
row.append(arch_mask[r][c2]==1)
self.segs.append(row)
self.total = sum(sum(r) for r in self.segs)
self.hp = self.total

```
def hit(self, bx, by):
    """Returns True if bunker absorbed the hit."""
    x0 = self.cx - self.cols*self.SEG_W//2
    y0 = self.y
    col = int((bx - x0) / self.SEG_W)
    row = int((by - y0) / self.SEG_H)
    if 0<=row<self.rows and 0<=col<self.cols and self.segs[row][col]:
        self.segs[row][col] = False
        self.hp -= 1
        # Damage neighbours randomly
        if random.random()<0.3:
            nr,nc = row+random.choice([-1,0,1]),col+random.choice([-1,0,1])
            if 0<=nr<self.rows and 0<=nc<self.cols:
                if self.segs[nr][nc]:
                    self.segs[nr][nc]=False; self.hp-=1
        return True
    # Check rough bounding box
    x1=self.cx-self.cols*self.SEG_W//2; x2=x1+self.cols*self.SEG_W
    y1=self.y; y2=y1+self.rows*self.SEG_H
    return x1<=bx<=x2 and y1<=by<=y2

def blocks(self, bx, by):
    x0=self.cx-self.cols*self.SEG_W//2; y0=self.y
    col=int((bx-x0)/self.SEG_W); row=int((by-y0)/self.SEG_H)
    if 0<=row<self.rows and 0<=col<self.cols:
        return self.segs[row][col]
    return False

def draw(self, canvas, pulse=0):
    x0=self.cx-self.cols*self.SEG_W//2; y0=self.y
    ratio = self.hp/max(1,self.total)
    if ratio>0.6: base="#44ff88"
    elif ratio>0.3: base="#ffaa00"
    else: base="#ff2244"
    # Pulse when under fire
    if pulse>0:
        v=int(pulse*60)
        base=f"#{v:02x}ff{v:02x}"
    for r in range(self.rows):
        for c2 in range(self.cols):
            if self.segs[r][c2]:
                x=x0+c2*self.SEG_W; y=y0+r*self.SEG_H
                canvas.create_rectangle(x,y,x+self.SEG_W-1,y+self.SEG_H-1,
                                        fill=base,outline=C["bg"],width=1)
```

# ══════════════════════════════════════════════════════

# UFO / MYSTERY SHIP

# ══════════════════════════════════════════════════════

class UFO:
def **init**(self):
self.active = False
self.x = -60; self.y = 55
self.dir = 1; self.speed = 3.5
self.hp = 3; self.anim_t = 0
self.cooldown = random.randint(FPS*15, FPS*35)
self.rewards = [“score_big”,“life”,“random_powerup”,“upgrade_token”,“shield”]

```
def update(self):
    if self.active:
        self.x += self.speed * self.dir
        self.anim_t += 0.08
        if self.x > W+80 or self.x < -80:
            self.active = False
            self.cooldown = random.randint(FPS*20, FPS*45)
    else:
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.activate()

def activate(self):
    self.active = True
    self.dir = random.choice([-1,1])
    self.x = -60 if self.dir==1 else W+60
    self.hp = 3
    self.cooldown = random.randint(FPS*20, FPS*45)

def draw(self, canvas):
    if not self.active: return
    x,y = self.x, self.y
    t = self.anim_t
    # Body
    canvas.create_oval(x-35,y-12,x+35,y+12,fill="#220033",outline=C["ufo"],width=2)
    # Dome
    canvas.create_oval(x-18,y-22,x+18,y+2,fill="#110022",outline="#cc00aa",width=1)
    # Rotating lights
    for i in range(6):
        a = math.tau*i/6 + t
        lx=x+math.cos(a)*28; ly=y+math.sin(a)*8
        blink = "#ff00cc" if (self.anim_t*3+i)%2<1 else "#440033"
        canvas.create_oval(lx-3,ly-3,lx+3,ly+3,fill=blink,outline="")
    # HP pips
    for i in range(self.hp):
        canvas.create_oval(x-8+i*8,y+14,x-3+i*8,y+19,fill=C["ufo"],outline="")
    # Label
    canvas.create_text(x,y-30,text="★ MYSTERY ★",fill=C["ufo"],
                      font=("Courier",8,"bold"))
```

# ══════════════════════════════════════════════════════

# ASTEROID (weather object)

# ══════════════════════════════════════════════════════

class Asteroid:
def **init**(self):
self.x = random.uniform(30,W-30)
self.y = -20
self.speed = random.uniform(2,5)
self.rot = 0; self.rot_speed = random.uniform(-0.08,0.08)
self.size = random.randint(10,22)
self.hp = 2
pts=[]
for i in range(8):
a=math.tau*i/8; r=self.size*random.uniform(0.7,1.3)
pts.append((math.cos(a)*r, math.sin(a)*r))
self.pts = pts

```
def update(self):
    self.y += self.speed; self.rot += self.rot_speed

def alive(self): return self.y < H+30

def draw(self, canvas):
    poly=[]
    for px,py in self.pts:
        rx=px*math.cos(self.rot)-py*math.sin(self.rot)
        ry=px*math.sin(self.rot)+py*math.cos(self.rot)
        poly.extend([self.x+rx, self.y+ry])
    if len(poly)>=6:
        canvas.create_polygon(poly,fill="#554433",outline="#887755",width=1)
```

# ══════════════════════════════════════════════════════

# ENEMY

# ══════════════════════════════════════════════════════

class Enemy:
SHAPES = {
0:[(0,-10),(8,0),(6,8),(-6,8),(-8,0)],
1:[(0,-12),(5,-4),(12,0),(5,8),(-5,8),(-12,0),(-5,-4)],
2:[(0,-8),(8,-8),(12,0),(8,8),(0,4),(-8,8),(-12,0),(-8,-8)],
}
def **init**(self,x,y,etype,tier):
self.x,self.y=x,y; self.etype=etype
self.hp = 1 + etype*(tier//2)
self.max_hp = self.hp
self.color=[C[“enemy1”],C[“enemy2”],C[“enemy3”]][etype]
self.hit_flash=0; self.anim_t=random.uniform(0,math.tau)
self.alive=True; self.last_kill_t=0

```
def pts(self): return (self.etype+1)*10
def draw(self,canvas):
    x,y=self.x,self.y
    self.anim_t+=0.04
    bob=math.sin(self.anim_t)*2
    col="#ffffff" if self.hit_flash>0 else self.color
    if self.hit_flash>0: self.hit_flash-=1
    shape=[(x+px, y+py+bob) for px,py in self.SHAPES[self.etype]]
    canvas.create_polygon(shape,fill=col,outline="#ffffff",width=1)
    if self.max_hp>1:
        bw=22; r2=self.hp/self.max_hp
        canvas.create_rectangle(x-bw//2,y+13,x+bw//2,y+16,fill="#222",outline="")
        bc="#00ff44" if r2>0.5 else "#ffaa00" if r2>0.25 else "#ff2244"
        canvas.create_rectangle(x-bw//2,y+13,x-bw//2+int(bw*r2),y+16,fill=bc,outline="")
    canvas.create_oval(x-3,y-3+bob,x+3,y+3+bob,fill=col,outline="")
    canvas.create_oval(x-1,y-1+bob,x+1,y+1+bob,fill="#ffffff",outline="")
```

# ══════════════════════════════════════════════════════

# BOSS

# ══════════════════════════════════════════════════════

class Boss:
NAMES=[“HARBINGER”,“DEVASTATOR”,“OBLIVION”,“NEMESIS”,“APOCALYPSE”]
def **init**(self,cfg,n):
self.x=W//2; self.y=110
self.hp=cfg[“boss_hp”]; self.max_hp=self.hp
self.move_t=0; self.shoot_t=0
self.speed=1.5+n*0.12; self.pattern=0
self.enraged=False; self.anim_t=0; self.hit_flash=0
self.size=52+min(n,8)*3
self.name=self.NAMES[n//5 % len(self.NAMES)]
self.phase=1

```
def update(self):
    self.move_t+=0.022; self.anim_t+=0.055; self.shoot_t+=1
    if self.hit_flash>0: self.hit_flash-=1
    if self.hp<self.max_hp*0.3 and not self.enraged:
        self.enraged=True; self.speed*=1.7
    if self.pattern==0: self.x=W//2+math.sin(self.move_t)*300
    elif self.pattern==1:
        self.x=W//2+math.sin(self.move_t*2)*250
        self.y=110+math.cos(self.move_t)*40
    elif self.pattern==2:
        self.x=W//2+math.cos(self.move_t*1.5)*320
        self.y=100+abs(math.sin(self.move_t))*60
    elif self.pattern==3:
        self.x=W//2+math.sin(self.move_t*3)*200
        self.y=110+math.sin(self.move_t*2)*50
    if int(self.move_t*50)%280==0:
        self.pattern=(self.pattern+1)%4

def should_shoot(self):
    rate=40 if not self.enraged else 20
    return self.shoot_t%rate==0

def fire(self):
    bullets=[]
    count=8 if not self.enraged else 16
    for i in range(count):
        a=math.tau*i/count+self.move_t*2; sp=4 if not self.enraged else 7
        bullets.append({"x":self.x,"y":self.y,"dx":math.cos(a)*sp,
                        "dy":math.sin(a)*sp,"type":"enemy_spiral",
                        "w":8,"h":8,"color":C["boss"]})
    if self.enraged:
        # Extra aimed shots
        bullets.append({"x":self.x,"y":self.y,"dx":-2,"dy":6,"type":"enemy","w":10,"h":10,"color":"#ff8844"})
        bullets.append({"x":self.x,"y":self.y,"dx":2,"dy":6,"type":"enemy","w":10,"h":10,"color":"#ff8844"})
    return bullets

def draw(self,canvas):
    x,y=self.x,self.y; s=self.size; t=self.anim_t
    col="#ffffff" if self.hit_flash>0 else C["boss"]
    # Outer orbiters
    for i in range(8):
        a=math.tau*i/8+t; rx=x+math.cos(a)*(s+18); ry=y+math.sin(a)*(s*0.55+12)
        rs=7+math.sin(t+i)*3
        canvas.create_oval(rx-rs,ry-rs,rx+rs,ry+rs,fill="#ff4400",outline=col,width=1)
    # Body
    pts=[]
    for i in range(14):
        a=math.tau*i/14+t*0.25; r=s+math.sin(t*3+i)*9
        pts.extend([x+math.cos(a)*r, y+math.sin(a)*r*0.58])
    if len(pts)>=6:
        canvas.create_polygon(pts,fill="#280010",outline=col,width=2,smooth=True)
    # Core
    cr=s*0.42
    canvas.create_oval(x-cr,y-cr*0.68,x+cr,y+cr*0.68,fill="#110018",outline="#ff4400",width=2)
    er=cr*0.44
    ecol="#ff0000" if self.enraged else "#ff6644"
    canvas.create_oval(x-er,y-er*0.68,x+er,y+er*0.68,fill=ecol,outline="#ff8800",width=1)
    pr=er*0.38
    canvas.create_oval(x-pr,y-pr*0.68,x+pr,y+pr*0.68,fill="#000",outline="")
    # HP bar
    bw=210; hr=self.hp/self.max_hp
    yb=y+s*0.72+8
    canvas.create_rectangle(x-bw//2,yb,x+bw//2,yb+16,fill="#111",outline="#444",width=1)
    bc="#ff0000" if self.enraged else ("#00ff44" if hr>0.5 else "#ffaa00")
    canvas.create_rectangle(x-bw//2,yb,x-bw//2+int(bw*hr),yb+16,fill=bc,outline="")
    tag=f"⚡ ENRAGED ⚡" if self.enraged else f"◈ {self.name} ◈"
    canvas.create_text(x,yb+26,text=tag,fill=C["boss"],font=("Courier",12,"bold"))
```

# ══════════════════════════════════════════════════════

# PLAYER

# ══════════════════════════════════════════════════════

class Player:
def **init**(self, skin_color=”#00eeff”):
self.x=W//2; self.y=H-65
self.base_speed=5; self.lives=3; self.max_lives=5
self.score=0; self.combo=0; self.max_combo=0; self.combo_timer=0
self.active_powerups={}; self.invincible=0; self.shield_hp=0
self.shoot_cooldown=0; self.base_cooldown=18
self.trail=[]; self.color=skin_color
self.upgrades={}     # upgrade_id -> level
self.damage_taken=0  # for no-damage achievement
self.level_start_damage=0

```
@property
def speed(self):
    bonus = self.upgrades.get("move_speed",0)*0.8
    return self.base_speed + bonus

def get_cooldown(self):
    cd=self.base_cooldown
    if "rapid" in self.active_powerups: cd=max(4,cd//3)
    reduction=self.upgrades.get("cooldown_red",0)*0.10
    reduction+=self.upgrades.get("fire_rate",0)*0.15
    cd=int(cd*(1-reduction))
    return max(3,cd)

def has(self,pid): return pid in self.active_powerups

def add_powerup(self,pid,duration):
    if duration>0: self.active_powerups[pid]=duration*FPS
    if pid=="shield": self.shield_hp=3+self.upgrades.get("shield_regen",0)
    elif pid=="life": self.lives=min(self.lives+1,self.max_lives)

def update_powerups(self):
    expired=[pid for pid,t in self.active_powerups.items() if t<=1]
    for pid in expired:
        del self.active_powerups[pid]
        if pid=="shield": self.shield_hp=0
    for pid in list(self.active_powerups):
        if pid in self.active_powerups:
            self.active_powerups[pid]-=1

def fire(self, enemies=None):
    bullets=[]; cx=self.x; cy=self.y-18
    dmg=1+self.upgrades.get("bullet_dmg",0)
    piercing=self.upgrades.get("piercing",0)>0
    multishot=self.upgrades.get("multishot",0)
    crit=random.random()<self.upgrades.get("crit_chance",0)*0.10
    dmg=dmg*2 if crit else dmg

    base_col=self.color
    def mk(x,y,dy,dx=0,btype="normal",w=4,h=14,color=None):
        return {"x":x,"y":y,"dy":dy,"dx":dx,"type":btype,"w":w,"h":h,
                "color":color or base_col,"dmg":dmg,"piercing":piercing,"crit":crit}

    if self.has("laser"):
        bullets.append(mk(cx,cy,-18,btype="laser",w=4,h=30,color="#ff0088"))
    elif self.has("wide"):
        for dx in range(-20,25,10):
            bullets.append(mk(cx+dx,cy,-10,btype="wide",w=8,h=12,color="#ff00ff"))
    elif self.has("triple"):
        bullets.append(mk(cx,cy,-12)); bullets.append(mk(cx,cy,-11,-2,color=C["cyan"]))
        bullets.append(mk(cx,cy,-11,2,color=C["cyan"]))
    elif self.has("dual"):
        bullets.append(mk(cx-15,cy,-12,color=C["green"]))
        bullets.append(mk(cx+15,cy,-12,color=C["green"]))
    elif self.has("homing") and enemies:
        target=min(enemies,key=lambda e:abs(e.x-cx)+abs(e.y-cy))
        dx_=(target.x-cx)/(abs(target.x-cx)+1)*5
        bullets.append(mk(cx,cy,-10,dx_,btype="homing",w=8,h=8,color="#ff4400"))
    else:
        bullets.append(mk(cx,cy,-12))

    # Multishot upgrade: add side shots
    if multishot>0:
        for side in [-18,18]:
            bullets.append(mk(cx+side,cy,-11,side*0.1,color=C["cyan"]))

    return bullets

def draw(self,canvas,tick=0):
    x,y=self.x,self.y
    col="#ffffff" if self.invincible%(FPS//5)<(FPS//10) and self.invincible>0 else self.color
    if self.invincible>0 and self.invincible%(FPS//5)>=(FPS//10):
        return  # blink off

    # Engine glow
    canvas.create_oval(x-10,y+10,x+10,y+26,fill="#001133",outline="")
    for dx2,gy in [(-10,22),(0,26),(10,22)]:
        sz=5
        canvas.create_oval(x+dx2-sz,y+gy,x+dx2+sz,y+gy+8,fill="#0055ff",outline="")

    body=[(x,y-14),(x+6,y-4),(x+18,y+10),(x+14,y+14),(x+6,y+10),
          (x,y+6),(x-6,y+10),(-14+x,y+14),(x-18,y+10),(x-6,y-4)]
    canvas.create_polygon(body,fill=col,outline=C["cyan"],width=1)
    canvas.create_oval(x-5,y-10,x+5,y+2,fill="#001133",outline=C["cyan"],width=1)
    canvas.create_line(x,y-14,x,y+6,fill=C["cyan"],width=1)

    # Shield ring
    if self.shield_hp>0:
        r=30+self.shield_hp*3
        canvas.create_oval(x-r,y-r,x+r,y+r,fill="",outline=C["shield"],width=2)
        canvas.create_oval(x-r+4,y-r+4,x+r-4,y+r-4,fill="",outline="#0044cc",width=1)
```

# ══════════════════════════════════════════════════════

# DRAW HELPERS

# ══════════════════════════════════════════════════════

def neon(canvas,x,y,text,color,size=16,glow=True,anchor=“center”,family=“Courier”):
fnt=(family,size,“bold”)
if glow:
c=color.lstrip(”#”); r,g,b=int(c[0:2],16)//4,int(c[2:4],16)//4,int(c[4:6],16)//4
dim=f”#{r:02x}{g:02x}{b:02x}”
for off in [(2,2),(-2,-2),(2,-2),(-2,2),(3,0),(-3,0),(0,3),(0,-3)]:
canvas.create_text(x+off[0],y+off[1],text=text,fill=dim,font=fnt,anchor=anchor)
canvas.create_text(x,y,text=text,fill=color,font=fnt,anchor=anchor)

def draw_bullet(canvas,b):
btype=b.get(“type”,“normal”); x,y=b[“x”],b[“y”]
w,h=b.get(“w”,4),b.get(“h”,14); col=b.get(“color”,C[“bullet”])
crit=b.get(“crit”,False)
if btype==“laser”:
canvas.create_rectangle(x-w//2,y-h,x+w//2,y+h,fill=col,outline=”#ffffff”,width=1)
canvas.create_rectangle(x-w,y-h,x+w,y+h,fill=””,outline=col,width=1)
elif btype in(“enemy”,“enemy_spiral”):
canvas.create_oval(x-w//2,y-h//2,x+w//2,y+h//2,fill=col,outline=”#ff8844”,width=1)
elif btype==“homing”:
pts=[(x,y-h//2),(x+w//2,y),(x,y+h//2),(x-w//2,y)]
canvas.create_polygon(pts,fill=col,outline=”#ffaa00”,width=1)
elif btype==“wide”:
canvas.create_rectangle(x-w//2,y-h//2,x+w//2,y+h//2,fill=col,outline=””)
else:
outline_col=”#ffff00” if crit else “”
canvas.create_rectangle(x-w//2,y-h,x+w//2,y,fill=col,outline=outline_col,width=1 if crit else 0)
canvas.create_rectangle(x-1,y-h-4,x+1,y-h,fill=”#ffffff”,outline=””)

def draw_powerup(canvas,pu,tick):
x,y=pu[“x”],pu[“y”]; t=pu[“t”]; col=pu[“data”][“color”]
bob=math.sin(t*0.08)*4; r=16
for i in range(6):
a=math.tau*i/6+t*0.04; rx=x+math.cos(a)*(r+5); ry=y+bob+math.sin(a)*(r+5)
canvas.create_oval(rx-3,ry-3,rx+3,ry+3,fill=col,outline=””)
canvas.create_oval(x-r,y-r+bob,x+r,y+r+bob,fill=”#111133”,outline=col,width=2)
canvas.create_text(x,y+bob,text=pu[“data”][“sym”],fill=col,font=(“Courier”,11,“bold”))

# ══════════════════════════════════════════════════════

# FORMATION GENERATOR

# ══════════════════════════════════════════════════════

def generate_formation(formation, cols, rows, tier):
positions=[]
cx=W//2; sy=95

```
if formation=="grid":
    sx=(W-(cols*55))//2+27
    for r in range(rows):
        for c in range(cols):
            positions.append((sx+c*55, sy+r*45, min(r,2)))

elif formation=="v_shape":
    for r in range(rows):
        half=max(1,cols//2-r)
        for c in range(-half,half+1):
            positions.append((cx+c*50, sy+r*42, min(r,2)))

elif formation=="diamond":
    center_r=rows//2
    for r in range(rows):
        dist=abs(r-center_r); n_this=max(1,cols-dist*2)
        for c in range(n_this):
            x=cx+(c-(n_this-1)/2)*52
            positions.append((x, sy+r*40, min(r%3,2)))

elif formation=="x_shape":
    for r in range(rows):
        for c in range(cols):
            if abs(c-cols//2)==r or abs(c-cols//2)==rows-1-r:
                positions.append((cx+(c-cols//2)*50, sy+r*40, min((r+c)%3,2)))

elif formation=="zigzag":
    for r in range(rows):
        offset=20 if r%2==0 else -20
        sx2=(W-(cols*50))//2+25
        for c in range(cols):
            positions.append((sx2+c*50+offset, sy+r*40, min(r%3,2)))

elif formation=="spiral":
    angle=0; radius=30; step=22
    for i in range(cols*rows):
        x=cx+math.cos(angle)*radius; y=sy+math.sin(angle)*radius*0.5+rows*20
        if 20<x<W-20 and y>20:
            positions.append((x,y,i%3))
        angle+=0.5; radius+=step*0.15

elif formation=="wings":
    for r in range(rows):
        for c in range(cols):
            mid=cols//2
            if abs(c-mid)>=r or r==0:
                positions.append((cx+(c-mid)*50, sy+r*38, min(r%3,2)))

elif formation=="double_arc":
    for arc in range(2):
        for i in range(cols):
            a=math.pi*i/(cols-1)
            x=cx+math.cos(a)*200*(1 if arc==0 else -1)
            y=sy+math.sin(a)*80+arc*50
            positions.append((x,y,arc%3))

else:
    return generate_formation("grid",cols,rows,tier)

return positions
```

# ══════════════════════════════════════════════════════

# STARFIELD

# ══════════════════════════════════════════════════════

class StarField:
def **init**(self):
self.stars=[{“x”:random.uniform(0,W),“y”:random.uniform(0,H),
“speed”:random.uniform(0.3,2.5),“size”:random.uniform(0.5,2.5),
“bright”:random.uniform(0.2,1.0),“twinkle”:random.uniform(0,math.tau)}
for _ in range(200)]
def update(self,spd=1.0):
for s in self.stars:
s[“y”]+=s[“speed”]*spd; s[“twinkle”]+=0.04
if s[“y”]>H: s[“y”]=-2; s[“x”]=random.uniform(0,W)
def draw(self,canvas):
for s in self.stars:
br=s[“bright”]*(0.7+0.3*math.sin(s[“twinkle”]))
v=int(br*220); col=f”#{v:02x}{v:02x}{min(255,v+35):02x}”
sz=s[“size”]
canvas.create_oval(s[“x”]-sz,s[“y”]-sz,s[“x”]+sz,s[“y”]+sz,fill=col,outline=””)

# ══════════════════════════════════════════════════════

# UPGRADE SCREEN

# ══════════════════════════════════════════════════════

class UpgradeScreen:
def **init**(self, player_upgrades):
self.choices = self._pick_3(player_upgrades)
self.selected = None
self.hover = 0

```
def _pick_3(self, current):
    available=[]
    for u in ALL_UPGRADES:
        cur=current.get(u["id"],0)
        if cur < u["max"]:
            available.append(dict(u, current_level=cur))
    random.shuffle(available)
    return available[:3]

def draw(self,canvas,tick):
    canvas.create_rectangle(0,0,W,H,fill="#000000",stipple="gray50",outline="")
    canvas.create_rectangle(W//2-380,80,W//2+380,H-80,fill="#040418",outline=C["cyan"],width=2)
    neon(canvas,W//2,115,"⚙  UPGRADE YOUR SHIP  ⚙",C["cyan"],size=22,glow=True)
    neon(canvas,W//2,148,"Choose one permanent upgrade",C["dim"],size=12,glow=False)

    card_w=210; card_h=220; gap=20
    total_w=len(self.choices)*card_w+(len(self.choices)-1)*gap
    x0=W//2-total_w//2

    for i,u in enumerate(self.choices):
        cx2=x0+i*(card_w+gap)+card_w//2; cy2=H//2+10
        is_hov=(i==self.hover)
        border_col=u["color"] if is_hov else C["dim"]
        fill="#0a0a28" if not is_hov else "#101030"
        glow2=4 if is_hov else 0
        # Shadow glow
        if is_hov:
            for g2 in range(6,0,-2):
                canvas.create_rectangle(cx2-card_w//2-g2,cy2-card_h//2-g2,
                                       cx2+card_w//2+g2,cy2+card_h//2+g2,
                                       fill="",outline=u["color"],width=1)
        canvas.create_rectangle(cx2-card_w//2,cy2-card_h//2,
                               cx2+card_w//2,cy2+card_h//2,
                               fill=fill,outline=border_col,width=2)
        # Symbol
        neon(canvas,cx2,cy2-70,u["sym"],u["color"],size=32,glow=is_hov)
        # Name
        neon(canvas,cx2,cy2-28,u["name"],u["color"],size=13,glow=is_hov)
        # Desc
        canvas.create_text(cx2,cy2+10,text=u["desc"],fill=C["white"],
                          font=("Courier",10,"bold"),width=card_w-20)
        # Level pips
        cur=u["current_level"]; mx=u["max"]
        for j in range(mx):
            fc=u["color"] if j<cur else "#222244"
            canvas.create_rectangle(cx2-mx*9//2+j*9,cy2+50,
                                   cx2-mx*9//2+j*9+7,cy2+60,fill=fc,outline="")
        canvas.create_text(cx2,cy2+75,text=f"Level {cur+1}/{mx}",
                          fill=u["color"],font=("Courier",9))
        # Key hint
        neon(canvas,cx2,cy2+card_h//2-18,f"[ {i+1} ]",C["white"],size=12,glow=False)

    if (tick//30)%2==0:
        neon(canvas,W//2,H-110,"Press 1 / 2 / 3  or  LEFT/RIGHT + ENTER",
             C["dim"],size=11,glow=False)
```

# ══════════════════════════════════════════════════════

# ACHIEVEMENT POPUP

# ══════════════════════════════════════════════════════

class AchievementPopup:
def **init**(self,ach):
self.ach=ach; self.life=FPS*4; self.max_life=self.life
def update(self): self.life-=1
def alive(self): return self.life>0
def draw(self,canvas):
ratio=self.life/self.max_life
alpha=min(1.0,ratio*5)*(1 if ratio>0.2 else ratio/0.2)
y=H-90-max(0,(1-ratio)*30)
v=int(alpha*255)
col=self.ach[“color”]
canvas.create_rectangle(W-280,y-28,W-10,y+28,
fill=f”#080818”,outline=col,width=2)
canvas.create_text(W-270,y,text=f”{self.ach[‘sym’]} ACHIEVEMENT!”,
fill=col,font=(“Courier”,9,“bold”),anchor=“w”)
canvas.create_text(W-270,y+14,text=self.ach[“name”],
fill=”#ffffff”,font=(“Courier”,11,“bold”),anchor=“w”)

# ══════════════════════════════════════════════════════

# MAIN GAME

# ══════════════════════════════════════════════════════

class GalacticSiege:
def **init**(self):
self.root=tk.Tk()
self.root.title(“GALACTIC SIEGE v2”)
self.root.configure(bg=C[“bg”])
self.root.resizable(False,False)
self.canvas=tk.Canvas(self.root,width=W,height=H,bg=C[“bg”],highlightthickness=0)
self.canvas.pack()

```
    self.save=load_save()
    self.state="menu"
    self.keys=set(); self.tick=0
    self.player_name=""
    self.mode="story"       # story | endless
    self.selected_skin="default"
    self.upgrade_screen=None
    self.achievement_popups=[]
    self.pending_achievements=[]

    self.stars=StarField()
    self.ufo=UFO()
    self.asteroids=[]
    self.weather=None
    self.weather_timer=0
    self.lightning_strikes=[]
    self.nebula_opacity=0

    # Speed pulse
    self.speed_pulse=0
    self.speed_pulse_col="#ff2244"

    # Chain explosion tracking
    self.chain_kills=[]

    # Menu state
    self.menu_cursor=0  # 0=story 1=endless 2=skins 3=scores
    self.skin_cursor=0

    self.grid_offset=0
    self.scan_line=0

    self.reset_game()

    self.root.bind("<KeyPress>",   self.key_down)
    self.root.bind("<KeyRelease>", self.key_up)
    self.root.bind("<Escape>",     self.on_escape)
    self.loop()
    self.root.mainloop()

# ── Input ────────────────────────────────────────
def key_down(self,e):
    k=e.keysym; self.keys.add(k)

    if self.state=="menu":
        if k in("Up","w"): self.menu_cursor=(self.menu_cursor-1)%4
        elif k in("Down","s"): self.menu_cursor=(self.menu_cursor+1)%4
        elif k=="Return":
            opts=["story","endless","skins","scores"]
            choice=opts[self.menu_cursor]
            if choice=="story": self.mode="story"; self.start_game()
            elif choice=="endless": self.mode="endless"; self.start_game()
            elif choice=="skins": self.state="skins"
            elif choice=="scores": self.state="highscore"

    elif self.state=="skins":
        unlocked=[s for s in SKINS if s["id"] in self.save["unlocked_skins"]]
        if k in("Left","a"): self.skin_cursor=(self.skin_cursor-1)%len(unlocked)
        elif k in("Right","d"): self.skin_cursor=(self.skin_cursor+1)%len(unlocked)
        elif k=="Return":
            self.selected_skin=unlocked[self.skin_cursor]["id"]
            self.state="menu"
        elif k=="Escape": self.state="menu"

    elif self.state=="highscore":
        if k in("Return","Escape"): self.state="menu"

    elif self.state=="game_over":
        if k=="Return": self.state="enter_name"; self.player_name=""

    elif self.state=="enter_name":
        if k=="Return" and self.player_name:
            add_highscore(self.save,self.player_name,self.player.score,
                         self.current_level,self.mode)
            if self.mode=="endless" and self.current_level>self.save.get("endless_best",0):
                self.save["endless_best"]=self.current_level
            write_save(self.save)
            self.state="highscore"
        elif k=="BackSpace": self.player_name=self.player_name[:-1]
        elif len(e.char)==1 and e.char.isprintable() and len(self.player_name)<12:
            self.player_name+=e.char.upper()

    elif self.state=="upgrade":
        if self.upgrade_screen:
            idx=None
            if k=="1" or (k=="Left" and self.upgrade_screen.hover>0):
                if k=="1": idx=0
                else: self.upgrade_screen.hover=max(0,self.upgrade_screen.hover-1)
            elif k=="2": idx=1
            elif k=="3": idx=2
            elif k in("Right","d"):
                self.upgrade_screen.hover=min(2,self.upgrade_screen.hover+1)
            elif k=="Return": idx=self.upgrade_screen.hover
            if idx is not None and idx<len(self.upgrade_screen.choices):
                self._apply_upgrade(self.upgrade_screen.choices[idx])

    elif self.state=="level_clear":
        if k=="Return": self._go_upgrade_or_next()

    elif self.state=="playing":
        if k=="space": self.try_shoot()
        if k=="p": self.state="paused"

    elif self.state=="paused":
        if k=="p" or k=="Return": self.state="playing"

def key_up(self,e): self.keys.discard(e.keysym)

def on_escape(self,e=None):
    if self.state=="playing": self.state="paused"
    elif self.state=="paused": self.state="playing"
    elif self.state in("skins","highscore","upgrade"): self.state="menu"

# ── Game Setup ───────────────────────────────────
def start_game(self):
    skin_data=next((s for s in SKINS if s["id"]==self.selected_skin),SKINS[0])
    self.player=Player(skin_data["color"])
    self.current_level=0
    self.particles=[]; self.combo_hits=[]
    self.ufo=UFO()
    self.asteroids=[]
    self.weather=None; self.weather_timer=0
    self.lightning_strikes=[]
    self.nebula_opacity=0
    self.speed_pulse=0
    self.chain_kills=[]
    self.level_start_time=time.time()
    self.level_damage_start=0
    self._next_level_number()
    self.state="playing"

def reset_game(self):
    self.player=Player()
    self.current_level=0; self.enemies=[]; self.bunkers=[]
    self.player_bullets=[]; self.enemy_bullets=[]; self.powerups_on_field=[]
    self.particles=[]; self.combo_hits=[]; self.boss=None; self.boss_active=False
    self.level_cfg=make_level(1); self.msg_text=""; self.msg_timer=0
    self.ufo=UFO(); self.asteroids=[]; self.weather=None
    self.weather_timer=0; self.lightning_strikes=[]; self.nebula_opacity=0
    self.speed_pulse=0; self.chain_kills=[]; self.level_start_time=time.time()
    self.level_damage_start=0; self.enemy_dir=1; self.enemy_move_timer=0
    self.achievement_popups=[]; self.upgrade_screen=None

def _next_level_number(self):
    self.current_level+=1
    self.load_level(self.current_level)

def load_level(self,n):
    cfg=make_level(n, endless=(self.mode=="endless"))
    self.level_cfg=cfg
    self.enemies=[]; self.player_bullets=[]; self.enemy_bullets=[]
    self.powerups_on_field=[]; self.boss=None
    self.boss_active=cfg["is_boss"]
    self.enemy_dir=1; self.enemy_move_timer=0
    self.level_start_time=time.time()
    self.level_damage_start=self.player.damage_taken
    self.asteroids=[]; self.lightning_strikes=[]

    # Weather
    self.weather=cfg.get("weather")
    self.weather_timer=FPS*20 if self.weather else 0
    self.nebula_opacity=0.5 if self.weather and self.weather["id"]=="nebula" else 0

    if self.boss_active:
        self.boss=Boss(cfg,n)
    else:
        positions=generate_formation(cfg["formation"],cfg["cols"],cfg["rows"],cfg["tier"])
        for x,y,etype in positions:
            self.enemies.append(Enemy(x,y,etype,cfg["tier"]))

    # Place bunkers (3 bunkers, story mode)
    if not self.mode=="endless" or n%3==0:
        self.bunkers=[]
        for bx in [W//4, W//2, 3*W//4]:
            self.bunkers.append(Bunker(bx, H-160))

    self.enemy_speed_x=cfg["enemy_speed"]
    tier_col=[C["green"],C["cyan"],C["yellow"],C["orange"],C["magenta"]][cfg["tier"]]
    wname=f"  ⚡ {self.weather['name']}" if self.weather else ""
    self.show_msg(f"LEVEL {n}  {cfg['tier_name']}{wname}",2.5)

def _go_upgrade_or_next(self):
    upgrades=ALL_UPGRADES
    unlocked_count=sum(self.player.upgrades.get(u["id"],0) for u in upgrades)
    # Offer upgrade every level
    self.upgrade_screen=UpgradeScreen(self.player.upgrades)
    if self.upgrade_screen.choices:
        self.state="upgrade"
    else:
        self._next_level_number()
        self.state="playing"

def _apply_upgrade(self,u):
    uid=u["id"]; cur=self.player.upgrades.get(uid,0)
    self.player.upgrades[uid]=cur+1
    self.show_msg(f"✦ {u['name']} UPGRADED! ✦",2)
    # Check max achievement
    if cur+1>=u["max"]:
        self.unlock_achievement("max_upgrade")
    self.upgrade_screen=None
    self._next_level_number()
    self.state="playing"

# ── Achievements ─────────────────────────────────
def unlock_achievement(self,aid):
    if aid not in self.save["achievements"]:
        ach=next((a for a in ACHIEVEMENTS if a["id"]==aid),None)
        if ach:
            self.save["achievements"].append(aid)
            write_save(self.save)
            self.achievement_popups.append(AchievementPopup(ach))
            self.show_msg(f"🏆 {ach['name']}!",1.5)

def check_achievements(self):
    p=self.player
    if len(self.enemies)==0 and not self.boss_active:
        if p.damage_taken==self.level_damage_start:
            self.unlock_achievement("no_damage")
    if p.combo>=10: self.unlock_achievement("combo_10")
    if p.combo>=50: self.unlock_achievement("combo_50")
    if p.score>=100000: self.unlock_achievement("score_100k")
    if self.current_level>=15 and self.mode=="story":
        self.unlock_achievement("level_15")
    if self.mode=="endless" and self.current_level>=10:
        self.unlock_achievement("endless_10")
    unlocked_skins=self.save.get("unlocked_skins",["default"])
    if len(unlocked_skins)>=len(SKINS):
        self.unlock_achievement("all_skins")

def check_skin_unlocks(self):
    p=self.player; saves=self.save
    def try_unlock(skin_id):
        if skin_id not in saves.get("unlocked_skins",["default"]):
            saves.setdefault("unlocked_skins",["default"]).append(skin_id)
            write_save(saves)
            skin=next(s for s in SKINS if s["id"]==skin_id)
            self.show_msg(f"🎖 SKIN UNLOCKED: {skin['name']}!",2.5)
    if p.score>=10000: try_unlock("fire")
    if "phantom" in saves.get("achievements",[]): try_unlock("phantom")
    if p.score>=50000: try_unlock("golden")
    if self.current_level>=10: try_unlock("neon")
    if self.mode=="endless" and self.current_level>=10: try_unlock("storm")

# ── Helpers ──────────────────────────────────────
def show_msg(self,text,dur=2.0):
    self.msg_text=text; self.msg_timer=int(dur*FPS)

def try_shoot(self):
    p=self.player
    if self.weather and self.weather["id"]=="emp" and self.weather_timer>0:
        return  # weapons offline
    if p.shoot_cooldown<=0 and self.state=="playing":
        bullets=p.fire(self.enemies if self.enemies else None)
        self.player_bullets.extend(bullets)
        p.shoot_cooldown=p.get_cooldown()
        if p.has("bomb"):
            del p.active_powerups["bomb"]; self.nova_bomb()

def nova_bomb(self):
    for e in self.enemies[:]:
        explode(self.particles,e.x,e.y,e.color,15)
        self.player.score+=e.pts()*max(1,self.player.combo)
    self.enemies.clear()
    if self.boss: self.boss.hp-=200
    explode(self.particles,self.player.x,self.player.y,"#ff8800",60)
    self.show_msg("☢ NOVA BOMB!",1.5)

# ── Update ───────────────────────────────────────
def update(self):
    self.tick+=1
    self.stars.update(self.level_cfg.get("bg_speed",0.5))
    self.scan_line=(self.scan_line+2)%H
    self.grid_offset=(self.grid_offset+0.5)%40
    if self.speed_pulse>0: self.speed_pulse-=1

    # Achievement popups
    for ap in self.achievement_popups[:]:
        ap.update()
        if not ap.alive(): self.achievement_popups.remove(ap)

    if self.state!="playing": return

    p=self.player
    cfg=self.level_cfg

    # Movement
    if "Left" in self.keys or "a" in self.keys: p.x=max(22,p.x-p.speed)
    if "Right" in self.keys or "d" in self.keys: p.x=min(W-22,p.x+p.speed)
    if "space" in self.keys: self.try_shoot()

    # Cooldowns/timers
    if p.shoot_cooldown>0: p.shoot_cooldown-=1
    if p.invincible>0: p.invincible-=1
    if p.combo_timer>0: p.combo_timer-=1
    else: p.combo=0
    p.update_powerups()

    # Auto-shield upgrade
    if p.upgrades.get("auto_shield",0)>0 and p.lives==1 and p.shield_hp==0:
        if "shield" not in p.active_powerups:
            p.add_powerup("shield",5)
            self.show_msg("⚡ AUTO-SHIELD ACTIVATED",1)

    # Trail
    p.trail.append((p.x,p.y+14))
    if len(p.trail)>12: p.trail.pop(0)

    if self.msg_timer>0: self.msg_timer-=1

    # UFO
    self.ufo.update()

    # Weather
    self._update_weather()

    # Speed pulse: fewer enemies = faster + visual effect
    if not self.boss_active:
        total_start=cfg["cols"]*cfg["rows"] if not cfg["is_boss"] else 1
        if len(self.enemies)>0:
            ratio=len(self.enemies)/max(1,total_start)
            self.enemy_speed_x=cfg["enemy_speed"]*(1+1.2*(1-ratio))
            if ratio<0.25 and self.tick%30==0:
                self.speed_pulse=15
                self.speed_pulse_col="#ff2244"

    # Move player bullets
    slowmo=0.5 if p.has("slowmo") else 1.0
    gravity_on = self.weather and self.weather["id"]=="gravity" and self.weather_timer>0
    for b in self.player_bullets[:]:
        b["x"]+=b.get("dx",0)
        b["y"]+=b["dy"]*slowmo
        if gravity_on: b["dy"]=min(b["dy"]+0.3, 0)  # pull toward less negative
        if b["y"]<-30 or b["y"]>H+10:
            if b in self.player_bullets: self.player_bullets.remove(b)
            continue
        # Homing steering
        if b.get("type")=="homing" and self.enemies:
            t2=min(self.enemies,key=lambda e:math.hypot(e.x-b["x"],e.y-b["y"]))
            dx_=(t2.x-b["x"]); turn=max(-4,min(4,dx_*0.12))
            b["dx"]=max(-9,min(9,b.get("dx",0)+turn*0.2))

    # Move enemy bullets
    for b in self.enemy_bullets[:]:
        b["x"]+=b.get("dx",0)*slowmo
        b["y"]+=b.get("dy",4)*slowmo
        if b["y"]>H+20 or b["x"]<-20 or b["x"]>W+20:
            self.enemy_bullets.remove(b)

    # Move powerups
    for pu in self.powerups_on_field[:]:
        pu["y"]+=1.2; pu["t"]+=1
        if p.has("magnet"):
            dx_=p.x-pu["x"]; dy_=p.y-pu["y"]
            d=math.hypot(dx_,dy_)+1
            pu["x"]+=dx_/d*9; pu["y"]+=dy_/d*9
        if pu["y"]>H+30: self.powerups_on_field.remove(pu)

    # Enemies
    if not self.boss_active:
        self.enemy_move_timer+=1
        mi=max(3,int(28-cfg["enemy_speed"]*4))
        if self.enemy_move_timer>=mi:
            self.enemy_move_timer=0; self._move_enemies()
        for e in self.enemies:
            if random.random()<cfg["shoot_chance"]*slowmo:
                self.enemy_bullets.append({"x":e.x,"y":e.y+10,
                    "dy":3+cfg["tier"]*0.7,"dx":0,"type":"enemy","w":6,"h":6,"color":e.color})
    else:
        if self.boss: self.boss.update()
        if self.boss and self.boss.should_shoot():
            self.enemy_bullets.extend(self.boss.fire())

    # Wormhole: random enemy teleport
    if self.weather and self.weather["id"]=="wormhole" and self.weather_timer>0:
        if self.tick%90==0 and self.enemies:
            e=random.choice(self.enemies)
            e.x=random.uniform(30,W-30); e.y=random.uniform(90,300)

    # Collisions
    self._collide_bullets_enemies()
    self._collide_bullets_bunkers()
    self._collide_enemy_bullets_player()
    self._collide_powerups()
    self._collide_ufo()
    self._collide_asteroids_player()

    # Particles
    for part in self.particles[:]:
        part.update()
        if not part.alive(): self.particles.remove(part)
        else:
            # Cap particles for performance
            pass
    if len(self.particles)>500:
        self.particles=self.particles[-400:]

    # Chain kills cleanup
    now=time.time()
    self.chain_kills=[k for k in self.chain_kills if now-k["t"]<0.4]

    # Powerup random spawn
    luck=1+self.player.upgrades.get("luck",0)*0.2
    if random.random()<cfg["powerup_freq"]*luck:
        if len(self.powerups_on_field)<5:
            data=random.choice(POWERUPS)
            self.powerups_on_field.append({"x":random.randint(30,W-30),
                                           "y":-20,"t":0,"data":data})

    # Win check
    if not self.boss_active and len(self.enemies)==0:
        bonus=500*self.current_level
        sb=self.player.upgrades.get("score_boost",0)*0.25
        bonus=int(bonus*(1+sb))
        self.player.score+=bonus
        self.check_achievements()
        self.check_skin_unlocks()
        if self.mode=="story" and self.current_level>=15:
            self.unlock_achievement("level_15")
            self.state="game_over"
        else:
            self.state="level_clear"
            self.show_msg(f"LEVEL {self.current_level} CLEAR! +{bonus}",2)
        # Speedrun achievement
        if self.current_level==1 and time.time()-self.level_start_time<30:
            self.unlock_achievement("speedrun_1")

    elif self.boss_active and self.boss and self.boss.hp<=0:
        explode(self.particles,self.boss.x,self.boss.y,C["boss"],80)
        boss_pts=5000*self.current_level
        sb=self.player.upgrades.get("score_boost",0)*0.25
        boss_pts=int(boss_pts*(1+sb))
        self.player.score+=boss_pts
        self.boss=None
        self.unlock_achievement("boss_kill")
        if self.weather: self.unlock_achievement("weather_boss")
        self.check_achievements()
        self.check_skin_unlocks()
        if self.mode=="story" and self.current_level>=15:
            self.state="game_over"
        else:
            self.state="level_clear"
            self.show_msg(f"BOSS DEFEATED! +{boss_pts}",2)

    # Enemies reach bottom
    for e in self.enemies:
        if e.y>H-90: self._player_die(); break

def _update_weather(self):
    if not self.weather: return
    wid=self.weather["id"]
    if self.weather_timer>0: self.weather_timer-=1
    else: self.weather=None; self.nebula_opacity=0; return

    if wid=="asteroid":
        if self.tick%40==0: self.asteroids.append(Asteroid())
        for ast in self.asteroids[:]:
            ast.update()
            if not ast.alive(): self.asteroids.remove(ast)

    elif wid=="storm":
        if self.tick%70==0:
            lx=random.randint(30,W-30)
            self.lightning_strikes.append({"x":lx,"y":0,"life":12,"max_life":12})
        for ls in self.lightning_strikes[:]:
            ls["life"]-=1
            if ls["life"]<=0: self.lightning_strikes.remove(ls)
            else:
                # Damage player?
                p=self.player
                if abs(ls["x"]-p.x)<20 and p.invincible==0:
                    self._player_die()

def _move_enemies(self):
    hit=False
    for e in self.enemies:
        e.x+=self.enemy_speed_x*self.enemy_dir
    for e in self.enemies:
        if (self.enemy_dir>0 and e.x>W-25) or (self.enemy_dir<0 and e.x<25):
            hit=True; break
    if hit:
        self.enemy_dir*=-1
        drop=self.level_cfg["enemy_drop"]
        for e in self.enemies:
            e.y+=drop
            e.x+=self.enemy_speed_x*self.enemy_dir*2

def _collide_bullets_enemies(self):
    p=self.player
    score_mult=2 if p.has("score2x") else 1
    sb=1+p.upgrades.get("score_boost",0)*0.25
    now=time.time()

    for b in self.player_bullets[:]:
        bx,by=b["x"],b["y"]; bw,bh=b.get("w",4),b.get("h",14)
        dmg=b.get("dmg",1); piercing=b.get("piercing",False)
        hit_count=0

        for e in self.enemies[:]:
            if abs(bx-e.x)<16+bw//2 and abs(by-e.y)<14+bh//2:
                e.hp-=dmg; e.hit_flash=6; hit_count+=1
                if e.hp<=0:
                    pts=int(e.pts()*score_mult*sb)
                    self._add_combo(pts,e.x,e.y)
                    explode(self.particles,e.x,e.y,e.color,18)
                    self.enemies.remove(e)
                    # Chain explosion tracking
                    self.chain_kills.append({"x":e.x,"y":e.y,"t":now})
                    if len(self.chain_kills)>=5:
                        self._trigger_chain()
                    if random.random()<0.18+p.upgrades.get("luck",0)*0.05:
                        self._spawn_pu(e.x,e.y)
                    if not self.save["achievements"] or "first_kill" not in self.save["achievements"]:
                        self.unlock_achievement("first_kill")
                    # Shield regen on kill
                    if p.upgrades.get("shield_regen",0)>0 and p.shield_hp>0:
                        p.shield_hp=min(p.shield_hp+1, 5)
                if not piercing and b.get("type")!="laser":
                    break

        # vs boss
        if self.boss_active and self.boss:
            bs=self.boss.size
            if abs(bx-self.boss.x)<bs and abs(by-self.boss.y)<bs*0.7:
                d2=8 if b.get("type")=="laser" else 6 if b.get("type")=="homing" else dmg*3
                self.boss.hp-=d2; self.boss.hit_flash=5
                pts=int(d2*5*score_mult*sb)
                self._add_combo(pts,bx,by); hit_count+=1

        if hit_count>0 and b.get("type")!="laser":
            if b in self.player_bullets: self.player_bullets.remove(b)

def _trigger_chain(self):
    cx=sum(k["x"] for k in self.chain_kills)/len(self.chain_kills)
    cy=sum(k["y"] for k in self.chain_kills)/len(self.chain_kills)
    bonus=int(len(self.chain_kills)*150*(1+self.player.upgrades.get("chain_power",0)*0.5))
    self.player.score+=bonus
    explode(self.particles,cx,cy,"#ffaa00",35)
    self.show_msg(f"⛓ CHAIN x{len(self.chain_kills)}! +{bonus}",1.5)
    self.chain_kills.clear()
    if len(self.chain_kills)>=5:
        self.unlock_achievement("chain_5")

def _collide_bullets_bunkers(self):
    for b in self.player_bullets[:]:
        for bk in self.bunkers:
            if bk.blocks(b["x"],b["y"]):
                if b in self.player_bullets: self.player_bullets.remove(b)
                break
    for b in self.enemy_bullets[:]:
        for bk in self.bunkers:
            if bk.hp>0 and bk.hit(b["x"],b["y"]):
                if b in self.enemy_bullets: self.enemy_bullets.remove(b)
                break
    for ast in self.asteroids:
        for bk in self.bunkers:
            if abs(ast.x-bk.cx)<bk.cols*bk.SEG_W//2 and abs(ast.y-bk.y-bk.rows*bk.SEG_H//2)<bk.rows*bk.SEG_H:
                bk.hit(ast.x,ast.y)

def _collide_enemy_bullets_player(self):
    p=self.player
    if p.invincible>0: return
    for b in self.enemy_bullets[:]:
        if abs(b["x"]-p.x)<18 and abs(b["y"]-p.y)<18:
            self.enemy_bullets.remove(b)
            if p.shield_hp>0:
                p.shield_hp-=1
                if p.shield_hp<=0 and "shield" in p.active_powerups:
                    del p.active_powerups["shield"]
                explode(self.particles,b["x"],b["y"],C["shield"],10)
                # Bunker save achievement check (shield acts like bunker)
                self.unlock_achievement("bunker_last")
            else:
                self._player_die()
            break

def _collide_powerups(self):
    p=self.player
    for pu in self.powerups_on_field[:]:
        if abs(pu["x"]-p.x)<24 and abs(pu["y"]-p.y)<24:
            d=pu["data"]
            p.add_powerup(d["id"],d["dur"])
            explode(self.particles,pu["x"],pu["y"],d["color"],15)
            self.show_msg(f"⬡ {d['name']}",1.5)
            self.powerups_on_field.remove(pu)

def _collide_ufo(self):
    if not self.ufo.active: return
    p=self.player
    for b in self.player_bullets[:]:
        if abs(b["x"]-self.ufo.x)<38 and abs(b["y"]-self.ufo.y)<18:
            self.ufo.hp-=1
            if b in self.player_bullets: self.player_bullets.remove(b)
            if self.ufo.hp<=0:
                self.ufo.active=False
                # Reward!
                reward=random.choice(["score_big","life","random_powerup","shield"])
                if reward=="score_big":
                    big=random.randint(1,9)*100
                    self.player.score+=big
                    self.show_msg(f"★ UFO: +{big} PTS! ★",2)
                elif reward=="life":
                    p.lives=min(p.lives+1,p.max_lives)
                    self.show_msg("★ UFO: +1 LIFE! ★",2)
                elif reward=="random_powerup":
                    data=random.choice(POWERUPS)
                    self.powerups_on_field.append({"x":self.ufo.x,"y":self.ufo.y,"t":0,"data":data})
                    self.show_msg("★ UFO: POWER-UP DROP! ★",2)
                elif reward=="shield":
                    p.add_powerup("shield",15)
                    self.show_msg("★ UFO: MEGA SHIELD! ★",2)
                explode(self.particles,self.ufo.x,self.ufo.y,C["ufo"],40)
                self.unlock_achievement("ufo_kill")
                break

def _collide_asteroids_player(self):
    p=self.player
    if p.invincible>0: return
    for ast in self.asteroids[:]:
        if abs(ast.x-p.x)<ast.size+10 and abs(ast.y-p.y)<ast.size+10:
            self.asteroids.remove(ast)
            if p.shield_hp>0:
                p.shield_hp-=1
                explode(self.particles,ast.x,ast.y,C["shield"],8)
            else:
                self._player_die()
            break
    # Bullets vs asteroids
    for b in self.player_bullets[:]:
        for ast in self.asteroids[:]:
            if abs(b["x"]-ast.x)<ast.size and abs(b["y"]-ast.y)<ast.size:
                ast.hp-=1
                if ast.hp<=0:
                    self.asteroids.remove(ast)
                    explode(self.particles,ast.x,ast.y,"#aa8844",12)
                    self.player.score+=50
                if b in self.player_bullets: self.player_bullets.remove(b)
                break

def _spawn_pu(self,x,y):
    data=random.choice(POWERUPS)
    self.powerups_on_field.append({"x":x,"y":y,"t":0,"data":data})

def _player_die(self):
    p=self.player
    explode(self.particles,p.x,p.y,p.color,40)
    p.lives-=1; p.damage_taken+=1
    p.invincible=FPS*3; p.active_powerups.clear(); p.shield_hp=0; p.combo=0
    if p.lives<=0: self.state="game_over"
    else: self.show_msg(f"☠ LIVES: {p.lives}",2)

def _add_combo(self,pts,x,y):
    p=self.player; p.combo+=1
    p.combo_timer=FPS*2
    if p.combo>p.max_combo: p.max_combo=p.combo
    mul=max(1,p.combo//5+1)
    total=pts*mul; p.score+=total
    self.combo_hits.append({"x":x,"y":y,"pts":total,"life":40,
                            "y_off":0,"combo":p.combo})
    self.check_achievements()

# ── Draw ─────────────────────────────────────────
def draw(self):
    c=self.canvas; c.delete("all")
    c.create_rectangle(0,0,W,H,fill=C["bg"],outline="")

    # Grid
    for gy in range(0,H,40):
        c.create_line(0,(gy+self.grid_offset)%H,W,(gy+self.grid_offset)%H,
                     fill=C["grid"],width=1)
    for gx in range(0,W,60):
        c.create_line(gx,0,gx,H,fill=C["grid"],width=1)

    self.stars.draw(c)

    # Scan line
    c.create_rectangle(0,self.scan_line,W,self.scan_line+2,
                      fill="#ffffff",outline="",stipple="gray12")

    # Nebula overlay
    if self.nebula_opacity>0 and self.weather and self.weather["id"]=="nebula":
        v=int(self.nebula_opacity*40)
        col=f"#0a00{v:02x}"
        for py in range(0,H,4):
            c.create_line(0,py,W,py,fill="#110033",width=3,stipple="gray50")

    # Speed pulse overlay
    if self.speed_pulse>0:
        alpha=self.speed_pulse/15
        v=int(alpha*80); col=f"#{v:02x}0011"
        c.create_rectangle(0,0,W,H,fill="",outline=self.speed_pulse_col,
                          width=int(alpha*8))

    if self.state=="menu": self.draw_menu(c)
    elif self.state in("playing","paused","level_clear","upgrade"):
        self.draw_game(c)
        if self.state=="paused": self.draw_pause(c)
        elif self.state=="level_clear": self.draw_level_clear(c)
        elif self.state=="upgrade" and self.upgrade_screen:
            self.upgrade_screen.draw(c,self.tick)
    elif self.state=="game_over":
        self.draw_game(c); self.draw_game_over(c)
    elif self.state=="highscore": self.draw_highscore(c)
    elif self.state=="enter_name": self.draw_enter_name(c)
    elif self.state=="skins": self.draw_skins(c)

    # Achievement popups (always on top)
    for ap in self.achievement_popups:
        ap.draw(c)

def draw_menu(self,c):
    t=self.tick
    gv=int(128+127*math.sin(t*0.04)); title_col=f"#{gv:02x}ffff"
    neon(c,W//2,120,"GALACTIC SIEGE",title_col,size=48,glow=True)
    neon(c,W//2,168,"═"*42,C["dim"],size=11,glow=False)
    neon(c,W//2,192,"v2.0  ULTIMATE EDITION",C["dim"],size=12,glow=False)

    # Animated enemy demo
    for i in range(6):
        ex=100+i*145+math.sin(t*0.02+i)*25
        ey=270+math.cos(t*0.03+i*1.2)*18
        e=Enemy(ex,ey,i%3,0)
        e.anim_t=t*0.04+i; e.draw(c)

    # Menu options
    opts=[("▶ STORY MODE","story",C["cyan"]),
          ("▶ ENDLESS MODE","endless",C["green"]),
          ("▶ SHIP SKINS","skins",C["magenta"]),
          ("▶ HIGH SCORES","scores",C["yellow"])]
    for i,(label,_,col) in enumerate(opts):
        y=370+i*46
        if i==self.menu_cursor:
            c.create_rectangle(W//2-180,y-18,W//2+180,y+18,
                              fill="#0a0a28",outline=col,width=2)
            neon(c,W//2,y,label,col,size=16,glow=True)
        else:
            neon(c,W//2,y,label,C["dim"],size=14,glow=False)

    neon(c,W//2,580,"↑↓ SELECT  •  ENTER CONFIRM  •  ESC BACK",C["dim"],size=11,glow=False)

    # Endless best
    if self.save.get("endless_best",0)>0:
        neon(c,W//2,620,f"ENDLESS BEST: WAVE {self.save['endless_best']}",
             C["orange"],size=11,glow=False)

    # Achievement count
    ac=len(self.save.get("achievements",[]))
    neon(c,W//2,648,f"ACHIEVEMENTS: {ac}/{len(ACHIEVEMENTS)}",C["dim"],size=10,glow=False)

def draw_game(self,c):
    p=self.player

    # Weather label
    if self.weather and self.weather_timer>0:
        wc=self.weather["color"]
        c.create_rectangle(0,36,W,56,fill="#000011",outline=wc,width=1)
        neon(c,W//2,46,f"⚡ {self.weather['name']}: {self.weather['desc']} ⚡",
             wc,size=11,glow=True)

    # Lightning strikes
    for ls in self.lightning_strikes:
        alpha=ls["life"]/ls["max_life"]
        lw=max(1,int(alpha*4))
        c.create_line(ls["x"],0,ls["x"]+random.randint(-10,10),H,
                     fill="#ffff88",width=lw)
        c.create_line(ls["x"]-2,0,ls["x"]+2,H,fill="#ffffff",width=1)

    # Asteroids
    for ast in self.asteroids:
        ast.draw(c)

    # Bunkers
    for bk in self.bunkers:
        if bk.hp>0: bk.draw(c)

    # Trail
    for i,(tx,ty) in enumerate(p.trail):
        a=i/len(p.trail); r=int(a*4)
        fc=f"#00{int(a*88+20):02x}{int(a*200):02x}"
        c.create_oval(tx-r,ty-r,tx+r,ty+r,fill=fc,outline="")

    # Player
    p.draw(c,self.tick)

    # UFO
    self.ufo.draw(c)

    # Enemy bullets
    for b in self.enemy_bullets: draw_bullet(c,b)
    # Player bullets
    for b in self.player_bullets: draw_bullet(c,b)
    # Enemies
    for e in self.enemies: e.draw(c)
    # Boss
    if self.boss_active and self.boss: self.boss.draw(c)
    # Powerups
    for pu in self.powerups_on_field: draw_powerup(c,pu,self.tick)

    # Particles
    for part in self.particles:
        col=part.draw_color(); s=part.size
        c.create_oval(part.x-s,part.y-s,part.x+s,part.y+s,fill=col,outline="")

    # Combo floats
    for ch in self.combo_hits[:]:
        ch["life"]-=1; ch["y_off"]=ch.get("y_off",0)-1
        a=ch["life"]/40
        r2=int(255*min(1,a*2)); g2=int(255*a)
        col=f"#{r2:02x}{g2:02x}00"
        txt=f"+{ch['pts']}"
        if ch["combo"]>=10: txt+=f"  ×{ch['combo']}!"
        c.create_text(ch["x"],ch["y"]+ch["y_off"],text=txt,fill=col,
                     font=("Courier",11,"bold"))
        if ch["life"]<=0: self.combo_hits.remove(ch)

    self.draw_hud(c)

    if self.msg_timer>0:
        a=min(1.0,self.msg_timer/(FPS*0.5)); v=int(a*255)
        neon(c,W//2,H//2-20,self.msg_text,f"#{v:02x}ffff",size=22,glow=True)

def draw_hud(self,c):
    p=self.player; cfg=self.level_cfg
    c.create_rectangle(0,0,W,36,fill="#06061a",outline=C["dim"],width=1)
    neon(c,10,18,f"SCORE  {p.score:>9}",C["cyan"],size=13,glow=False,anchor="w")
    lvc=[C["green"],C["cyan"],C["yellow"],C["orange"],C["magenta"]][cfg["tier"]]
    mode_tag="ENDLESS" if self.mode=="endless" else f"LEVEL {self.current_level}"
    neon(c,W//2,18,f"{mode_tag}  {cfg['tier_name']}",lvc,size=13,glow=False)
    for i in range(p.max_lives):
        col=C["red"] if i<p.lives else C["dim"]
        c.create_text(W-130+i*24,18,text="❤",fill=col,font=("Courier",14,"bold"))

    if p.combo>0:
        c.create_rectangle(0,36,W,42,fill="#111",outline="")
        ratio=min(1.0,p.combo_timer/(FPS*2))
        bc=C["yellow"] if p.combo<10 else C["magenta"]
        c.create_rectangle(0,36,int(W*ratio),42,fill=bc,outline="")
        c.create_text(W//2,39,text=f"COMBO ×{p.combo}",fill="#000",
                     font=("Courier",8,"bold"))

    # Bottom HUD
    c.create_rectangle(0,H-40,W,H,fill="#06061a",outline=C["dim"],width=1)
    px=10
    for pid,ticks in list(p.active_powerups.items())[:8]:
        data=next((pu for pu in POWERUPS if pu["id"]==pid),None)
        if data:
            dur=data["dur"]; ratio2=ticks/(dur*FPS) if dur>0 else 1
            col=data["color"]
            c.create_rectangle(px,H-34,px+58,H-18,fill="#111",outline=col,width=1)
            c.create_rectangle(px,H-34,px+int(58*ratio2),H-18,fill=col,outline="")
            c.create_text(px+29,H-26,text=f"{data['sym']} {data['name'][:5]}",
                         fill="#000",font=("Courier",7,"bold"))
            px+=62
            if px>W-80: break

    # Upgrade icons (tiny)
    ux=W-10
    for uid,lvl in list(p.upgrades.items()):
        u=next((u2 for u2 in ALL_UPGRADES if u2["id"]==uid),None)
        if u:
            c.create_text(ux,H-26,text=f"{u['sym']}{lvl}",fill=u["color"],
                         font=("Courier",8,"bold"),anchor="e")
            ux-=32

def draw_pause(self,c):
    c.create_rectangle(0,0,W,H,fill="#000",stipple="gray50",outline="")
    neon(c,W//2,H//2-40,"⏸  PAUSED",C["cyan"],size=32,glow=True)
    neon(c,W//2,H//2+20,"[ ESC / P ] RESUME",C["dim"],size=16,glow=False)

def draw_level_clear(self,c):
    c.create_rectangle(0,0,W,H,fill="#000",stipple="gray50",outline="")
    neon(c,W//2,H//2-80,f"✦ LEVEL {self.current_level} CLEARED ✦",C["green"],size=28,glow=True)
    neon(c,W//2,H//2-30,f"SCORE: {self.player.score}",C["yellow"],size=20,glow=False)
    neon(c,W//2,H//2+15,f"MAX COMBO: ×{self.player.max_combo}",C["magenta"],size=16,glow=False)
    # Achievements unlocked this level
    recent=[ap.ach["name"] for ap in self.achievement_popups]
    if recent:
        neon(c,W//2,H//2+55,f"🏆 {recent[-1]}",C["yellow"],size=13,glow=False)
    if (self.tick//25)%2==0:
        neon(c,W//2,H//2+100,"[ ENTER ] CHOOSE UPGRADE →",C["cyan"],size=16,glow=True)

def draw_game_over(self,c):
    c.create_rectangle(0,0,W,H,fill="#000",stipple="gray50",outline="")
    t=self.tick; pv=int(128+127*math.sin(t*0.05))
    neon(c,W//2,H//2-90,f"☠  GAME OVER  ☠",f"#{pv:02x}0033",size=36,glow=True)
    neon(c,W//2,H//2-35,f"FINAL SCORE: {self.player.score}",C["white"],size=22,glow=False)
    neon(c,W//2,H//2+5,f"LEVEL REACHED: {self.current_level}",C["cyan"],size=16,glow=False)
    neon(c,W//2,H//2+38,f"MAX COMBO: ×{self.player.max_combo}",C["magenta"],size=14,glow=False)
    ac=len(self.save.get("achievements",[]))
    neon(c,W//2,H//2+68,f"ACHIEVEMENTS: {ac}/{len(ACHIEVEMENTS)}",C["yellow"],size=12,glow=False)
    if (self.tick//30)%2==0:
        neon(c,W//2,H//2+105,"[ ENTER ] SAVE SCORE",C["yellow"],size=16,glow=True)

def draw_enter_name(self,c):
    c.create_rectangle(W//2-220,H//2-90,W//2+220,H//2+110,
                      fill="#080820",outline=C["cyan"],width=2)
    neon(c,W//2,H//2-58,"ENTER YOUR NAME",C["cyan"],size=20,glow=True)
    nd=self.player_name+("|" if (self.tick//20)%2==0 else " ")
    neon(c,W//2,H//2,nd,C["white"],size=26,glow=False)
    neon(c,W//2,H//2+60,"[ ENTER ] CONFIRM",C["green"],size=13,glow=False)

def draw_highscore(self,c):
    scores=self.save.get("highscores",[])
    neon(c,W//2,55,"◈  HALL OF FAME  ◈",C["yellow"],size=26,glow=True)
    neon(c,W//2,92,"─"*55,C["dim"],size=9,glow=False)
    if not scores:
        neon(c,W//2,H//2,"NO SCORES YET!",C["dim"],size=18,glow=False)
    else:
        rank_sym=["🥇","🥈","🥉","4.","5.","6.","7.","8.","9.","10.","11.","12."]
        rank_col=[C["yellow"],"#c0c0c0","#cd7f32",C["cyan"],C["cyan"],C["dim"],
                 C["dim"],C["dim"],C["dim"],C["dim"],C["dim"],C["dim"]]
        for i,s in enumerate(scores[:12]):
            y=122+i*44
            col=rank_col[min(i,len(rank_col)-1)]
            c.create_rectangle(W//2-330,y-16,W//2+330,y+18,
                              fill="#0a0a22" if i%2==0 else "#080818",
                              outline=C["dim"],width=1)
            c.create_text(W//2-310,y,text=rank_sym[i],fill=col,
                         font=("Courier",14,"bold"),anchor="w")
            c.create_text(W//2-260,y,text=s["name"],fill=col,
                         font=("Courier",14,"bold"),anchor="w")
            mode_tag="[E]" if s.get("mode")=="endless" else "[S]"
            c.create_text(W//2-90,y,text=mode_tag,fill=C["dim"],
                         font=("Courier",10),anchor="w")
            c.create_text(W//2+80,y,text=f"{s['score']:>9}",fill=col,
                         font=("Courier",14,"bold"),anchor="e")
            c.create_text(W//2+190,y,text=f"LVL {s['level']}",fill=C["dim"],
                         font=("Courier",12),anchor="e")
            c.create_text(W//2+310,y,text=s.get("date",""),fill=C["dim"],
                         font=("Courier",10),anchor="e")
    neon(c,W//2,H-38,"[ ENTER / ESC ] BACK",C["dim"],size=12,glow=False)

def draw_skins(self,c):
    neon(c,W//2,60,"🎖  SHIP SKINS  🎖",C["magenta"],size=26,glow=True)
    unlocked=self.save.get("unlocked_skins",["default"])
    # Draw all skins
    card_w=130; gap=18; total=len(SKINS)
    x0=W//2-(total*(card_w+gap))//2+card_w//2
    unlocked_list=[s for s in SKINS if s["id"] in unlocked]
    locked_list=[s for s in SKINS if s["id"] not in unlocked]
    all_display=unlocked_list+locked_list

    for i,sk in enumerate(all_display):
        is_unlocked=sk["id"] in unlocked
        is_sel=(i<len(unlocked_list) and i==self.skin_cursor)
        is_active=sk["id"]==self.selected_skin
        cx2=x0+i*(card_w+gap); cy2=320

        border=sk["color"] if is_sel else (C["dim"] if not is_unlocked else "#334466")
        fill="#0a0a28" if is_sel else "#050515"
        c.create_rectangle(cx2-card_w//2,cy2-80,cx2+card_w//2,cy2+80,
                          fill=fill,outline=border,width=2 if is_sel else 1)

        # Preview ship
        if is_unlocked:
            col=sk["color"]
            body=[(cx2,cy2-44),(cx2+6,cy2-34),(cx2+18,cy2-20),
                  (cx2+14,cy2-16),(cx2+6,cy2-20),(cx2,cy2-24),
                  (cx2-6,cy2-20),(cx2-14,cy2-16),(cx2-18,cy2-20),(cx2-6,cy2-34)]
            c.create_polygon(body,fill=col,outline=C["cyan"],width=1)
            c.create_oval(cx2-4,cy2-40,cx2+4,cy2-28,fill="#001133",outline=col,width=1)
        else:
            c.create_text(cx2,cy2-30,text="🔒",font=("Courier",24,"bold"),fill=C["dim"])

        neon(c,cx2,cy2+10,sk["name"],sk["color"] if is_unlocked else C["dim"],
             size=11,glow=is_sel)
        if is_active:
            neon(c,cx2,cy2+30,"● ACTIVE",C["green"],size=9,glow=False)
        if not is_unlocked:
            c.create_text(cx2,cy2+48,text=sk["unlock"],fill=C["dim"],
                         font=("Courier",8),width=card_w-10)

    neon(c,W//2,H-130,"←→ SELECT SKIN  •  ENTER EQUIP  •  ESC BACK",C["dim"],size=11,glow=False)
    neon(c,W//2,H-90,f"UNLOCKED: {len(unlocked)}/{len(SKINS)}",C["magenta"],size=13,glow=False)

    # Achievements panel
    neon(c,W//2,H-55,f"ACHIEVEMENTS: {len(self.save.get('achievements',[]))}/{len(ACHIEVEMENTS)}",
         C["yellow"],size=11,glow=False)

# ── Loop ─────────────────────────────────────────
def loop(self):
    self.update()
    self.draw()
    self.root.after(1000//FPS, self.loop)
```

# ══════════════════════════════════════════════════════

# ENTRY

# ══════════════════════════════════════════════════════

if **name**==”**main**”:
GalacticSiege()
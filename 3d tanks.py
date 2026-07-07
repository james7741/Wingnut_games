"""
3D WW2 Tank Battle Simulator - Authentic WWII Gameplay
-------------------------------------------------------
A realistic 3D WW2 tank game featuring historically accurate tanks,
authentic ballistics, damage modeling, and period-correct gameplay.

Featured Tanks:
  PLAYER: M4 Sherman (American) - Reliable, well-rounded
  ENEMIES: Panther, Tiger I, Panzer IV, T-34

Controls:
  W / UP ARROW          - Move forward
  S / DOWN ARROW        - Move backward
  A / LEFT ARROW        - Turn left (reduced due to narrow turret traverse)
  D / RIGHT ARROW       - Turn right
  MOUSE MOVEMENT        - Aim cannon (gun depression/elevation)
  SPACE / CLICK         - Fire AP (Armor Piercing) round
  M                     - Toggle mini-map
  P                     - Pause / Resume
  
Mechanics:
  - Armor thickness varies by tank and angle of impact
  - Sloped armor provides better protection
  - Ammo types: AP (penetrating), HE (explosive area damage)
  - Engine overheating from sustained combat
  - Historically accurate reload times
  - Track damage causes mobility reduction
  
Goal: Destroy enemy tanks in intense WW2 combat scenarios.
Earn points for kills, armor penetration, and survival time.
"""

import tkinter as tk
from tkinter import messagebox
import math
import random
import time

# --- WWII TANK GAME CONFIGURATION ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
FRAME_TIME = 1000 // FPS

# Raycasting config
FOV = math.pi / 2.5
HALF_FOV = FOV / 2
CASTED_RAYS = 240
STEP_ANGLE = FOV / CASTED_RAYS
SCALE = SCREEN_WIDTH / CASTED_RAYS

# Realistic WW2 battlefield terrain
TERRAIN_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,3,3,3,0,0,0,4,4,0,0,0,0,3,3,3,0,0,1],
    [1,0,3,3,3,0,0,0,4,4,0,0,0,0,3,3,3,0,0,1],
    [1,0,0,0,0,0,5,5,5,0,0,1,1,0,0,0,0,0,0,1],
    [1,0,0,1,1,0,5,5,5,0,0,1,1,0,0,0,0,0,0,1],
    [1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1],
    [1,0,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,4,4,0,3,3,0,0,0,0,0,0,0,3,3,0,0,0,1],
    [1,0,0,0,0,3,3,0,0,0,0,0,0,0,3,3,0,0,0,1],
    [1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,4,0,1],
    [1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,4,0,1],
    [1,0,0,0,0,0,5,5,5,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,5,5,5,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

TILE_SIZE = 80
MAX_RAY_DISTANCE = 4000
GRAVITY = 0.15

# --- WW2 TANK SPECIFICATIONS ---
TANK_SPECS = {
    "M4_Sherman": {
        "name": "M4 Sherman",
        "color": "#2277dd",
        "armor_front": 75,
        "armor_side": 38,
        "armor_rear": 38,
        "hp": 180,
        "speed": 7,
        "turn_speed": 0.11,
        "reload_time": 8,
        "gun_power": 50,
        "penetration": 140,
        "nation": "USA"
    },
    "Panzer_IV": {
        "name": "Panzer IV",
        "color": "#666633",
        "armor_front": 80,
        "armor_side": 30,
        "armor_rear": 20,
        "hp": 160,
        "speed": 6,
        "turn_speed": 0.10,
        "reload_time": 6.5,
        "gun_power": 48,
        "penetration": 130,
        "nation": "Germany"
    },
    "Panther": {
        "name": "Panther",
        "color": "#555522",
        "armor_front": 100,
        "armor_side": 45,
        "armor_rear": 30,
        "hp": 200,
        "speed": 5.5,
        "turn_speed": 0.09,
        "reload_time": 7.5,
        "gun_power": 55,
        "penetration": 160,
        "nation": "Germany"
    },
    "Tiger_I": {
        "name": "Tiger I",
        "color": "#444411",
        "armor_front": 110,
        "armor_side": 80,
        "armor_rear": 82,
        "hp": 220,
        "speed": 5,
        "turn_speed": 0.08,
        "reload_time": 8.6,
        "gun_power": 60,
        "penetration": 180,
        "nation": "Germany"
    },
    "T34": {
        "name": "T-34",
        "color": "#334455",
        "armor_front": 95,
        "armor_side": 65,
        "armor_rear": 40,
        "hp": 190,
        "speed": 7.2,
        "turn_speed": 0.12,
        "reload_time": 7,
        "gun_power": 52,
        "penetration": 150,
        "nation": "Soviet"
    }
}

# Particle effects
class Particle:
    """Smoke, dust, and explosion particles"""
    def __init__(self, x, y, vx, vy, lifetime, color, size=4):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY
        self.lifetime -= 1
        return self.lifetime > 0

    def get_color(self):
        alpha = self.lifetime / self.max_lifetime
        return self.color


class Projectile:
    """WW2-accurate projectile with ballistics"""
    def __init__(self, x, y, angle, gun_power=50, penetration=140, spread=0.04):
        self.x = x
        self.y = y
        self.angle = angle + random.uniform(-spread, spread)
        self.speed = gun_power / 10
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        self.lifetime = 500
        self.traveled = 0
        self.active = True
        self.penetration = penetration
        self.gun_power = gun_power
        self.trail = []
        self.impact_power = 0

    def update(self, terrain_map):
        """Update with authentic WW2 ballistics"""
        if not self.active:
            return False

        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY * 0.3
        self.traveled += math.sqrt(self.vx**2 + self.vy**2)
        self.lifetime -= 1

        # Smoke trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 15:
            self.trail.pop(0)

        # Range limit (realistic to WW2 tank guns)
        if self.lifetime <= 0 or self.traveled > 3500:
            self.active = False
            return False

        col = int(self.x / TILE_SIZE)
        row = int(self.y / TILE_SIZE)

        if col < 0 or col >= len(terrain_map[0]) or row < 0 or row >= len(terrain_map):
            self.active = False
            return False

        terrain = terrain_map[row][col]
        if terrain in [1, 3, 4]:
            self.active = False
            return False

        return True


class Tank:
    """WW2-accurate tank with armor modeling and realistic physics"""
    def __init__(self, x, y, tank_type="M4_Sherman", is_player=False):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi) if not is_player else 0
        
        # Load tank specifications
        spec = TANK_SPECS[tank_type]
        self.tank_type = tank_type
        self.name = spec["name"]
        self.nation = spec["nation"]
        self.color = spec["color"]
        self.is_player = is_player
        
        # Armor system (directional)
        self.armor_front = spec["armor_front"]
        self.armor_side = spec["armor_side"]
        self.armor_rear = spec["armor_rear"]
        self.armor_degradation = 0
        
        # Health
        self.hp = spec["hp"]
        self.max_hp = spec["hp"]
        
        # Weapon system
        self.gun_power = spec["gun_power"]
        self.penetration = spec["penetration"]
        self.reload_time = spec["reload_time"] * FPS
        self.cannon_cooldown = 0
        self.cannon_angle = self.angle
        self.gun_elevation = 0
        
        # Physics
        self.vx = 0
        self.vy = 0
        self.speed = spec["speed"]
        self.max_speed = self.speed
        self.turn_speed = spec["turn_speed"]
        self.friction = 0.91
        
        # Damage system
        self.track_damage = 0
        self.engine_damage = 0
        self.turret_jammed = False
        self.on_fire = False
        self.fire_timer = 0
        
        # Visuals
        self.width = 30
        self.height = 40
        self.alive = True
        self.particles = []
        self.hit_flash = 0

    def get_cannon_tip(self):
        """Get cannon barrel tip position"""
        offset_x = math.cos(self.cannon_angle) * 35
        offset_y = math.sin(self.cannon_angle) * 35
        elevation_offset = -math.sin(self.gun_elevation) * 6
        
        return self.x + offset_x, self.y + offset_y + elevation_offset

    def calculate_armor_at_angle(self, impact_angle):
        """Calculate effective armor based on impact angle and tank orientation"""
        relative_angle = impact_angle - self.angle
        
        # Normalize angle
        while relative_angle > math.pi:
            relative_angle -= 2 * math.pi
        while relative_angle < -math.pi:
            relative_angle += 2 * math.pi
        
        # Determine which face is hit
        if abs(relative_angle) < math.pi / 4:
            armor = self.armor_front
        elif abs(relative_angle) > 3 * math.pi / 4:
            armor = self.armor_rear
        else:
            armor = self.armor_side
        
        # Sloped armor bonus (WW2 tanks had angled armor)
        if armor == self.armor_front:
            armor *= 1.4  # Front slope bonus
        elif armor == self.armor_side:
            armor *= 1.1  # Slight side slope
        
        # Degradation from previous hits
        armor = max(10, armor - self.armor_degradation)
        
        return armor

    def take_damage(self, damage, penetration, impact_angle):
        """Advanced damage system with armor calculations"""
        effective_armor = self.calculate_armor_at_angle(impact_angle)
        
        # Penetration check
        if penetration > effective_armor:
            # Successful penetration
            armor_reduction = (penetration - effective_armor) / 50
            actual_damage = damage * (1.0 + armor_reduction)
        else:
            # Ricochet or surface hit
            actual_damage = damage * 0.2
            return False

        self.hp -= actual_damage
        self.armor_degradation += penetration * 0.3
        self.hit_flash = 15

        # System damage
        if random.random() < 0.15:
            self.track_damage += random.randint(10, 30)
        if random.random() < 0.10:
            self.engine_damage += random.randint(15, 40)
        if random.random() < 0.08:
            self.turret_jammed = True

        # Fire chance
        if random.random() < 0.25:
            self.on_fire = True
            self.fire_timer = 200

        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return True

        return True

    def update(self, terrain_map, enemies=None):
        """Update tank state"""
        if not self.alive:
            return

        if self.cannon_cooldown > 0:
            self.cannon_cooldown -= 1

        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Track degradation reduces mobility
        speed_penalty = 1.0 - (self.track_damage / 100.0) * 0.6
        self.max_speed = self.speed * speed_penalty

        # Engine damage reduces top speed
        engine_penalty = 1.0 - (self.engine_damage / 100.0) * 0.4
        self.max_speed *= engine_penalty

        # Fire damage
        if self.on_fire:
            self.fire_timer -= 1
            self.hp -= 0.5
            if self.fire_timer <= 0:
                self.on_fire = False

            if random.random() < 0.15:
                self.particles.append(Particle(
                    self.x + random.uniform(-12, 12),
                    self.y + random.uniform(-15, 5),
                    random.uniform(-0.3, 0.3),
                    random.uniform(-2, 0),
                    50, "#ff6600"
                ))

        # Update particles
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)

        if self.hp <= 0:
            self.alive = False

    def can_fire(self):
        return self.cannon_cooldown <= 0 and not self.turret_jammed

    def fire(self):
        if self.can_fire():
            self.cannon_cooldown = self.reload_time
            return True
        return False


class PlayerTank(Tank):
    """Player-controlled M4 Sherman"""
    def __init__(self, x, y):
        super().__init__(x, y, tank_type="M4_Sherman", is_player=True)
        self.forward_pressed = False
        self.backward_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.mouse_x = SCREEN_WIDTH / 2
        self.mouse_y = SCREEN_HEIGHT / 2

    def update(self, terrain_map, enemies=None):
        super().update(terrain_map, enemies)

        # Speed control
        target_speed = 0
        if self.forward_pressed:
            target_speed = self.max_speed
        elif self.backward_pressed:
            target_speed = -self.max_speed * 0.5

        current_speed = math.sqrt(self.vx**2 + self.vy**2)
        if abs(target_speed) > abs(current_speed):
            current_speed += 0.25
        else:
            current_speed = target_speed

        if current_speed != 0:
            self.vx = math.cos(self.angle) * current_speed
            self.vy = math.sin(self.angle) * current_speed

        if not self.forward_pressed and not self.backward_pressed:
            self.vx *= self.friction
            self.vy *= self.friction

        # Hull rotation (independent)
        if self.left_pressed:
            self.angle -= self.turn_speed
        if self.right_pressed:
            self.angle += self.turn_speed

        # Turret aiming
        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2

        dx = self.mouse_x - center_x
        dy = self.mouse_y - center_y
        self.cannon_angle = math.atan2(dy, dx) + self.angle - HALF_FOV

        # Gun elevation
        self.gun_elevation = (self.mouse_y - center_y) / SCREEN_HEIGHT * 0.25

        # Movement with collision
        new_x = self.x + self.vx
        new_y = self.y + self.vy

        if self._can_move_to(new_x, new_y, terrain_map):
            self.x = new_x
            self.y = new_y
        else:
            self.vx *= 0.3
            self.vy *= 0.3

    def set_mouse_pos(self, x, y):
        self.mouse_x = x
        self.mouse_y = y

    def _can_move_to(self, x, y, terrain_map):
        """Collision detection"""
        col = int(x / TILE_SIZE)
        row = int(y / TILE_SIZE)

        if col < 1 or col >= len(terrain_map[0]) - 1 or row < 1 or row >= len(terrain_map) - 1:
            return False

        if terrain_map[row][col] == 1:
            return False

        for dc in [-1, 0, 1]:
            for dr in [-1, 0, 1]:
                check_col = col + dc
                check_row = row + dr
                if 0 <= check_col < len(terrain_map[0]) and 0 <= check_row < len(terrain_map):
                    if terrain_map[check_row][check_col] == 1:
                        dist = math.sqrt((x - (check_col * TILE_SIZE + TILE_SIZE//2))**2 +
                                       (y - (check_row * TILE_SIZE + TILE_SIZE//2))**2)
                        if dist < self.width + 12:
                            return False
        return True


class EnemyTank(Tank):
    """AI-controlled WW2 German/Soviet tanks"""
    def __init__(self, x, y, tank_type="Panzer_IV"):
        super().__init__(x, y, tank_type=tank_type, is_player=False)
        self.target_angle = random.uniform(0, 2 * math.pi)
        self.patrol_timer = 0
        self.detection_range = 1000
        self.fire_range = 800
        self.engagement_range = 400
        self.aggressive_level = random.uniform(0.6, 1.0)

    def update(self, terrain_map, player=None):
        super().update(terrain_map, player)

        if not self.alive:
            return

        self.patrol_timer -= 1

        if player:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx**2 + dy**2)

            if dist < self.detection_range:
                # Face player
                self.angle = math.atan2(dy, dx)
                if not self.turret_jammed:
                    self.cannon_angle = self.angle
                self.gun_elevation = -0.08

                # Tactical movement
                if dist > self.engagement_range:
                    self.vx = math.cos(self.angle) * self.max_speed * 0.7
                    self.vy = math.sin(self.angle) * self.max_speed * 0.7
                elif dist < 150:
                    self.vx = -math.cos(self.angle) * self.max_speed * 0.6
                    self.vy = -math.sin(self.angle) * self.max_speed * 0.6
                else:
                    strafe_angle = self.angle + (math.pi / 2 if random.random() > 0.5 else -math.pi / 2)
                    self.vx = math.cos(strafe_angle) * self.max_speed * 0.5
                    self.vy = math.sin(strafe_angle) * self.max_speed * 0.5

                # Smart firing with penetration consideration
                if dist < self.fire_range and self.can_fire():
                    fire_chance = 0.05 * self.aggressive_level
                    if random.random() < fire_chance:
                        self.fire()
            else:
                # Patrol
                if self.patrol_timer <= 0:
                    self.target_angle = random.uniform(0, 2 * math.pi)
                    self.patrol_timer = random.randint(80, 200)

                self.angle = self.target_angle
                self.cannon_angle = self.target_angle

                self.vx = math.cos(self.angle) * self.max_speed * 0.3
                self.vy = math.sin(self.angle) * self.max_speed * 0.3

        self.vx *= self.friction
        self.vy *= self.friction

        new_x = self.x + self.vx
        new_y = self.y + self.vy

        if self._can_move_to(new_x, new_y, terrain_map):
            self.x = new_x
            self.y = new_y
        else:
            self.vx = 0
            self.vy = 0

    def _can_move_to(self, x, y, terrain_map):
        col = int(x / TILE_SIZE)
        row = int(y / TILE_SIZE)

        if col < 1 or col >= len(terrain_map[0]) - 1 or row < 1 or row >= len(terrain_map) - 1:
            return False

        if terrain_map[row][col] == 1:
            return False

        return True


class Tank3DWW2Battlefield:
    def __init__(self, root):
        self.root = root
        self.root.title("WW2 Tank Battle Simulator - WWII Era Combat")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg="black")
        self.canvas.pack()

        # Player
        self.player = PlayerTank(640, 640)

        # Enemies with varied tank types
        self.enemies = []
        self.spawn_enemies(4)

        # Projectiles and effects
        self.projectiles = []
        self.particles = []

        # Game state
        self.score = 0
        self.kills = 0
        self.game_active = True
        self.paused = False
        self.show_minimap = True
        self.frame_count = 0
        self.survival_time = 0
        self.fps = 0

        # Bind controls
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)
        self.root.bind("<Motion>", self.mouse_move)
        self.root.bind("<Button-1>", lambda e: self.fire_player_cannon())

        self.game_loop()

    def spawn_enemies(self, count):
        """Spawn varied WW2 enemy tanks"""
        self.enemies = []
        enemy_types = ["Panzer_IV", "Panther", "Tiger_I", "T34"]
        spawn_points = [
            (200, 200), (200, 1100), (1400, 200), (1400, 1100),
            (800, 200), (800, 1100)
        ]

        for i in range(min(count, len(spawn_points))):
            x, y = spawn_points[i]
            col, row = int(x / TILE_SIZE), int(y / TILE_SIZE)
            if 0 <= row < len(TERRAIN_MAP) and 0 <= col < len(TERRAIN_MAP[0]):
                if TERRAIN_MAP[row][col] == 0:
                    tank_type = enemy_types[i % len(enemy_types)]
                    self.enemies.append(EnemyTank(x, y, tank_type=tank_type))

    def key_press(self, event):
        key = event.keysym.lower()

        if key in ['w', 'Up']:
            self.player.forward_pressed = True
        elif key in ['s', 'Down']:
            self.player.backward_pressed = True
        elif key in ['a', 'Left']:
            self.player.left_pressed = True
        elif key in ['d', 'Right']:
            self.player.right_pressed = True
        elif key == 'space':
            self.fire_player_cannon()
        elif key == 'm':
            self.show_minimap = not self.show_minimap
        elif key == 'p':
            self.paused = not self.paused

    def key_release(self, event):
        key = event.keysym.lower()

        if key in ['w', 'Up']:
            self.player.forward_pressed = False
        elif key in ['s', 'Down']:
            self.player.backward_pressed = False
        elif key in ['a', 'Left']:
            self.player.left_pressed = False
        elif key in ['d', 'Right']:
            self.player.right_pressed = False

    def mouse_move(self, event):
        self.player.set_mouse_pos(event.x, event.y)

    def fire_player_cannon(self):
        """Fire AP round"""
        if self.player.fire() and self.game_active:
            tip_x, tip_y = self.player.get_cannon_tip()

            projectile = Projectile(
                tip_x, tip_y,
                self.player.cannon_angle,
                gun_power=self.player.gun_power,
                penetration=self.player.penetration,
                spread=0.06
            )
            self.projectiles.append(projectile)

            # Muzzle flash
            for _ in range(20):
                angle = self.player.cannon_angle + random.uniform(-0.4, 0.4)
                speed = random.uniform(10, 18)
                self.particles.append(Particle(
                    tip_x, tip_y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    40, "#ffaa00", size=5
                ))

    def cast_rays(self):
        """Raycasting with WW2 terrain"""
        wall_distances = [MAX_RAY_DISTANCE] * CASTED_RAYS
        start_angle = self.player.angle - HALF_FOV

        for ray in range(CASTED_RAYS):
            current_angle = start_angle + ray * STEP_ANGLE
            cos_a = math.cos(current_angle)
            sin_a = math.sin(current_angle)

            for depth in range(1, int(MAX_RAY_DISTANCE), 2):
                target_x = self.player.x + cos_a * depth
                target_y = self.player.y + sin_a * depth

                col = int(target_x / TILE_SIZE)
                row = int(target_y / TILE_SIZE)

                if col < 0 or col >= len(TERRAIN_MAP[0]) or row < 0 or row >= len(TERRAIN_MAP):
                    break

                terrain = TERRAIN_MAP[row][col]

                if terrain == 1:  # Stone wall
                    dist = depth * math.cos(current_angle - self.player.angle)
                    wall_distances[ray] = dist
                    wall_height = min(SCREEN_HEIGHT, (TILE_SIZE * SCREEN_HEIGHT) / (dist + 0.0001))

                    color_val = max(30, min(180, int(200 - (dist * 0.12))))
                    color = f"#{color_val:02x}{color_val:02x}{color_val:02x}"

                    x_start = ray * SCALE
                    y_start = (SCREEN_HEIGHT / 2) - (wall_height / 2)

                    self.canvas.create_rectangle(x_start, y_start, x_start + SCALE, y_start + wall_height,
                                                fill=color, outline="")
                    break

                elif terrain == 5:  # Trenches/foxholes
                    dist = depth * math.cos(current_angle - self.player.angle)
                    wall_distances[ray] = dist
                    wall_height = min(SCREEN_HEIGHT, (TILE_SIZE * SCREEN_HEIGHT) / (dist + 0.0001))

                    color = f"#{int(80 - dist*0.01):02x}{int(60 - dist*0.01):02x}{int(40 - dist*0.01):02x}"

                    x_start = ray * SCALE
                    y_start = (SCREEN_HEIGHT / 2) - (wall_height / 2)
                    self.canvas.create_rectangle(x_start, y_start, x_start + SCALE, y_start + wall_height,
                                                fill=color, outline="")
                    break

                elif terrain == 3:  # Bunkers/crates
                    dist = depth * math.cos(current_angle - self.player.angle)
                    wall_distances[ray] = dist
                    wall_height = min(SCREEN_HEIGHT, (TILE_SIZE * SCREEN_HEIGHT) / (dist + 0.0001))

                    color = "#6b4423"
                    x_start = ray * SCALE
                    y_start = (SCREEN_HEIGHT / 2) - (wall_height / 2)
                    self.canvas.create_rectangle(x_start, y_start, x_start + SCALE, y_start + wall_height,
                                                fill=color, outline="")
                    break

                elif terrain == 4:  # Trees
                    dist = depth * math.cos(current_angle - self.player.angle)
                    wall_distances[ray] = dist
                    wall_height = min(SCREEN_HEIGHT, (TILE_SIZE * SCREEN_HEIGHT) / (dist + 0.0001))

                    color = "#1a3d1a"
                    x_start = ray * SCALE
                    y_start = (SCREEN_HEIGHT / 2) - (wall_height / 2)
                    self.canvas.create_rectangle(x_start, y_start, x_start + SCALE, y_start + wall_height,
                                                fill=color, outline="")
                    break

        # Render enemies
        active_enemies = [e for e in self.enemies if e.alive]
        active_enemies.sort(key=lambda e: math.sqrt((e.x - self.player.x)**2 + (e.y - self.player.y)**2), reverse=True)

        for enemy in active_enemies:
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            dist = math.sqrt(dx**2 + dy**2)

            if dist > 10:
                sprite_angle = math.atan2(dy, dx) - self.player.angle
                while sprite_angle > math.pi:
                    sprite_angle -= 2 * math.pi
                while sprite_angle < -math.pi:
                    sprite_angle += 2 * math.pi

                if abs(sprite_angle) < HALF_FOV:
                    screen_x = int((SCREEN_WIDTH / 2) + (math.tan(sprite_angle) * (SCREEN_WIDTH / 2)))
                    sprite_size = min(SCREEN_HEIGHT - 80, int((TILE_SIZE * SCREEN_HEIGHT) / (dist + 1)))

                    ray_idx = int((screen_x / SCREEN_WIDTH) * CASTED_RAYS)
                    if 0 <= ray_idx < CASTED_RAYS and wall_distances[ray_idx] > dist:
                        sx = screen_x - sprite_size // 2
                        sy = (SCREEN_HEIGHT // 2) - sprite_size // 2

                        # Tank body
                        body_color = enemy.color
                        if enemy.hit_flash > 0:
                            body_color = "#ffff00"

                        self.canvas.create_rectangle(sx, sy, sx + sprite_size, sy + sprite_size,
                                                    fill=body_color, outline="#000000", width=2)

                        # Turret
                        turret_center_x = screen_x
                        turret_center_y = sy + sprite_size // 3
                        turret_size = sprite_size // 4
                        self.canvas.create_oval(turret_center_x - turret_size, turret_center_y - turret_size,
                                              turret_center_x + turret_size, turret_center_y + turret_size,
                                              fill=enemy.color, outline="#000000", width=2)

                        # Cannon barrel
                        cannon_len = sprite_size // 2
                        cannon_x2 = turret_center_x + math.cos(enemy.cannon_angle - self.player.angle) * cannon_len
                        cannon_y2 = turret_center_y + math.sin(enemy.cannon_angle - self.player.angle) * cannon_len
                        self.canvas.create_line(turret_center_x, turret_center_y, cannon_x2, cannon_y2,
                                              fill="#1a1a1a", width=3)

                        # HP bar
                        bar_width = sprite_size
                        bar_height = 5
                        bar_x = sx
                        bar_y = sy - 15

                        self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                                                    fill="#1a1a1a", outline="white", width=1)
                        hp_percent = max(0, enemy.hp / enemy.max_hp)
                        bar_color = "#00ff00" if hp_percent > 0.6 else "#ffff00" if hp_percent > 0.3 else "#ff0000"
                        self.canvas.create_rectangle(bar_x, bar_y, bar_x + (bar_width * hp_percent), bar_y + bar_height,
                                                    fill=bar_color, outline="")

                        # Tank name
                        self.canvas.create_text(screen_x, sy - 30, text=enemy.name,
                                              fill="white", font=("Courier", 9, "bold"))

                        # Status indicators
                        status_y = sy + sprite_size + 12
                        if enemy.on_fire:
                            self.canvas.create_text(screen_x, status_y, text="🔥 ON FIRE", fill="red", font=("Courier", 8))
                        if enemy.track_damage > 50:
                            self.canvas.create_text(screen_x, status_y + 12, text="IMMOBILIZED", fill="orange", font=("Courier", 8))

    def draw_ui(self):
        """Enhanced HUD with WW2 information"""
        # Sky and terrain
        self.canvas.create_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT / 2.5, fill="#87ceeb", tags="bg")
        self.canvas.create_rectangle(0, SCREEN_HEIGHT / 2.5, SCREEN_WIDTH, SCREEN_HEIGHT / 2, fill="#6fa8d3", tags="bg")
        self.canvas.create_rectangle(0, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, fill="#5a8a47", tags="bg")
        self.canvas.tag_lower("bg")

        # Player info
        self.canvas.create_text(15, 15, anchor="nw", fill="lime", font=("Courier", 13, "bold"),
                               text=f"{self.player.name} - HP: {int(self.player.hp)}/{int(self.player.max_hp)}")
        
        armor_status = f"ARMOR: {int(self.player.armor_front)}mm"
        if self.player.track_damage > 0:
            armor_status += f" | TRACK DAMAGE: {int(self.player.track_damage)}"
        self.canvas.create_text(15, 40, anchor="nw", fill="yellow", font=("Courier", 10),
                               text=armor_status)

        # Score and kills
        self.canvas.create_text(SCREEN_WIDTH - 15, 15, anchor="ne", fill="white", font=("Courier", 13, "bold"),
                               text=f"SCORE: {self.score}")
        self.canvas.create_text(SCREEN_WIDTH - 15, 40, anchor="ne", fill="white", font=("Courier", 11),
                               text=f"KILLS: {self.kills} | TIME: {int(self.survival_time/60)}s")

        # Enemy count
        alive_enemies = len([e for e in self.enemies if e.alive])
        self.canvas.create_text(SCREEN_WIDTH / 2, 15, anchor="n", fill="white", font=("Courier", 12, "bold"),
                               text=f"ENEMIES: {alive_enemies}/{len(self.enemies)}")

        # Advanced crosshair
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        cross_color = "red" if not self.player.can_fire() else "lime"
        cross_size = 20

        self.canvas.create_line(cx - cross_size, cy, cx + cross_size, cy, fill=cross_color, width=2)
        self.canvas.create_line(cx, cy - cross_size, cx, cy + cross_size, fill=cross_color, width=2)
        self.canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill=cross_color, outline="")

        # Reload indicator
        if not self.player.can_fire():
            reload_percent = 1 - (self.player.cannon_cooldown / self.player.reload_time)
            bar_width = 180
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            bar_y = SCREEN_HEIGHT - 50

            self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + 20, 
                                        fill="#1a1a1a", outline="lime", width=2)
            self.canvas.create_rectangle(bar_x + 2, bar_y + 2, bar_x + 2 + (bar_width - 4) * reload_percent, 
                                        bar_y + 18, fill="lime")
            reload_time = self.player.reload_time / FPS
            self.canvas.create_text(bar_x + bar_width // 2, bar_y + 10, 
                                   text=f"RELOADING {reload_time:.1f}s", fill="white", font=("Courier", 9, "bold"))

        # Status warnings
        warning_y = SCREEN_HEIGHT - 120
        if self.player.on_fire:
            self.canvas.create_text(SCREEN_WIDTH // 2, warning_y, text="⚠ ENGINE ON FIRE ⚠",
                                   fill="red", font=("Courier", 11, "bold"))
        if self.player.track_damage > 40:
            self.canvas.create_text(SCREEN_WIDTH // 2, warning_y + 25, text="⚠ TRACK DAMAGED",
                                   fill="orange", font=("Courier", 10, "bold"))
        if self.player.turret_jammed:
            self.canvas.create_text(SCREEN_WIDTH // 2, warning_y + 50, text="⚠ TURRET JAMMED",
                                   fill="yellow", font=("Courier", 10, "bold"))

        # FPS
        self.canvas.create_text(SCREEN_WIDTH - 15, SCREEN_HEIGHT - 15, anchor="se", fill="white", 
                               font=("Courier", 9), text=f"FPS: {int(self.fps)}")

        # Pause
        if self.paused:
            self.canvas.create_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fill="black", stipple="gray50")
            self.canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, text="⏸ PAUSED",
                                   fill="white", font=("Courier", 48, "bold"))
            self.canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60, text="Press P to Resume",
                                   fill="white", font=("Courier", 16))

        # Game over
        if not self.game_active:
            self.canvas.create_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fill="#330000", stipple="gray50")
            self.canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60, text="TANK DESTROYED",
                                   fill="red", font=("Courier", 50, "bold"))
            self.canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20,
                                   text=f"Final Score: {self.score} | Kills: {self.kills}",
                                   fill="white", font=("Courier", 16))
            self.canvas.create_text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                                   text=f"Survival Time: {int(self.survival_time/60)} seconds",
                                   fill="white", font=("Courier", 14))

    def draw_minimap(self):
        """WW2 battlefield minimap"""
        if not self.show_minimap:
            return

        minimap_size = 220
        minimap_x = SCREEN_WIDTH - minimap_size - 15
        minimap_y = 70

        self.canvas.create_rectangle(minimap_x, minimap_y, minimap_x + minimap_size, minimap_y + minimap_size,
                                    fill="#0a0a0a", outline="lime", width=2)

        tile_scale = minimap_size / len(TERRAIN_MAP[0])

        for row in range(len(TERRAIN_MAP)):
            for col in range(len(TERRAIN_MAP[0])):
                x0 = minimap_x + col * tile_scale
                y0 = minimap_y + row * tile_scale

                if TERRAIN_MAP[row][col] == 1:
                    self.canvas.create_rectangle(x0, y0, x0 + tile_scale, y0 + tile_scale, fill="#444444", outline="")
                elif TERRAIN_MAP[row][col] == 5:
                    self.canvas.create_rectangle(x0, y0, x0 + tile_scale, y0 + tile_scale, fill="#8B4513", outline="")
                elif TERRAIN_MAP[row][col] == 3:
                    self.canvas.create_rectangle(x0, y0, x0 + tile_scale, y0 + tile_scale, fill="#6b4423", outline="")
                elif TERRAIN_MAP[row][col] == 4:
                    self.canvas.create_rectangle(x0, y0, x0 + tile_scale, y0 + tile_scale, fill="#2d5016", outline="")

        # Player
        player_map_x = minimap_x + (self.player.x / (len(TERRAIN_MAP[0]) * TILE_SIZE)) * minimap_size
        player_map_y = minimap_y + (self.player.y / (len(TERRAIN_MAP) * TILE_SIZE)) * minimap_size
        self.canvas.create_oval(player_map_x - 5, player_map_y - 5, player_map_x + 5, player_map_y + 5,
                               fill="lime", outline="white", width=2)

        # Enemies
        for enemy in self.enemies:
            if enemy.alive:
                enemy_map_x = minimap_x + (enemy.x / (len(TERRAIN_MAP[0]) * TILE_SIZE)) * minimap_size
                enemy_map_y = minimap_y + (enemy.y / (len(TERRAIN_MAP) * TILE_SIZE)) * minimap_size
                self.canvas.create_oval(enemy_map_x - 3, enemy_map_y - 3, enemy_map_x + 3, enemy_map_y + 3,
                                       fill="red", outline="darkred", width=1)

    def update_projectiles(self):
        """Advanced ballistic system"""
        for projectile in self.projectiles[:]:
            if not projectile.update(TERRAIN_MAP):
                self.projectiles.remove(projectile)
                continue

            # Enemy collision
            for enemy in self.enemies:
                if not enemy.alive:
                    continue

                dx = enemy.x - projectile.x
                dy = enemy.y - projectile.y
                dist = math.sqrt(dx**2 + dy**2)

                if dist < 35:
                    impact_angle = math.atan2(dy, dx)
                    penetrated = enemy.take_damage(projectile.gun_power, projectile.penetration, impact_angle)

                    # Explosion particles
                    for _ in range(25):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(4, 10)
                        self.particles.append(Particle(
                            projectile.x, projectile.y,
                            math.cos(angle) * speed,
                            math.sin(angle) * speed,
                            60, "#ff8800" if penetrated else "#ffff00", size=6
                        ))

                    if penetrated:
                        self.score += 100
                        if not enemy.alive:
                            self.score += 300
                            self.kills += 1

                            if all(not e.alive for e in self.enemies):
                                self.spawn_enemies(len(self.enemies) + 1)

                    projectile.active = False
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    break

    def update_particles(self):
        """Update particles"""
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)

        for enemy in self.enemies:
            for particle in enemy.particles[:]:
                if not particle.update():
                    enemy.particles.remove(particle)

    def game_loop(self):
        frame_start = time.time()

        if self.game_active and not self.paused:
            self.player.update(TERRAIN_MAP, self.enemies)

            for enemy in self.enemies:
                enemy.update(TERRAIN_MAP, self.player)

            self.update_projectiles()
            self.update_particles()
            self.survival_time += 1

            # Proximity ramming damage
            for enemy in self.enemies:
                if enemy.alive:
                    dx = enemy.x - self.player.x
                    dy = enemy.y - self.player.y
                    dist = math.sqrt(dx**2 + dy**2)

                    if dist < 45:
                        self.player.take_damage(1, 30, math.atan2(dy, dx))

            if self.player.hp <= 0:
                self.game_active = False

        # Render
        self.canvas.delete("all")
        self.cast_rays()
        self.draw_minimap()
        self.draw_ui()

        self.frame_count += 1
        frame_end = time.time()
        frame_time = frame_end - frame_start
        self.fps = 1.0 / frame_time if frame_time > 0 else 0

        self.root.after(FRAME_TIME, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = Tank3DWW2Battlefield(root)
    root.mainloop()

"""The Ashen Titan: a telegraphed, two-phase dungeon boss."""

import math

import pygame


class DungeonBoss:
    """A heavy guardian with dodgeable slams and a phase-two shockwave."""

    NAME = "THE ASHEN TITAN"
    MAX_HEALTH = 780
    XP_REWARD = 150

    SLAM_RANGE = 118
    SLAM_RADIUS = 74
    SLAM_DAMAGE = 28
    SLAM_WINDUP = 0.82
    SLAM_COOLDOWN = 1.55

    PULSE_TRIGGER_RANGE = 258
    PULSE_RADIUS = 178
    PULSE_DAMAGE = 23
    PULSE_WINDUP = 1.15
    PULSE_COOLDOWN = 6.2

    def __init__(self, x, y):
        self.rect = pygame.Rect(int(x), int(y), 48, 48)
        self.max_health = self.MAX_HEALTH
        self.health = self.max_health
        self.xp_reward = self.XP_REWARD

        self.speed = 92
        self.phase_two_speed = 126

        self.state = "approach"
        self.state_timer = 0.0
        self.attack_cooldown = 0.0
        self.special_cooldown = 4.5
        self.telegraph_position = None
        self.hit_flash_timer = 0.0

        self.path = []
        self.path_goal = None
        self.path_refresh_timer = 0.0

        self.title_font = pygame.font.Font(None, 25)
        self.health_font = pygame.font.Font(None, 20)

    @property
    def is_phase_two(self):
        return self.health <= self.max_health * 0.5 and not self.is_dead()

    @property
    def is_telegraphing(self):
        return self.state in ("slam_windup", "pulse_windup")

    def is_dead(self):
        return self.health <= 0

    def take_damage(self, damage):
        """Apply damage and preserve the boss's health bounds."""
        if self.is_dead():
            return
        self.health = max(0, self.health - max(0, int(damage)))
        self.hit_flash_timer = 0.12

    def update(self, player, dt, world):
        """Advance boss AI, including warning periods before every attack."""
        if self.is_dead():
            return

        dt = max(0.0, float(dt))
        self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        if self.state == "slam_windup":
            self.state_timer = max(0.0, self.state_timer - dt)
            if self.state_timer <= 0.0:
                self._resolve_slam(player)
            return

        if self.state == "pulse_windup":
            self.state_timer = max(0.0, self.state_timer - dt)
            if self.state_timer <= 0.0:
                self._resolve_pulse(player)
            return

        if self.state == "recover":
            self.state_timer = max(0.0, self.state_timer - dt)
            if self.state_timer <= 0.0:
                self.state = "approach"
            return

        if self.is_phase_two:
            self.special_cooldown = max(0.0, self.special_cooldown - dt)
            if (
                self.special_cooldown <= 0.0
                and distance <= self.PULSE_TRIGGER_RANGE
            ):
                self.state = "pulse_windup"
                self.state_timer = self.PULSE_WINDUP
                self.telegraph_position = self.rect.center
                self.special_cooldown = self.PULSE_COOLDOWN
                return

        if distance <= self.SLAM_RANGE and self.attack_cooldown <= 0.0:
            self.state = "slam_windup"
            self.state_timer = self.SLAM_WINDUP
            # Lock the target on telegraph start. Movement after this moment
            # lets a player evade the impact instead of tracking unfairly.
            self.telegraph_position = player.rect.center
            self.attack_cooldown = (
                self.SLAM_COOLDOWN * (0.78 if self.is_phase_two else 1.0)
            )
            return

        self._move_toward(player, dt, world)

    def _resolve_slam(self, player):
        target = self.telegraph_position
        if target is not None:
            distance = math.hypot(
                player.rect.centerx - target[0],
                player.rect.centery - target[1],
            )
            if distance <= self.SLAM_RADIUS:
                player.take_damage(
                    self.SLAM_DAMAGE + (4 if self.is_phase_two else 0)
                )
        self.state = "recover"
        self.state_timer = 0.68
        self.telegraph_position = None

    def _resolve_pulse(self, player):
        center = self.telegraph_position or self.rect.center
        distance = math.hypot(
            player.rect.centerx - center[0],
            player.rect.centery - center[1],
        )
        if distance <= self.PULSE_RADIUS:
            player.take_damage(self.PULSE_DAMAGE)
        self.state = "recover"
        self.state_timer = 0.82
        self.telegraph_position = None

    def _move_toward(self, player, dt, world):
        """Follow the dungeon's real floor paths instead of crossing walls."""
        tile_size = world.TILE_SIZE
        current_tile = (
            self.rect.x // tile_size,
            self.rect.y // tile_size,
        )
        goal_tile = (
            player.rect.x // tile_size,
            player.rect.y // tile_size,
        )
        aligned = (
            self.rect.x % tile_size == 0
            and self.rect.y % tile_size == 0
        )
        self.path_refresh_timer = max(0.0, self.path_refresh_timer - dt)

        if (
            aligned
            and (
                self.path_refresh_timer <= 0.0
                or goal_tile != self.path_goal
            )
        ):
            route = world.find_path(current_tile, goal_tile)
            self.path = route[1:] if len(route) > 1 else []
            self.path_goal = goal_tile
            self.path_refresh_timer = 0.45

        if not self.path:
            return

        target_column, target_row = self.path[0]
        target_x = target_column * tile_size
        target_y = target_row * tile_size
        dx = target_x - self.rect.x
        dy = target_y - self.rect.y

        if abs(dx) <= 1 and abs(dy) <= 1:
            self.rect.x = target_x
            self.rect.y = target_y
            self.path.pop(0)
            if not self.path:
                return
            target_column, target_row = self.path[0]
            target_x = target_column * tile_size
            target_y = target_row * tile_size
            dx = target_x - self.rect.x
            dy = target_y - self.rect.y

        move_speed = self.phase_two_speed if self.is_phase_two else self.speed
        step = max(1, int(move_speed * dt))

        candidate = self.rect.copy()
        if dx:
            candidate.x += max(-step, min(step, dx))
            if not world.collides_with_wall(candidate):
                self.rect.x = candidate.x
            else:
                self.path = []
                self.path_refresh_timer = 0.0

        candidate = self.rect.copy()
        if dy:
            candidate.y += max(-step, min(step, dy))
            if not world.collides_with_wall(candidate):
                self.rect.y = candidate.y
            else:
                self.path = []
                self.path_refresh_timer = 0.0

    def render(self, screen, camera):
        """Draw a broad, ember-cracked armored silhouette in pixel-art style."""
        if self.is_dead():
            return

        rect = camera.apply(self.rect)
        cx = rect.centerx
        y = rect.y
        outline = (12, 13, 17)
        armor = (48, 51, 58)
        armor_light = (94, 91, 83)
        ember = (226, 70, 37) if self.is_phase_two else (230, 135, 49)
        ember_light = (255, 190, 87)

        pygame.draw.ellipse(
            screen, (8, 8, 10),
            pygame.Rect(cx - 40, rect.bottom - 5, 80, 18),
        )

        # Crown and broken horns.
        pygame.draw.polygon(
            screen, outline,
            [(cx - 25, y + 17), (cx - 35, y - 3), (cx - 13, y + 8),
             (cx, y - 11), (cx + 13, y + 8), (cx + 35, y - 3),
             (cx + 25, y + 18)],
        )
        pygame.draw.polygon(
            screen, (79, 73, 69),
            [(cx - 26, y + 15), (cx - 31, y + 2), (cx - 13, y + 14),
             (cx, y - 6), (cx + 13, y + 14), (cx + 31, y + 2),
             (cx + 25, y + 16)],
        )

        # Broad shoulder plates and segmented chest.
        pygame.draw.polygon(
            screen, outline,
            [(cx - 33, y + 17), (cx - 20, y + 10), (cx + 20, y + 10),
             (cx + 33, y + 19), (cx + 28, y + 46), (cx + 17, y + 58),
             (cx - 17, y + 58), (cx - 28, y + 46)],
        )
        pygame.draw.polygon(
            screen, armor,
            [(cx - 28, y + 20), (cx - 18, y + 14), (cx + 18, y + 14),
             (cx + 28, y + 21), (cx + 23, y + 43), (cx + 14, y + 52),
             (cx - 14, y + 52), (cx - 23, y + 43)],
        )
        pygame.draw.polygon(
            screen, armor_light,
            [(cx - 25, y + 21), (cx - 16, y + 17), (cx - 8, y + 23),
             (cx - 11, y + 43), (cx - 21, y + 40)],
        )
        pygame.draw.polygon(
            screen, (31, 35, 41),
            [(cx - 9, y + 22), (cx + 8, y + 22),
             (cx + 13, y + 45), (cx, y + 50),
             (cx - 13, y + 45)],
        )

        # The face is a dark mask with glowing eyes and a fractured ember core.
        pygame.draw.polygon(
            screen, outline,
            [(cx - 16, y + 6), (cx - 10, y - 1), (cx + 10, y - 1),
             (cx + 16, y + 7), (cx + 13, y + 21),
             (cx, y + 27), (cx - 13, y + 21)],
        )
        pygame.draw.polygon(
            screen, (28, 27, 30),
            [(cx - 12, y + 7), (cx - 7, y + 3), (cx + 7, y + 3),
             (cx + 12, y + 8), (cx + 10, y + 18),
             (cx, y + 22), (cx - 10, y + 18)],
        )
        pygame.draw.polygon(
            screen, ember,
            [(cx - 10, y + 11), (cx - 3, y + 9),
             (cx - 5, y + 14), (cx - 11, y + 15)],
        )
        pygame.draw.polygon(
            screen, ember,
            [(cx + 10, y + 11), (cx + 3, y + 9),
             (cx + 5, y + 14), (cx + 11, y + 15)],
        )
        pygame.draw.line(
            screen, ember_light, (cx - 2, y + 16), (cx + 3, y + 19), 2
        )
        pygame.draw.line(
            screen, (18, 20, 25), (cx, y + 24), (cx - 4, y + 37), 3
        )
        pygame.draw.line(
            screen, ember, (cx + 6, y + 29), (cx + 2, y + 39), 2
        )

        # Armored greaves and a stone maul.
        pygame.draw.rect(screen, outline, (cx - 20, y + 48, 15, 16))
        pygame.draw.rect(screen, armor_light, (cx - 17, y + 51, 8, 11))
        pygame.draw.rect(screen, outline, (cx + 5, y + 48, 15, 16))
        pygame.draw.rect(screen, armor_light, (cx + 8, y + 51, 8, 11))
        pygame.draw.line(screen, outline, (cx + 27, y + 29), (cx + 36, y + 55), 7)
        pygame.draw.line(screen, (116, 88, 61), (cx + 27, y + 29), (cx + 36, y + 55), 3)
        pygame.draw.rect(screen, outline, (cx + 28, y + 16, 19, 19))
        pygame.draw.rect(screen, (76, 78, 81), (cx + 31, y + 19, 13, 13))
        pygame.draw.line(screen, ember, (cx + 34, y + 21), (cx + 41, y + 27), 2)

        if self.hit_flash_timer > 0:
            pygame.draw.rect(screen, (255, 245, 220), rect.inflate(-14, -14), 2)

    def render_telegraph(self, screen, camera):
        """Render readable danger zones over the finished scene."""
        if not self.is_telegraphing or self.telegraph_position is None:
            return

        world_x, world_y = self.telegraph_position
        world_point = pygame.Rect(int(world_x), int(world_y), 1, 1)
        center = camera.apply(world_point).topleft
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        if self.state == "slam_windup":
            radius = self.SLAM_RADIUS
            fill = (226, 49, 37, 48)
            edge = (255, 89, 55)
            inner = (255, 184, 94)
        else:
            radius = self.PULSE_RADIUS
            fill = (239, 51, 34, 43)
            edge = (255, 75, 45)
            inner = (255, 173, 76)

        pygame.draw.circle(overlay, fill, center, radius)
        screen.blit(overlay, (0, 0))
        pygame.draw.circle(screen, edge, center, radius, 4)
        pygame.draw.circle(screen, inner, center, max(3, radius - 9), 2)

        # A shrinking inner ring makes the warning countdown legible without
        # introducing a new timer widget over the established HUD.
        duration = self.SLAM_WINDUP if self.state == "slam_windup" else self.PULSE_WINDUP
        fraction = max(0.0, min(1.0, self.state_timer / duration))
        inner_radius = max(3, int(radius * fraction))
        pygame.draw.circle(screen, edge, center, inner_radius, 2)

    def render_health_bar(self, screen):
        """Show the boss name and a dedicated full-width boss health meter."""
        if self.is_dead():
            return

        width, _ = screen.get_size()
        panel_width = min(540, width - 32)
        panel_height = 56
        panel = pygame.Rect(
            (width - panel_width) // 2,
            96,
            panel_width,
            panel_height,
        )
        pygame.draw.rect(screen, (3, 5, 8), panel.move(3, 4))
        pygame.draw.rect(screen, (12, 16, 22), panel)
        pygame.draw.rect(screen, (113, 63, 42), panel, 2)
        pygame.draw.rect(screen, (202, 144, 74), panel.inflate(-5, -5), 1)

        name = self.title_font.render(self.NAME, True, (245, 187, 103))
        health_text = self.health_font.render(
            f"{self.health:,} / {self.max_health:,}",
            True, (228, 222, 209),
        )
        screen.blit(name, (panel.left + 17, panel.top + 5))
        screen.blit(
            health_text,
            (panel.right - 17 - health_text.get_width(), panel.top + 8),
        )

        bar = pygame.Rect(
            panel.left + 17, panel.top + 32, panel.width - 34, 13
        )
        pygame.draw.rect(screen, (32, 18, 19), bar)
        ratio = max(0.0, min(1.0, self.health / self.max_health))
        fill_width = int(bar.width * ratio)
        if fill_width > 0:
            color = (238, 77, 43) if self.is_phase_two else (176, 41, 39)
            pygame.draw.rect(
                screen, color,
                pygame.Rect(bar.x, bar.y, fill_width, bar.height),
            )
            pygame.draw.line(
                screen, (255, 166, 104),
                (bar.x, bar.y), (bar.x + fill_width - 1, bar.y), 1,
            )
        pygame.draw.rect(screen, (77, 44, 36), bar, 1)

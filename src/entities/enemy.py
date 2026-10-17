import pygame
import math


class Enemy:

    def __init__(
        self,
        x,
        y,
        enemy_type="Goblin"
    ):

        self.x = x
        self.y = y

        self.width = 40
        self.height = 40

        # ==================================================
        # ENEMY TYPE
        # ==================================================

        self.enemy_type = enemy_type

        # ==================================================
        # DEFAULT STATS
        # ==================================================

        self.max_health = 60
        self.health = self.max_health

        self.speed = 150

        self.attack_damage = 10
        self.attack_cooldown = 1.0

        self.xp_reward = 10

        self.color = (
            200,
            60,
            60
        )

        # ==================================================
        # ENEMY VARIANTS
        # ==================================================

        if enemy_type == "Orc":

            self.max_health = 120
            self.health = self.max_health

            self.speed = 90

            self.attack_damage = 20
            self.attack_cooldown = 1.2

            self.xp_reward = 25

            self.color = (
                100,
                160,
                70
            )

        elif enemy_type == "Skeleton":

            self.max_health = 80
            self.health = self.max_health

            self.speed = 120

            self.attack_damage = 15
            self.attack_cooldown = 1.0

            self.xp_reward = 15

            self.color = (
                190,
                190,
                190
            )

        # ==================================================
        # MOVEMENT
        # ==================================================

        self.stop_distance = 55

        # ==================================================
        # ATTACK
        # ==================================================

        self.attack_range = 60
        self.attack_timer = 0.0

        # ==================================================
        # HIT FLASH
        # ==================================================

        self.hit_flash_timer = 0.0
        self.hit_flash_duration = 0.10

        # ==================================================
        # RECT
        # ==================================================

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        player,
        dt,
        world
    ):

        if self.is_dead():
            return

        # ==================================================
        # HIT FLASH TIMER
        # ==================================================

        if self.hit_flash_timer > 0:

            self.hit_flash_timer -= dt

        # ==================================================
        # ATTACK TIMER
        # ==================================================

        if self.attack_timer > 0:

            self.attack_timer -= dt

        # ==================================================
        # DISTANCE TO PLAYER
        # ==================================================

        dx = (
            player.rect.centerx
            - self.rect.centerx
        )

        dy = (
            player.rect.centery
            - self.rect.centery
        )

        distance = math.sqrt(
            dx ** 2 + dy ** 2
        )

        # ==================================================
        # ENEMY ATTACK
        # ==================================================

        if distance <= self.attack_range:

            if self.attack_timer <= 0:

                player.take_damage(
                    self.attack_damage
                )

                self.attack_timer = (
                    self.attack_cooldown
                )

            return

        # ==================================================
        # STOP DISTANCE
        # ==================================================

        if distance <= self.stop_distance:

            return

        # ==================================================
        # NORMALIZE DIRECTION
        # ==================================================

        if distance > 0:

            dx /= distance
            dy /= distance

        movement_x = (
            dx
            * self.speed
            * dt
        )

        movement_y = (
            dy
            * self.speed
            * dt
        )

        # ==================================================
        # HORIZONTAL MOVEMENT
        # ==================================================

        new_rect = self.rect.copy()

        new_rect.x += int(
            movement_x
        )

        if not world.collides_with_wall(
            new_rect
        ):

            self.rect.x = new_rect.x

        # ==================================================
        # VERTICAL MOVEMENT
        # ==================================================

        new_rect = self.rect.copy()

        new_rect.y += int(
            movement_y
        )

        if not world.collides_with_wall(
            new_rect
        ):

            self.rect.y = new_rect.y

        # ==================================================
        # SYNC POSITION
        # ==================================================

        self.x = self.rect.x
        self.y = self.rect.y

    # ======================================================
    # TAKE DAMAGE
    # ======================================================

    def take_damage(
        self,
        damage
    ):

        if self.is_dead():
            return

        self.health -= damage

        self.hit_flash_timer = (
            self.hit_flash_duration
        )

        if self.health < 0:

            self.health = 0

    # ======================================================
    # IS DEAD
    # ======================================================

    def is_dead(self):

        return self.health <= 0

    # ======================================================
    # RENDER
    # ======================================================

    def render(self, screen, camera):
        """Draw compact, original pixel-art enemies with readable silhouettes."""
        screen_rect = camera.apply(self.rect)
        x, y = screen_rect.x, screen_rect.y
        cx = screen_rect.centerx
        bone = (230, 218, 187)
        bone_light = (255, 246, 218)
        outline = (16, 17, 20)
        dark = (35, 34, 32)

        if self.hit_flash_timer > 0:
            bone = (255, 255, 255)
            bone_light = (255, 255, 255)

        # Shared soft shadow gives the sprites a little depth over the floor.
        shadow = pygame.Surface((48, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 120), (2, 2, 44, 10))
        screen.blit(shadow, (cx - 24, screen_rect.bottom - 8))

        if self.enemy_type == "Skeleton":
            # Skull and jaw.
            skull = pygame.Rect(x + 11, y + 3, 18, 15)
            pygame.draw.rect(screen, outline, skull.inflate(2, 2))
            pygame.draw.polygon(
                screen, bone,
                [(x + 13, y + 5), (x + 17, y + 3), (x + 24, y + 4),
                 (x + 28, y + 8), (x + 27, y + 14), (x + 23, y + 17),
                 (x + 16, y + 16), (x + 12, y + 12)]
            )
            pygame.draw.line(screen, bone_light, (x + 16, y + 5), (x + 23, y + 5), 1)
            pygame.draw.rect(screen, dark, (x + 15, y + 8, 4, 4))
            pygame.draw.rect(screen, dark, (x + 22, y + 8, 4, 4))
            pygame.draw.polygon(
                screen, outline,
                [(x + 20, y + 11), (x + 18, y + 14), (x + 21, y + 14)]
            )
            pygame.draw.rect(screen, bone, (x + 15, y + 15, 11, 3))
            for tooth_x in (17, 20, 23):
                pygame.draw.line(
                    screen, (101, 91, 74),
                    (x + tooth_x, y + 15), (x + tooth_x, y + 18), 1
                )

            # Spine and ribs.
            pygame.draw.line(screen, outline, (cx, y + 18), (cx, y + 30), 5)
            pygame.draw.line(screen, bone, (cx, y + 18), (cx, y + 29), 2)
            for rib_y, rib_w in ((20, 8), (23, 9), (26, 7)):
                pygame.draw.arc(
                    screen, outline,
                    pygame.Rect(cx - rib_w, y + rib_y - 2, rib_w * 2, 6),
                    0, 3.14, 3
                )
                pygame.draw.arc(
                    screen, bone,
                    pygame.Rect(cx - rib_w, y + rib_y - 2, rib_w * 2, 6),
                    0, 3.14, 1
                )
            pygame.draw.line(screen, bone, (x + 13, y + 19), (x + 8, y + 26), 3)
            pygame.draw.line(screen, outline, (x + 13, y + 19), (x + 8, y + 26), 5)
            pygame.draw.line(screen, bone, (x + 27, y + 19), (x + 32, y + 25), 3)
            pygame.draw.line(screen, outline, (x + 27, y + 19), (x + 32, y + 25), 5)
            pygame.draw.line(screen, bone, (x + 8, y + 26), (x + 13, y + 28), 3)
            pygame.draw.line(screen, bone, (x + 32, y + 25), (x + 35, y + 22), 3)

            # Uneven femurs and shins.
            pygame.draw.line(screen, outline, (x + 17, y + 29), (x + 13, y + 36), 5)
            pygame.draw.line(screen, bone, (x + 17, y + 29), (x + 13, y + 36), 2)
            pygame.draw.line(screen, outline, (x + 23, y + 29), (x + 28, y + 36), 5)
            pygame.draw.line(screen, bone, (x + 23, y + 29), (x + 28, y + 36), 2)
            pygame.draw.line(screen, bone_light, (x + 10, y + 37), (x + 16, y + 37), 3)
            pygame.draw.line(screen, bone_light, (x + 25, y + 37), (x + 31, y + 37), 3)

            # A chipped short blade and a leather-wrapped hilt.
            pygame.draw.line(screen, outline, (x + 32, y + 25), (x + 39, y + 15), 5)
            pygame.draw.line(screen, (119, 71, 42), (x + 32, y + 25), (x + 35, y + 21), 3)
            pygame.draw.line(screen, (191, 211, 218), (x + 35, y + 20), (x + 39, y + 15), 3)
            pygame.draw.line(screen, (255, 255, 238), (x + 37, y + 18), (x + 39, y + 15), 1)
            pygame.draw.line(screen, (181, 119, 61), (x + 30, y + 22), (x + 35, y + 25), 2)

        elif self.enemy_type == "Orc":
            green_dark = (44, 71, 39)
            green = (103, 151, 68)
            green_light = (157, 191, 93)
            leather = (82, 49, 31)

            # Broad shoulders and muscular body.
            pygame.draw.polygon(
                screen, outline,
                [(x + 6, y + 15), (x + 12, y + 11), (x + 28, y + 11),
                 (x + 35, y + 16), (x + 32, y + 29), (x + 27, y + 32),
                 (x + 12, y + 31), (x + 8, y + 27)]
            )
            pygame.draw.polygon(
                screen, green_dark,
                [(x + 9, y + 16), (x + 14, y + 13), (x + 27, y + 13),
                 (x + 32, y + 17), (x + 29, y + 27), (x + 25, y + 30),
                 (x + 14, y + 29), (x + 11, y + 26)]
            )
            pygame.draw.polygon(
                screen, green,
                [(x + 13, y + 15), (x + 20, y + 14), (x + 26, y + 16),
                 (x + 25, y + 25), (x + 15, y + 25)]
            )
            pygame.draw.rect(screen, leather, (x + 12, y + 27, 17, 4))
            pygame.draw.rect(screen, (216, 159, 65), (x + 19, y + 27, 5, 4))
            pygame.draw.rect(screen, outline, (x + 11, y + 31, 7, 7))
            pygame.draw.rect(screen, outline, (x + 23, y + 31, 7, 7))
            pygame.draw.rect(screen, (58, 65, 54), (x + 12, y + 32, 5, 5))
            pygame.draw.rect(screen, (58, 65, 54), (x + 24, y + 32, 5, 5))

            # Heavy head, brow, eyes, and tusks.
            pygame.draw.polygon(
                screen, outline,
                [(x + 11, y + 5), (x + 16, y + 2), (x + 26, y + 3),
                 (x + 31, y + 7), (x + 28, y + 16), (x + 13, y + 16)]
            )
            pygame.draw.polygon(
                screen, green,
                [(x + 13, y + 6), (x + 17, y + 4), (x + 25, y + 4),
                 (x + 28, y + 8), (x + 26, y + 14), (x + 14, y + 14)]
            )
            pygame.draw.rect(screen, outline, (x + 14, y + 8, 6, 3))
            pygame.draw.rect(screen, outline, (x + 22, y + 8, 5, 3))
            pygame.draw.rect(screen, (245, 186, 68), (x + 16, y + 9, 3, 2))
            pygame.draw.rect(screen, (245, 186, 68), (x + 23, y + 9, 2, 2))
            pygame.draw.polygon(
                screen, (240, 229, 190),
                [(x + 15, y + 12), (x + 18, y + 12), (x + 17, y + 17)]
            )
            pygame.draw.polygon(
                screen, (240, 229, 190),
                [(x + 24, y + 12), (x + 27, y + 12), (x + 26, y + 17)]
            )
            pygame.draw.line(screen, (147, 186, 91), (x + 16, y + 5), (x + 23, y + 5), 1)

            pygame.draw.line(screen, outline, (x + 8, y + 18), (x + 4, y + 27), 6)
            pygame.draw.line(screen, green, (x + 8, y + 18), (x + 4, y + 27), 3)
            pygame.draw.line(screen, outline, (x + 31, y + 18), (x + 36, y + 25), 6)
            pygame.draw.line(screen, green, (x + 31, y + 18), (x + 36, y + 25), 3)
            pygame.draw.line(screen, (189, 204, 190), (x + 35, y + 24), (x + 39, y + 13), 3)

        else:
            # Goblin / default: compact green face, pointed ears, leather tunic.
            green_dark = (33, 62, 37)
            green = (96, 151, 65)
            green_light = (151, 190, 88)
            leather = (104, 61, 36)

            pygame.draw.polygon(
                screen, outline,
                [(x + 12, y + 13), (x + 5, y + 9), (x + 9, y + 19),
                 (x + 12, y + 21)]
            )
            pygame.draw.polygon(
                screen, outline,
                [(x + 28, y + 13), (x + 36, y + 8), (x + 33, y + 20),
                 (x + 28, y + 21)]
            )
            pygame.draw.polygon(
                screen, (98, 140, 58),
                [(x + 12, y + 14), (x + 7, y + 11), (x + 11, y + 18)]
            )
            pygame.draw.polygon(
                screen, (98, 140, 58),
                [(x + 28, y + 14), (x + 34, y + 10), (x + 31, y + 18)]
            )

            pygame.draw.polygon(
                screen, outline,
                [(x + 12, y + 14), (x + 12, y + 6), (x + 17, y + 2),
                 (x + 25, y + 3), (x + 29, y + 8), (x + 28, y + 17),
                 (x + 23, y + 21), (x + 15, y + 19)]
            )
            pygame.draw.polygon(
                screen, green,
                [(x + 14, y + 8), (x + 18, y + 5), (x + 24, y + 5),
                 (x + 27, y + 9), (x + 26, y + 15), (x + 22, y + 18),
                 (x + 16, y + 17)]
            )
            pygame.draw.line(screen, green_light, (x + 17, y + 6), (x + 22, y + 5), 1)
            pygame.draw.rect(screen, outline, (x + 15, y + 9, 4, 4))
            pygame.draw.rect(screen, outline, (x + 22, y + 9, 4, 4))
            pygame.draw.rect(screen, (243, 198, 69), (x + 16, y + 10, 2, 2))
            pygame.draw.rect(screen, (243, 198, 69), (x + 23, y + 10, 2, 2))
            pygame.draw.line(screen, green_dark, (x + 19, y + 15), (x + 23, y + 15), 2)

            pygame.draw.polygon(
                screen, outline,
                [(x + 12, y + 19), (x + 17, y + 17), (x + 24, y + 17),
                 (x + 29, y + 20), (x + 27, y + 30), (x + 13, y + 30)]
            )
            pygame.draw.polygon(
                screen, leather,
                [(x + 14, y + 20), (x + 18, y + 19), (x + 23, y + 19),
                 (x + 27, y + 21), (x + 25, y + 28), (x + 15, y + 28)]
            )
            pygame.draw.line(screen, (146, 94, 49), (x + 17, y + 21), (x + 24, y + 25), 2)
            pygame.draw.rect(screen, (216, 159, 65), (x + 19, y + 27, 4, 3))
            pygame.draw.line(screen, outline, (x + 15, y + 29), (x + 12, y + 36), 5)
            pygame.draw.line(screen, outline, (x + 25, y + 29), (x + 29, y + 36), 5)
            pygame.draw.line(screen, (49, 55, 42), (x + 13, y + 36), (x + 18, y + 36), 3)
            pygame.draw.line(screen, (49, 55, 42), (x + 27, y + 36), (x + 32, y + 36), 3)

            # A short, dark-edged iron weapon in the goblin's right hand.
            pygame.draw.line(screen, outline, (x + 31, y + 25), (x + 38, y + 16), 5)
            pygame.draw.line(screen, leather, (x + 31, y + 25), (x + 34, y + 21), 3)
            pygame.draw.line(screen, (194, 211, 214), (x + 34, y + 21), (x + 38, y + 16), 2)

        # Red, high-contrast enemy health bars remain readable over the dark
        # scene; they shrink with health but do not change to unrelated hues.
        bar_width = 52
        bar_height = 6
        bar_x = screen_rect.centerx - bar_width // 2
        bar_y = screen_rect.top - 13
        background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (20, 10, 12), background_rect)
        ratio = max(0.0, min(1.0, self.health / self.max_health))
        fill_width = int(bar_width * ratio)
        if fill_width > 0:
            pygame.draw.rect(
                screen, (211, 36, 43),
                pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            )
            pygame.draw.line(
                screen, (255, 112, 103),
                (bar_x, bar_y),
                (bar_x + fill_width - 1, bar_y), 1
            )
        pygame.draw.rect(screen, (61, 31, 28), background_rect, 1)

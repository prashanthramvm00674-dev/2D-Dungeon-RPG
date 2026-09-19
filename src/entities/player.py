import pygame
import math


class Player:
    def __init__(self):
        self.x = 640
        self.y = 360

        self.width = 40
        self.height = 40

        self.color = (50, 150, 255)

        self.speed = 300

        self.direction = "down"
        self.is_moving = False

        # -------------------------
        # HEALTH
        # -------------------------

        self.max_health = 100
        self.health = self.max_health

        self.damage_cooldown = 0.0
        self.damage_invulnerability = 0.5

        self.is_dead = False

        # Hit feedback
        self.hit_flash_timer = 0.0
        self.hit_flash_duration = 0.12

        # -------------------------
        # COMBAT
        # -------------------------

        self.is_attacking = False
        self.attack_timer = 0.0
        self.attack_duration = 0.15

        self.attack_cooldown = 0.25
        self.attack_cooldown_timer = 0.0

        self.attack_has_hit = False

        self.attack_width = 40
        self.attack_height = 40
        self.attack_distance = 10

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

        self.attack_rect = pygame.Rect(
            0,
            0,
            self.attack_width,
            self.attack_height
        )

    def update(
        self,
        input_manager,
        dt,
        world
    ):
        if self.is_dead:
            return

        # -------------------------
        # DAMAGE COOLDOWN
        # -------------------------

        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

        # -------------------------
        # HIT FLASH
        # -------------------------

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        # -------------------------
        # COMBAT TIMERS
        # -------------------------

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt

        if self.is_attacking:
            self.attack_timer -= dt

            if self.attack_timer <= 0:
                self.is_attacking = False

        # -------------------------
        # ATTACK
        # -------------------------

        if (
            input_manager.is_pressed(pygame.K_SPACE)
            and not self.is_attacking
            and self.attack_cooldown_timer <= 0
        ):
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.attack_cooldown_timer = self.attack_cooldown
            self.attack_has_hit = False

        # -------------------------
        # MOVEMENT
        # -------------------------

        direction_x = 0
        direction_y = 0

        if input_manager.is_down(pygame.K_a):
            direction_x -= 1

        if input_manager.is_down(pygame.K_d):
            direction_x += 1

        if input_manager.is_down(pygame.K_w):
            direction_y -= 1

        if input_manager.is_down(pygame.K_s):
            direction_y += 1

        self.is_moving = (
            direction_x != 0
            or direction_y != 0
        )

        if direction_x < 0:
            self.direction = "left"

        elif direction_x > 0:
            self.direction = "right"

        elif direction_y < 0:
            self.direction = "up"

        elif direction_y > 0:
            self.direction = "down"

        if self.is_moving:
            length = math.sqrt(
                direction_x ** 2
                + direction_y ** 2
            )

            direction_x /= length
            direction_y /= length

        movement_x = (
            direction_x
            * self.speed
            * dt
        )

        movement_y = (
            direction_y
            * self.speed
            * dt
        )

        # -------------------------
        # HORIZONTAL MOVEMENT
        # -------------------------

        new_rect = self.rect.copy()
        new_rect.x += int(movement_x)

        if not world.collides_with_wall(new_rect):
            self.rect.x = new_rect.x

        # -------------------------
        # VERTICAL MOVEMENT
        # -------------------------

        new_rect = self.rect.copy()
        new_rect.y += int(movement_y)

        if not world.collides_with_wall(new_rect):
            self.rect.y = new_rect.y

        self.x = self.rect.x
        self.y = self.rect.y

        self.update_attack_rect()

    def take_damage(self, damage):
        if self.is_dead:
            return

        if self.damage_cooldown > 0:
            return

        self.health -= damage

        # Start hit flash
        self.hit_flash_timer = (
            self.hit_flash_duration
        )

        # Temporary invulnerability
        self.damage_cooldown = (
            self.damage_invulnerability
        )

        if self.health <= 0:
            self.health = 0
            self.is_dead = True

    def update_attack_rect(self):

        if self.direction == "up":

            self.attack_rect.size = (
                self.attack_width,
                self.attack_height
            )

            self.attack_rect.midbottom = (
                self.rect.centerx,
                self.rect.top
                - self.attack_distance
            )

        elif self.direction == "down":

            self.attack_rect.size = (
                self.attack_width,
                self.attack_height
            )

            self.attack_rect.midtop = (
                self.rect.centerx,
                self.rect.bottom
                + self.attack_distance
            )

        elif self.direction == "left":

            self.attack_rect.size = (
                self.attack_height,
                self.attack_width
            )

            self.attack_rect.midright = (
                self.rect.left
                - self.attack_distance,
                self.rect.centery
            )

        elif self.direction == "right":

            self.attack_rect.size = (
                self.attack_height,
                self.attack_width
            )

            self.attack_rect.midleft = (
                self.rect.right
                + self.attack_distance,
                self.rect.centery
            )

    def render(self, screen, camera):

        screen_rect = camera.apply(
            self.rect
        )

        # -------------------------
        # PLAYER COLOR
        # -------------------------

        if self.hit_flash_timer > 0:
            player_color = (255, 255, 255)
        else:
            player_color = self.color

        pygame.draw.rect(
            screen,
            player_color,
            screen_rect
        )

        # -------------------------
        # ATTACK HITBOX
        # -------------------------

        if self.is_attacking:

            attack_screen_rect = camera.apply(
                self.attack_rect
            )

            pygame.draw.rect(
                screen,
                (255, 80, 80),
                attack_screen_rect
            )

        # -------------------------
        # HEALTH BAR
        # -------------------------

        bar_width = 100
        bar_height = 8

        health_ratio = (
            self.health
            / self.max_health
        )

        background_rect = pygame.Rect(
            screen_rect.centerx
            - bar_width // 2,
            screen_rect.top - 20,
            bar_width,
            bar_height
        )

        health_rect = pygame.Rect(
            screen_rect.centerx
            - bar_width // 2,
            screen_rect.top - 20,
            int(
                bar_width
                * health_ratio
            ),
            bar_height
        )

        pygame.draw.rect(
            screen,
            (60, 60, 60),
            background_rect
        )

        pygame.draw.rect(
            screen,
            (50, 200, 80),
            health_rect
        )
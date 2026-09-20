import pygame
import math


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.width = 40
        self.height = 40

        self.color = (200, 60, 60)

        # -------------------------
        # HEALTH
        # -------------------------

        self.max_health = 100
        self.health = self.max_health

        # -------------------------
        # MOVEMENT
        # -------------------------

        self.speed = 100
        self.stop_distance = 55

        # -------------------------
        # ATTACK
        # -------------------------

        self.attack_range = 60
        self.attack_damage = 10
        self.attack_cooldown = 1.0
        self.attack_timer = 0.0

        # -------------------------
        # HIT FLASH
        # -------------------------

        self.hit_flash_timer = 0.0
        self.hit_flash_duration = 0.10

        # -------------------------
        # RECT
        # -------------------------

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

    def update(self, player, dt, world):

        if self.is_dead():
            return

        # -------------------------
        # HIT FLASH TIMER
        # -------------------------

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        # -------------------------
        # ATTACK TIMER
        # -------------------------

        if self.attack_timer > 0:
            self.attack_timer -= dt

        # -------------------------
        # DISTANCE TO PLAYER
        # -------------------------

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

        # -------------------------
        # ENEMY ATTACK
        # -------------------------

        if distance <= self.attack_range:

            if self.attack_timer <= 0:

                player.take_damage(
                    self.attack_damage
                )

                self.attack_timer = (
                    self.attack_cooldown
                )

            return

        # -------------------------
        # STOP DISTANCE
        # -------------------------

        if distance <= self.stop_distance:
            return

        # -------------------------
        # NORMALIZE DIRECTION
        # -------------------------

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

        # -------------------------
        # HORIZONTAL MOVEMENT
        # -------------------------

        new_rect = self.rect.copy()
        new_rect.x += int(movement_x)

        if not world.collides_with_wall(
            new_rect
        ):
            self.rect.x = new_rect.x

        # -------------------------
        # VERTICAL MOVEMENT
        # -------------------------

        new_rect = self.rect.copy()
        new_rect.y += int(movement_y)

        if not world.collides_with_wall(
            new_rect
        ):
            self.rect.y = new_rect.y

        self.x = self.rect.x
        self.y = self.rect.y

    def take_damage(self, damage):

        if self.is_dead():
            return

        self.health -= damage

        self.hit_flash_timer = (
            self.hit_flash_duration
        )

        if self.health < 0:
            self.health = 0

    def is_dead(self):
        return self.health <= 0

    def render(self, screen, camera):

        screen_rect = camera.apply(
            self.rect
        )

        # -------------------------
        # ENEMY BODY
        # -------------------------

        if self.hit_flash_timer > 0:
            enemy_color = (
                255,
                255,
                255
            )
        else:
            enemy_color = self.color

        pygame.draw.rect(
            screen,
            enemy_color,
            screen_rect
        )

        # -------------------------
        # HEALTH BAR
        # -------------------------

        bar_width = 60
        bar_height = 8

        bar_x = (
            screen_rect.centerx
            - bar_width // 2
        )

        bar_y = (
            screen_rect.top
            - 15
        )

        # Background
        background_rect = pygame.Rect(
            bar_x,
            bar_y,
            bar_width,
            bar_height
        )

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            background_rect
        )

        # -------------------------
        # HEALTH RATIO
        # -------------------------

        health_ratio = (
            self.health
            / self.max_health
        )

        health_width = int(
            bar_width
            * health_ratio
        )

        # -------------------------
        # HEALTH COLOR
        # -------------------------

        if health_ratio > 0.60:

            health_color = (
                50,
                220,
                80
            )

        elif health_ratio > 0.30:

            health_color = (
                255,
                210,
                40
            )

        else:

            health_color = (
                240,
                50,
                50
            )

        # Draw health
        if health_width > 0:

            health_rect = pygame.Rect(
                bar_x,
                bar_y,
                health_width,
                bar_height
            )

            pygame.draw.rect(
                screen,
                health_color,
                health_rect
            )

        # -------------------------
        # BORDER
        # -------------------------

        pygame.draw.rect(
            screen,
            (220, 220, 220),
            background_rect,
            1
        )
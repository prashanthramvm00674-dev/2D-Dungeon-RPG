import pygame
import math


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.width = 40
        self.height = 40

        self.color = (200, 60, 60)

        # Health
        self.max_health = 100
        self.health = self.max_health

        # Movement
        self.speed = 100
        self.stop_distance = 55

        # Attack
        self.attack_range = 60
        self.attack_damage = 10
        self.attack_cooldown = 1.0
        self.attack_timer = 0.0

        # Hit feedback
        self.hit_flash_timer = 0.0
        self.hit_flash_duration = 0.10

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

    def update(self, player, dt, world):
        if self.is_dead():
            return

        # Hit flash timer
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        # Attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Distance to player
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

        # Attack when close
        if distance <= self.attack_range:

            if self.attack_timer <= 0:
                player.take_damage(
                    self.attack_damage
                )

                self.attack_timer = (
                    self.attack_cooldown
                )

            return

        # Stop when close
        if distance <= self.stop_distance:
            return

        # Normalize direction
        if distance > 0:
            dx /= distance
            dy /= distance

        movement_x = dx * self.speed * dt
        movement_y = dy * self.speed * dt

        # Horizontal movement
        new_rect = self.rect.copy()
        new_rect.x += int(movement_x)

        if not world.collides_with_wall(new_rect):
            self.rect.x = new_rect.x

        # Vertical movement
        new_rect = self.rect.copy()
        new_rect.y += int(movement_y)

        if not world.collides_with_wall(new_rect):
            self.rect.y = new_rect.y

        self.x = self.rect.x
        self.y = self.rect.y

    def take_damage(self, damage):
        if self.is_dead():
            return

        self.health -= damage

        # Start hit flash
        self.hit_flash_timer = (
            self.hit_flash_duration
        )

        if self.health < 0:
            self.health = 0

    def is_dead(self):
        return self.health <= 0

    def render(self, screen, camera):
        screen_rect = camera.apply(self.rect)

        # Flash white when hit
        if self.hit_flash_timer > 0:
            enemy_color = (255, 255, 255)
        else:
            enemy_color = self.color

        pygame.draw.rect(
            screen,
            enemy_color,
            screen_rect
        )

        # Health bar
        health_ratio = (
            self.health / self.max_health
        )

        bar_width = self.width
        bar_height = 6

        background_rect = pygame.Rect(
            screen_rect.x,
            screen_rect.y - 10,
            bar_width,
            bar_height
        )

        health_rect = pygame.Rect(
            screen_rect.x,
            screen_rect.y - 10,
            int(bar_width * health_ratio),
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
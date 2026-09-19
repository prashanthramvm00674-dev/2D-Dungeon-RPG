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

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

    def update(
        self,
        input_manager,
        dt,
        world
    ):
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
            direction_x != 0 or direction_y != 0
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
                direction_x ** 2 + direction_y ** 2
            )

            direction_x /= length
            direction_y /= length

        movement_x = direction_x * self.speed * dt
        movement_y = direction_y * self.speed * dt

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

    def render(self, screen, camera):
        screen_rect = camera.apply(self.rect)

        pygame.draw.rect(
            screen,
            self.color,
            screen_rect
        )
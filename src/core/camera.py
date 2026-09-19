import pygame


class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0

        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, target_rect, world_width, world_height):
        # Center camera on player
        self.x = target_rect.centerx - self.screen_width // 2
        self.y = target_rect.centery - self.screen_height // 2

        # Keep camera inside world
        max_x = max(0, world_width - self.screen_width)
        max_y = max(0, world_height - self.screen_height)

        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def apply(self, rect):
        return rect.move(
            -self.x,
            -self.y
        )
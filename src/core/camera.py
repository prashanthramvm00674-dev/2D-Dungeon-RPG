import pygame


class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0

        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(
        self,
        target_rect,
        world_width,
        world_height,
        viewport_width=None,
        viewport_height=None
    ):
        """Track the target while keeping the viewport inside the world."""
        # Update viewport dimensions when the game window is resized.
        if viewport_width is not None:
            self.screen_width = max(1, int(viewport_width))
        if viewport_height is not None:
            self.screen_height = max(1, int(viewport_height))

        # Center camera on player
        self.x = target_rect.centerx - self.screen_width // 2
        self.y = target_rect.centery - self.screen_height // 2

        # Keep camera inside world
        max_x = max(0, world_width - self.screen_width)
        max_y = max(0, world_height - self.screen_height)

        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

        # Keep offsets integral and non-negative for stable pixel rendering.
        self.x = int(self.x)
        self.y = int(self.y)

    def apply(self, rect):
        return rect.move(
            -self.x,
            -self.y
        )
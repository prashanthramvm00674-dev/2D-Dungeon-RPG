import pygame


class DamageNumber:
    def __init__(self, x, y, damage):
        self.x = float(x)
        self.y = float(y)

        self.damage = damage

        self.life = 0.6
        self.max_life = 0.6

        self.speed = 50

        self.font = pygame.font.Font(None, 28)

    def update(self, dt):
        self.y -= self.speed * dt
        self.life -= dt

    def is_finished(self):
        return self.life <= 0

    def render(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y

        alpha = int(
            255 * (self.life / self.max_life)
        )

        text = self.font.render(
            f"-{self.damage}",
            True,
            (255, 220, 80)
        )

        text.set_alpha(alpha)

        rect = text.get_rect(
            center=(
                int(screen_x),
                int(screen_y)
            )
        )

        screen.blit(
            text,
            rect
        )
import pygame

from core.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WINDOW_TITLE,
    FPS,
)

from core.input import InputManager


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.RESIZABLE
        )

        pygame.display.set_caption(WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0.0

        self.input = InputManager()
        self.font = pygame.font.Font(None, 24)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        if self.input.is_pressed(pygame.K_ESCAPE):
            self.running = False

        if self.input.is_pressed(pygame.K_SPACE):
            print("SPACE PRESSED")

        if self.input.is_released(pygame.K_SPACE):
            print("SPACE RELEASED")

    def render(self):
        self.screen.fill((20, 20, 25))

        fps = self.clock.get_fps()

        debug_text = self.font.render(
            f"FPS: {fps:.1f}  DT: {self.dt:.4f}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(debug_text, (10, 10))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.input.update()
            self.update()
            self.render()

        pygame.quit()
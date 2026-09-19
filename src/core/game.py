import pygame

from core.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WINDOW_TITLE,
    FPS,
)

from core.input import InputManager
from core.camera import Camera
from core.damage_number import DamageNumber

from entities.player import Player
from entities.enemy import Enemy

from world.world import World


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

        # -------------------------
        # WORLD
        # -------------------------

        self.world = World()

        # -------------------------
        # PLAYER
        # -------------------------

        self.player = Player()

        # -------------------------
        # ENEMIES
        # -------------------------

        self.enemies = [
            Enemy(800, 360),
            Enemy(1040, 360),
            Enemy(600, 520),
            Enemy(960, 680),
        ]

        # -------------------------
        # DAMAGE NUMBERS
        # -------------------------

        self.damage_numbers = []

        # -------------------------
        # CAMERA
        # -------------------------

        self.camera = Camera(
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )

        # -------------------------
        # FONTS
        # -------------------------

        self.font = pygame.font.Font(
            None,
            24
        )

        self.game_over_font = pygame.font.Font(
            None,
            72
        )

        self.game_over_small_font = pygame.font.Font(
            None,
            32
        )

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

    def update(self):

        # =========================
        # GAME OVER
        # =========================

        if self.player.is_dead:

            if self.input.is_pressed(
                pygame.K_ESCAPE
            ):
                self.running = False

            if self.input.is_pressed(
                pygame.K_r
            ):
                self.restart()

            # Damage numbers can still finish
            for damage_number in self.damage_numbers:
                damage_number.update(self.dt)

            self.damage_numbers = [
                damage_number
                for damage_number in self.damage_numbers
                if not damage_number.is_finished()
            ]

            return

        # =========================
        # ESCAPE
        # =========================

        if self.input.is_pressed(
            pygame.K_ESCAPE
        ):
            self.running = False

        # =========================
        # PLAYER
        # =========================

        self.player.update(
            self.input,
            self.dt,
            self.world
        )

        # =========================
        # ENEMIES
        # =========================

        for enemy in self.enemies:

            enemy.update(
                self.player,
                self.dt,
                self.world
            )

        # =========================
        # PLAYER ATTACK
        # =========================

        if self.player.is_attacking:

            for enemy in self.enemies:

                if enemy.is_dead():
                    continue

                if self.player.attack_has_hit:
                    break

                if self.player.attack_rect.colliderect(
                    enemy.rect
                ):
                    damage = 25

                    enemy.take_damage(
                        damage
                    )

                    # Create floating damage number
                    self.damage_numbers.append(
                        DamageNumber(
                            enemy.rect.centerx,
                            enemy.rect.top,
                            damage
                        )
                    )

                    self.player.attack_has_hit = True

        # =========================
        # DAMAGE NUMBERS
        # =========================

        for damage_number in self.damage_numbers:

            damage_number.update(
                self.dt
            )

        self.damage_numbers = [
            damage_number
            for damage_number in self.damage_numbers
            if not damage_number.is_finished()
        ]

        # =========================
        # CAMERA
        # =========================

        self.camera.update(
            self.player.rect,
            self.world.get_width(),
            self.world.get_height()
        )

    def restart(self):

        # Reset player
        self.player = Player()

        # Reset enemies
        self.enemies = [
            Enemy(800, 360),
            Enemy(1040, 360),
            Enemy(600, 520),
            Enemy(960, 680),
        ]

        # Clear damage numbers
        self.damage_numbers = []

        # Reset camera
        self.camera.update(
            self.player.rect,
            self.world.get_width(),
            self.world.get_height()
        )

    def render(self):

        # =========================
        # BACKGROUND
        # =========================

        self.screen.fill(
            (20, 20, 25)
        )

        # =========================
        # WORLD
        # =========================

        self.world.render(
            self.screen,
            self.camera
        )

        # =========================
        # ENEMIES
        # =========================

        for enemy in self.enemies:

            if enemy.is_dead():
                continue

            enemy.render(
                self.screen,
                self.camera
            )

        # =========================
        # PLAYER
        # =========================

        self.player.render(
            self.screen,
            self.camera
        )

        # =========================
        # DAMAGE NUMBERS
        # =========================

        for damage_number in self.damage_numbers:

            damage_number.render(
                self.screen,
                self.camera
            )

        # =========================
        # DEBUG INFORMATION
        # =========================

        fps = self.clock.get_fps()

        state = (
            "MOVING"
            if self.player.is_moving
            else "IDLE"
        )

        attack_state = (
            "ATTACKING"
            if self.player.is_attacking
            else "READY"
        )

        alive_enemies = sum(
            not enemy.is_dead()
            for enemy in self.enemies
        )

        debug_text = self.font.render(
            f"FPS: {fps:.1f}  "
            f"DT: {self.dt:.4f}  "
            f"Direction: {self.player.direction}  "
            f"State: {state}  "
            f"Attack: {attack_state}  "
            f"HP: {self.player.health}  "
            f"Enemies: {alive_enemies}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            debug_text,
            (10, 10)
        )

        # =========================
        # GAME OVER SCREEN
        # =========================

        if self.player.is_dead:

            overlay = pygame.Surface(
                self.screen.get_size(),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 170)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            center_x = (
                self.screen.get_width()
                // 2
            )

            center_y = (
                self.screen.get_height()
                // 2
            )

            game_over_text = (
                self.game_over_font.render(
                    "GAME OVER",
                    True,
                    (255, 80, 80)
                )
            )

            restart_text = (
                self.game_over_small_font.render(
                    "Press R to restart",
                    True,
                    (255, 255, 255)
                )
            )

            quit_text = (
                self.game_over_small_font.render(
                    "Press ESC to quit",
                    True,
                    (255, 255, 255)
                )
            )

            self.screen.blit(
                game_over_text,
                (
                    center_x
                    - game_over_text.get_width()
                    // 2,
                    center_y - 70
                )
            )

            self.screen.blit(
                restart_text,
                (
                    center_x
                    - restart_text.get_width()
                    // 2,
                    center_y + 20
                )
            )

            self.screen.blit(
                quit_text,
                (
                    center_x
                    - quit_text.get_width()
                    // 2,
                    center_y + 60
                )
            )

        # =========================
        # DISPLAY
        # =========================

        pygame.display.flip()

    def run(self):

        while self.running:

            self.dt = (
                self.clock.tick(FPS)
                / 1000.0
            )

            self.handle_events()
            self.input.update()
            self.update()
            self.render()

        pygame.quit()
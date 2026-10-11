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

from entities.item import (
    HEALTH_POTION,
    IRON_SWORD,
    SHIELD,
)

from entities.loot import Loot

from world.world import World

from ui.hud import HUD
from ui.inventory_ui import InventoryUI


class Game:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.RESIZABLE
        )

        pygame.display.set_caption(
            WINDOW_TITLE
        )

        self.clock = pygame.time.Clock()

        self.running = True
        self.paused = False
        self.dt = 0.0

        self.input = InputManager()

        # ==================================================
        # WORLD
        # ==================================================

        self.world = World()

        # ==================================================
        # PLAYER
        # ==================================================

        self.player = Player()

        # ==================================================
        # STARTING INVENTORY
        # ==================================================

        self.player.inventory.add_item(
            HEALTH_POTION,
            3
        )

        self.player.inventory.add_item(
            IRON_SWORD,
            1
        )

        self.player.inventory.add_item(
            SHIELD,
            1
        )

        # ==================================================
        # ENEMIES
        # ==================================================

        self.enemies = [
            Enemy(800, 360, "Goblin"),
            Enemy(1040, 360, "Skeleton"),
            Enemy(600, 520, "Orc"),
            Enemy(960, 680, "Goblin"),
        ]

        # ==================================================
        # DAMAGE NUMBERS
        # ==================================================

        self.damage_numbers = []

        # ==================================================
        # LOOT
        # ==================================================

        self.loot = []

        # ==================================================
        # CAMERA
        # ==================================================

        self.camera = Camera(
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )

        # ==================================================
        # HUD
        # ==================================================

        self.hud = HUD()

        # ==================================================
        # INVENTORY UI
        # ==================================================

        self.inventory_ui = InventoryUI()

        # ==================================================
        # FONTS
        # ==================================================

        self.font = pygame.font.Font(
            None,
            24
        )

        self.pause_font = pygame.font.Font(
            None,
            72
        )

        self.pause_small_font = pygame.font.Font(
            None,
            30
        )

        self.game_over_font = pygame.font.Font(
            None,
            72
        )

        self.game_over_small_font = pygame.font.Font(
            None,
            32
        )

    # ======================================================
    # EVENTS
    # ======================================================

    def handle_events(self):

        for event in pygame.event.get():

            # ==================================================
            # QUIT
            # ==================================================

            if event.type == pygame.QUIT:

                self.running = False

                continue

            # ==================================================
            # KEYBOARD
            # ==================================================

            if event.type == pygame.KEYDOWN:

                # ==================================================
                # GAME OVER
                # ==================================================

                if self.player.is_dead:

                    if event.key == pygame.K_r:

                        self.restart()

                    elif event.key == pygame.K_ESCAPE:

                        self.running = False

                    continue

                # ==================================================
                # INVENTORY
                # ==================================================

                if self.inventory_ui.visible:

                    # ------------------------------------------
                    # ESC CLOSES INVENTORY ONLY
                    # ------------------------------------------

                    if event.key == pygame.K_ESCAPE:

                        self.inventory_ui.close()

                        continue

                    # ------------------------------------------
                    # INVENTORY KEYBOARD CONTROLS
                    # ------------------------------------------

                    self.inventory_ui.handle_key(
                        event.key,
                        self.player.inventory,
                        self.player
                    )

                    continue

                # ==================================================
                # INVENTORY TOGGLE
                # ==================================================

                if event.key == pygame.K_i:

                    if not self.paused:

                        self.inventory_ui.toggle()

                    continue

                # ==================================================
                # PAUSE / RESUME
                # ==================================================

                if event.key == pygame.K_ESCAPE:

                    self.paused = not self.paused

                    continue

                # ==================================================
                # QUIT FROM PAUSE
                # ==================================================

                if event.key == pygame.K_q:

                    if self.paused:

                        self.running = False

    # ======================================================
    # UPDATE
    # ======================================================

    def update(self):

        # ==================================================
        # GAME OVER
        # ==================================================

        if self.player.is_dead:

            return

        # ==================================================
        # INVENTORY
        # ==================================================

        if self.inventory_ui.visible:

            return

        # ==================================================
        # PAUSED
        # ==================================================

        if self.paused:

            return

        # ==================================================
        # PLAYER
        # ==================================================

        self.player.update(
            self.input,
            self.dt,
            self.world
        )

        # ==================================================
        # ENEMIES
        # ==================================================

        for enemy in self.enemies:

            enemy.update(
                self.player,
                self.dt,
                self.world
            )

        # ==================================================
        # PLAYER ATTACK
        # ==================================================

        if self.player.is_attacking:

            for enemy in self.enemies:

                if enemy.is_dead():

                    continue

                if self.player.attack_has_hit:

                    break

                if self.player.attack_rect.colliderect(
                    enemy.rect
                ):

                    # ==================================================
                    # DAMAGE
                    # ==================================================

                    damage = (
                        self.player.attack_damage
                    )

                    enemy.take_damage(
                        damage
                    )

                    # ==================================================
                    # ENEMY DEATH
                    # ==================================================

                    if enemy.is_dead():

                        # ------------------------------------------
                        # XP REWARD
                        # ------------------------------------------

                        self.player.add_xp(
                            enemy.xp_reward
                        )

                        # ------------------------------------------
                        # LOOT DROP
                        # ------------------------------------------

                        self.loot.append(
                            Loot(
                                enemy.rect.centerx - 12,
                                enemy.rect.centery - 12,
                                HEALTH_POTION
                            )
                        )

                    # ==================================================
                    # DAMAGE NUMBER
                    # ==================================================

                    self.damage_numbers.append(
                        DamageNumber(
                            enemy.rect.centerx,
                            enemy.rect.top,
                            damage
                        )
                    )

                    self.player.attack_has_hit = True

        # ==================================================
        # LOOT
        # ==================================================

        for loot in self.loot:

            loot.update(
                self.player,
                self.player.inventory
            )

        # ==================================================
        # REMOVE COLLECTED LOOT
        # ==================================================

        self.loot = [
            loot
            for loot in self.loot
            if not loot.is_collected
        ]

        # ==================================================
        # DAMAGE NUMBERS
        # ==================================================

        for damage_number in self.damage_numbers:

            damage_number.update(
                self.dt
            )

        self.damage_numbers = [
            damage_number
            for damage_number in self.damage_numbers
            if not damage_number.is_finished()
        ]

        # ==================================================
        # CAMERA
        # ==================================================

        self.camera.update(
            self.player.rect,
            self.world.get_width(),
            self.world.get_height()
        )

    # ======================================================
    # RESTART
    # ======================================================

    def restart(self):

        # ==================================================
        # NEW PLAYER
        # ==================================================

        self.player = Player()

        # ==================================================
        # RESTORE STARTING INVENTORY
        # ==================================================

        self.player.inventory.add_item(
            HEALTH_POTION,
            3
        )

        self.player.inventory.add_item(
            IRON_SWORD,
            1
        )

        self.player.inventory.add_item(
            SHIELD,
            1
        )

        # ==================================================
        # RESET ENEMIES
        # ==================================================

        self.enemies = [
            Enemy(800, 360, "Goblin"),
            Enemy(1040, 360, "Skeleton"),
            Enemy(600, 520, "Orc"),
            Enemy(960, 680, "Goblin"),
        ]

        # ==================================================
        # RESET DAMAGE NUMBERS
        # ==================================================

        self.damage_numbers = []

        # ==================================================
        # RESET LOOT
        # ==================================================

        self.loot = []

        # ==================================================
        # RESET PAUSE
        # ==================================================

        self.paused = False

        # ==================================================
        # CLOSE INVENTORY
        # ==================================================

        self.inventory_ui.close()

        # ==================================================
        # RESET CAMERA
        # ==================================================

        self.camera.update(
            self.player.rect,
            self.world.get_width(),
            self.world.get_height()
        )

    # ======================================================
    # PAUSE MENU
    # ======================================================

    def render_pause_menu(self):

        # ==================================================
        # DARK OVERLAY
        # ==================================================

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

        # ==================================================
        # CENTER
        # ==================================================

        center_x = (
            self.screen.get_width()
            // 2
        )

        center_y = (
            self.screen.get_height()
            // 2
        )

        # ==================================================
        # PAUSED
        # ==================================================

        paused_text = self.pause_font.render(
            "PAUSED",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            paused_text,
            (
                center_x
                - paused_text.get_width()
                // 2,
                center_y - 100
            )
        )

        # ==================================================
        # RESUME
        # ==================================================

        resume_text = self.pause_small_font.render(
            "ESC  -  RESUME",
            True,
            (120, 220, 120)
        )

        self.screen.blit(
            resume_text,
            (
                center_x
                - resume_text.get_width()
                // 2,
                center_y
            )
        )

        # ==================================================
        # QUIT
        # ==================================================

        quit_text = self.pause_small_font.render(
            "Q  -  QUIT",
            True,
            (220, 100, 100)
        )

        self.screen.blit(
            quit_text,
            (
                center_x
                - quit_text.get_width()
                // 2,
                center_y + 45
            )
        )

    # ======================================================
    # GAME OVER MENU
    # ======================================================

    def render_game_over(self):

        # ==================================================
        # DARK OVERLAY
        # ==================================================

        overlay = pygame.Surface(
            self.screen.get_size(),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 180)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        # ==================================================
        # CENTER
        # ==================================================

        center_x = (
            self.screen.get_width()
            // 2
        )

        center_y = (
            self.screen.get_height()
            // 2
        )

        # ==================================================
        # GAME OVER
        # ==================================================

        game_over_text = (
            self.game_over_font.render(
                "GAME OVER",
                True,
                (255, 80, 80)
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

        # ==================================================
        # RESTART
        # ==================================================

        restart_text = (
            self.game_over_small_font.render(
                "R  -  RESTART",
                True,
                (255, 255, 255)
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

        # ==================================================
        # QUIT
        # ==================================================

        quit_text = (
            self.game_over_small_font.render(
                "ESC  -  QUIT",
                True,
                (255, 255, 255)
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

    # ======================================================
    # RENDER
    # ======================================================

    def render(self):

        # ==================================================
        # BACKGROUND
        # ==================================================

        self.screen.fill(
            (20, 20, 25)
        )

        # ==================================================
        # WORLD
        # ==================================================

        self.world.render(
            self.screen,
            self.camera
        )

        # ==================================================
        # ENEMIES
        # ==================================================

        for enemy in self.enemies:

            if enemy.is_dead():

                continue

            enemy.render(
                self.screen,
                self.camera
            )

        # ==================================================
        # LOOT
        # ==================================================

        for loot in self.loot:

            loot.render(
                self.screen,
                self.camera
            )

        # ==================================================
        # PLAYER
        # ==================================================

        self.player.render(
            self.screen,
            self.camera
        )

        # ==================================================
        # DAMAGE NUMBERS
        # ==================================================

        for damage_number in self.damage_numbers:

            damage_number.render(
                self.screen,
                self.camera
            )

        # ==================================================
        # HUD
        # ==================================================

        self.hud.render(
            self.screen,
            self.player,
            self.enemies
        )

        # ==================================================
        # INVENTORY UI
        # ==================================================

        self.inventory_ui.render(
            self.screen,
            self.player.inventory,
            self.player
        )

        # ==================================================
        # PAUSE MENU
        # ==================================================

        if self.paused:

            self.render_pause_menu()

        # ==================================================
        # GAME OVER
        # ==================================================

        if self.player.is_dead:

            self.render_game_over()

        # ==================================================
        # DISPLAY
        # ==================================================

        pygame.display.flip()

    # ======================================================
    # MAIN LOOP
    # ======================================================

    def run(self):

        while self.running:

            # ==================================================
            # DELTA TIME
            # ==================================================

            self.dt = (
                self.clock.tick(FPS)
                / 1000.0
            )

            # ==================================================
            # EVENTS
            # ==================================================

            self.handle_events()

            # ==================================================
            # INPUT
            # ==================================================

            self.input.update()

            # ==================================================
            # UPDATE
            # ==================================================

            self.update()

            # ==================================================
            # RENDER
            # ==================================================

            self.render()

        # ==================================================
        # QUIT
        # ==================================================

        pygame.quit()
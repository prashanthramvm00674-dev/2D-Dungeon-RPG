import ctypes
import sys

import pygame

from core.mouse import normalize_mouse_position
from core.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WINDOW_TITLE,
    FPS,
)

from core.input import InputManager
from core.camera import Camera
from core.wave_manager import WaveManager
from core.quest_manager import QuestManager
from core.damage_number import DamageNumber
from graphics.lighting import LightingSystem
from graphics.post_processing import ScenePostProcessor

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
from ui.quest_ui import QuestJournalUI


def _enable_windows_dpi_awareness():
    """Keep Pygame drawing and mouse input aligned on scaled Windows displays."""
    if sys.platform != "win32":
        return

    try:
        user32 = ctypes.windll.user32
        # PER_MONITOR_AWARE_V2 prevents Windows from bitmap-scaling the window.
        try:
            if user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4)):
                return
        except (AttributeError, OSError):
            pass

        try:
            if ctypes.windll.shcore.SetProcessDpiAwareness(2) == 0:
                return
        except (AttributeError, OSError):
            pass

        try:
            user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass
    except Exception:
        # DPI APIs differ on older Windows releases; normal startup should
        # still work even when no awareness API is available.
        return


_enable_windows_dpi_awareness()


class Game:

    def __init__(self):

        pygame.init()

        # Start in a normal resizable window so desktop tools such as
        # Windows Snipping Tool can capture the game reliably. F11 still
        # switches between this window and fullscreen during play.
        display_info = pygame.display.Info()
        self.desktop_size = (
            display_info.current_w or SCREEN_WIDTH,
            display_info.current_h or SCREEN_HEIGHT
        )

        desktop_width, desktop_height = self.desktop_size
        aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
        available_width = max(640, desktop_width - 40)
        available_height = max(480, desktop_height - 100)

        window_width = min(
            SCREEN_WIDTH,
            available_width,
            int(available_height * aspect_ratio)
        )
        window_height = min(
            SCREEN_HEIGHT,
            available_height,
            int(window_width / aspect_ratio)
        )
        self.windowed_size = (window_width, window_height)
        self.fullscreen = False

        self.screen = pygame.display.set_mode(
            self.windowed_size,
            pygame.RESIZABLE
        )

        pygame.display.set_caption(
            WINDOW_TITLE
        )

        self.clock = pygame.time.Clock()

        self.running = True
        self.paused = False
        self.pause_menu_buttons = {}
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

        # Spawn the player on the safe floor tile nearest the map center.
        spawn_x, spawn_y = self.world.get_center_spawn_position()
        self.player.x = spawn_x
        self.player.y = spawn_y
        self.player.rect.x = spawn_x
        self.player.rect.y = spawn_y

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

        # The opening roster preserves the existing encounter while the
        # WaveManager owns all subsequent progression and spawn queues.
        self.wave_manager = WaveManager()
        self.enemies = []
        enemy_types = self.wave_manager.initial_roster
        enemy_positions = self.world.get_edge_spawn_positions(
            len(enemy_types),
            avoid_positions=[(spawn_x, spawn_y)]
        )

        for enemy_type, (enemy_x, enemy_y) in zip(
            enemy_types,
            enemy_positions
        ):
            self.enemies.append(
                Enemy(enemy_x, enemy_y, enemy_type)
            )

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
            *self.screen.get_size()
        )

        # ==================================================
        # LIGHTING
        # ==================================================

        self.lighting = LightingSystem()

        # ==================================================
        # SCENE POST-PROCESSING
        # ==================================================

        # The finishing pass improves shadow detail and visual focus while
        # leaving the pixel-art geometry and HUD artwork untouched.
        self.post_processing = ScenePostProcessor()

        # ==================================================
        # HUD
        # ==================================================

        self.hud = HUD()

        # ==================================================
        # INVENTORY UI
        # ==================================================

        self.inventory_ui = InventoryUI()
        self.quest_manager = QuestManager()
        self.quest_ui = QuestJournalUI()

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
            # WINDOW RESIZE
            # ==================================================

            if event.type == pygame.VIDEORESIZE:
                # Fullscreen size changes are managed by SDL itself; only
                # recreate the surface for a real user-resized window.
                if self.fullscreen:
                    continue

                new_width = max(640, int(event.w))
                new_height = max(480, int(event.h))

                self.screen = pygame.display.set_mode(
                    (new_width, new_height),
                    pygame.RESIZABLE
                )
                self.windowed_size = self.screen.get_size()

                self.camera.update(
                    self.player.rect,
                    self.world.get_width(),
                    self.world.get_height(),
                    *self.screen.get_size()
                )
                continue

            # ==================================================
            # MOUSE INPUT: MENU, INVENTORY, AND QUICK SLOTS
            # ==================================================

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.wave_manager.is_victory:
                        continue

                    mouse_position = normalize_mouse_position(
                        event.pos,
                        self.screen.get_size()
                    )

                    if self.paused:
                        # Click targets are drawn in surface pixels, so use
                        # the same coordinate space as their hitboxes.
                        buttons = self.pause_menu_buttons
                        if buttons.get("resume", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                            self.paused = False
                        elif buttons.get("restart", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                            self.restart()
                        elif buttons.get("quit", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                            self.running = False
                        elif buttons.get("fullscreen", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                            self.toggle_fullscreen()
                        continue

                    if not self.player.is_dead:
                        # The top-right button remains a pause/menu control.
                        if self.hud.menu_button_contains(mouse_position):
                            self.inventory_ui.close()
                            self.quest_ui.close()
                            self.paused = True
                            continue

                        if self.quest_ui.visible:
                            # The journal is modal; ignore world/hotbar clicks.
                            continue

                        if self.inventory_ui.visible:
                            # InventoryUI normalizes the raw event coordinates
                            # itself so direct UI callers share the same path.
                            self.inventory_ui.handle_click(
                                event.pos,
                                self.player.inventory,
                                self.player,
                                self.screen.get_size(),
                                click_count=getattr(event, "clicks", 1)
                            )
                            continue

                        quick_slot = self.hud.hotbar_slot_at(mouse_position)
                        if quick_slot is not None:
                            self.activate_hotbar_slot(quick_slot)

                continue

            # ==================================================
            # KEYBOARD
            # ==================================================

            if event.type == pygame.KEYDOWN:

                # ==================================================
                # FULLSCREEN TOGGLE
                # ==================================================

                if (
                    event.key == pygame.K_F11
                    or (
                        event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                        and event.mod & pygame.KMOD_ALT
                    )
                ):
                    # F11 and Alt+Enter share the same tested toggle path.
                    self.toggle_fullscreen()
                    continue

                # ==================================================
                # WAVE VICTORY
                # ==================================================

                if self.wave_manager.is_victory:
                    if event.key == pygame.K_r:
                        self.restart()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                    continue

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
                # QUEST JOURNAL
                # ==================================================

                if self.quest_ui.visible:
                    if event.key in (pygame.K_j, pygame.K_ESCAPE):
                        self.quest_ui.close()
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
                # PAUSED MENU SHORTCUTS
                # ==================================================

                if self.paused:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        self.paused = False
                    elif event.key == pygame.K_r:
                        self.restart()
                    elif event.key == pygame.K_q:
                        self.running = False
                    continue

                # ==================================================
                # QUEST JOURNAL TOGGLE
                # ==================================================

                if event.key == pygame.K_j:
                    self.inventory_ui.close()
                    self.quest_ui.toggle()
                    continue

                # ==================================================
                # INVENTORY TOGGLE
                # ==================================================

                if event.key == pygame.K_i:
                    self.inventory_ui.toggle()
                    continue

                # ==================================================
                # OPEN MENU
                # ==================================================

                if event.key == pygame.K_ESCAPE:
                    self.inventory_ui.close()
                    self.paused = True
                    continue

                # ==================================================
                # QUICK-SLOT HOTKEYS
                # ==================================================

                hotkey_slots = {
                    pygame.K_1: 0,
                    pygame.K_2: 1,
                    pygame.K_3: 2,
                    pygame.K_4: 3,
                    pygame.K_5: 4,
                }
                if event.key in hotkey_slots:
                    self.activate_hotbar_slot(hotkey_slots[event.key])

    def toggle_fullscreen(self):
        """Toggle immersive fullscreen and return to the last window size."""
        if self.fullscreen:
            self.screen = pygame.display.set_mode(
                self.windowed_size,
                pygame.RESIZABLE
            )
            self.fullscreen = False
        else:
            # Preserve the user's latest window size for the return trip.
            self.windowed_size = self.screen.get_size()
            self.screen = pygame.display.set_mode(
                self.desktop_size,
                pygame.FULLSCREEN
            )
            self.fullscreen = True

        pygame.display.set_caption(WINDOW_TITLE)
        self.camera.update(
            self.player.rect,
            self.world.get_width(),
            self.world.get_height(),
            *self.screen.get_size()
        )

    def activate_hotbar_slot(self, index):
        """Use a consumable or equip gear from one of the five quick slots."""
        if index < 0 or index >= min(5, self.player.inventory.max_slots):
            return False

        slot = self.player.inventory.slots[index]
        if slot is None:
            return False

        item = slot["item"]
        if item.item_type == "consumable":
            return self.inventory_ui.use_item(
                item,
                self.player,
                self.player.inventory
            )

        if item.item_type in ("weapon", "armor"):
            was_equipped = self.inventory_ui.is_equipped(item, self.player)
            self.inventory_ui.equip_or_unequip(item, self.player)
            return not was_equipped

        return False

    # ======================================================
    # UPDATE
    # ======================================================

    def update(self):

        # ==================================================
        # GAME OVER
        # ==================================================

        if self.player.is_dead or self.wave_manager.is_victory:

            return

        # ==================================================
        # INVENTORY
        # ==================================================

        if self.inventory_ui.visible or self.quest_ui.visible:

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
        # WAVES
        # ==================================================

        alive_count = sum(not enemy.is_dead() for enemy in self.enemies)
        self.wave_manager.update(
            self.dt,
            alive_count,
            self._spawn_wave_enemy,
        )
        self.quest_manager.update(
            self.wave_manager,
            sum(not enemy.is_dead() for enemy in self.enemies),
            self.player,
        )

        # ==================================================
        # CAMERA
        # ==================================================

        self.camera.update(
            self.player.rect,
            self.world.get_width(),
            self.world.get_height(),
            *self.screen.get_size()
        )

    def _spawn_wave_enemy(self, enemy_type, spawn_index):
        """Spawn one reinforcement on safe floor away from current actors."""
        avoid_positions = [(self.player.rect.x, self.player.rect.y)]
        avoid_positions.extend(
            (enemy.rect.x, enemy.rect.y)
            for enemy in self.enemies
            if not enemy.is_dead()
        )
        positions = self.world.get_edge_spawn_positions(
            1,
            avoid_positions=avoid_positions,
            start_index=spawn_index,
        )
        if not positions:
            return False

        enemy_x, enemy_y = positions[0]
        self.enemies.append(Enemy(enemy_x, enemy_y, enemy_type))
        return True

    # ======================================================
    # RESTART
    # ======================================================

    def restart(self):

        # ==================================================
        # NEW PLAYER
        # ==================================================

        self.player = Player()

        # Respawn the player on the safe floor tile nearest the map center.
        spawn_x, spawn_y = self.world.get_center_spawn_position()
        self.player.x = spawn_x
        self.player.y = spawn_y
        self.player.rect.x = spawn_x
        self.player.rect.y = spawn_y

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

        # Reset wave and quest progress alongside the player and inventory.
        self.wave_manager = WaveManager()
        self.quest_manager = QuestManager()
        self.quest_ui.close()
        self.enemies = []
        enemy_types = self.wave_manager.initial_roster
        enemy_positions = self.world.get_edge_spawn_positions(
            len(enemy_types),
            avoid_positions=[(spawn_x, spawn_y)]
        )

        for enemy_type, (enemy_x, enemy_y) in zip(
            enemy_types,
            enemy_positions
        ):
            self.enemies.append(
                Enemy(enemy_x, enemy_y, enemy_type)
            )

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
        self.pause_menu_buttons = {}

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
            self.world.get_height(),
            *self.screen.get_size()
        )

    # ======================================================
    # PAUSE MENU
    # ======================================================

    def render_pause_menu(self):
        """Draw an interactive gold-framed pause menu above the dungeon."""
        screen_width, screen_height = self.screen.get_size()
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((2, 5, 9, 190))
        self.screen.blit(overlay, (0, 0))

        panel_width = min(480, screen_width - 36)
        panel_height = min(390, screen_height - 36)
        panel = pygame.Rect(
            (screen_width - panel_width) // 2,
            (screen_height - panel_height) // 2,
            panel_width,
            panel_height
        )

        pygame.draw.rect(self.screen, (2, 4, 7), panel.move(5, 6))
        pygame.draw.rect(self.screen, (10, 17, 24), panel)
        pygame.draw.rect(self.screen, (121, 75, 41), panel, 4)
        pygame.draw.rect(self.screen, (235, 171, 81), panel.inflate(-9, -9), 1)

        title = self.pause_small_font.render(
            "DUNGEON PAUSED", True, (246, 190, 94)
        )
        self.screen.blit(
            title,
            (panel.centerx - title.get_width() // 2, panel.top + 32)
        )

        subtitle_font = pygame.font.Font(None, 22)
        subtitle = subtitle_font.render(
            "The darkness can wait.", True, (171, 183, 190)
        )
        self.screen.blit(
            subtitle,
            (panel.centerx - subtitle.get_width() // 2, panel.top + 72)
        )

        button_width = min(310, panel.width - 46)
        button_height = 47
        button_gap = 8
        first_y = panel.top + 115
        fullscreen_label = (
            "EXIT FULLSCREEN" if self.fullscreen else "ENTER FULLSCREEN"
        )
        button_specs = (
            ("resume", "RESUME", (35, 73, 53), (119, 198, 133)),
            ("restart", "RESTART RUN", (78, 53, 29), (241, 185, 91)),
            ("fullscreen", fullscreen_label, (38, 59, 74), (150, 185, 198)),
            ("quit", "QUIT GAME", (69, 35, 36), (208, 113, 102)),
        )
        mouse_pos = pygame.mouse.get_pos()
        self.pause_menu_buttons = {}

        for index, (key, label, fill, border) in enumerate(button_specs):
            button = pygame.Rect(
                panel.centerx - button_width // 2,
                first_y + index * (button_height + button_gap),
                button_width,
                button_height
            )
            self.pause_menu_buttons[key] = button
            hover = button.collidepoint(mouse_pos)
            actual_fill = tuple(min(255, channel + 16) for channel in fill) if hover else fill

            pygame.draw.rect(self.screen, (3, 6, 9), button.move(2, 3))
            pygame.draw.rect(self.screen, actual_fill, button)
            pygame.draw.rect(self.screen, border, button, 2)
            pygame.draw.rect(self.screen, (94, 78, 60), button.inflate(-6, -6), 1)

            label_surface = self.pause_small_font.render(
                label, True, (244, 238, 223)
            )
            self.screen.blit(
                label_surface,
                (
                    button.centerx - label_surface.get_width() // 2,
                    button.centery - label_surface.get_height() // 2
                )
            )

        hint = pygame.font.Font(None, 19).render(
            "ESC  RESUME     R  RESTART     Q  QUIT",
            True,
            (154, 163, 168)
        )
        self.screen.blit(
            hint,
            (panel.centerx - hint.get_width() // 2, panel.bottom - 28)
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

    def render_wave_status(self):
        """Draw a short center-screen announcement without changing the HUD."""
        if self.wave_manager.is_victory or self.player.is_dead:
            return

        message = self.wave_manager.announcement
        if self.wave_manager.announcement_timer <= 0.0:
            if self.wave_manager.is_intermission:
                seconds = max(1, int(self.wave_manager.intermission_remaining + 0.999))
                message = f"NEXT WAVE IN {seconds}"
            else:
                return

        if not message:
            return

        width, height = self.screen.get_size()
        panel_width = min(560, width - 32)
        panel_height = 62
        panel = pygame.Rect(
            (width - panel_width) // 2,
            max(105, int(height * 0.27)),
            panel_width,
            panel_height,
        )
        overlay = pygame.Surface(panel.size, pygame.SRCALPHA)
        overlay.fill((5, 10, 16, 218))
        self.screen.blit(overlay, panel.topleft)
        pygame.draw.rect(self.screen, (104, 64, 35), panel, 2)
        pygame.draw.rect(self.screen, (208, 145, 65), panel.inflate(-6, -6), 1)

        label = self.pause_small_font.render(
            message, True, (255, 203, 112)
        )
        self.screen.blit(
            label,
            (panel.centerx - label.get_width() // 2,
             panel.centery - label.get_height() // 2),
        )

    def render_victory(self):
        """Show the completed four-wave run and familiar restart/exit keys."""
        width, height = self.screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((2, 4, 7, 205))
        self.screen.blit(overlay, (0, 0))

        title = self.game_over_font.render(
            "DUNGEON CLEARED", True, (255, 203, 112)
        )
        subtitle = self.game_over_small_font.render(
            f"ALL {self.wave_manager.total_waves} WAVES DEFEATED",
            True, (231, 225, 210)
        )
        restart_text = self.game_over_small_font.render(
            "R  -  RESTART", True, (255, 255, 255)
        )
        quit_text = self.game_over_small_font.render(
            "ESC  -  QUIT", True, (255, 255, 255)
        )

        center_x = width // 2
        center_y = height // 2
        self.screen.blit(
            title, (center_x - title.get_width() // 2, center_y - 105)
        )
        self.screen.blit(
            subtitle, (center_x - subtitle.get_width() // 2, center_y - 35)
        )
        self.screen.blit(
            restart_text, (center_x - restart_text.get_width() // 2, center_y + 30)
        )
        self.screen.blit(
            quit_text, (center_x - quit_text.get_width() // 2, center_y + 72)
        )

    # ======================================================
    # RENDER
    # ======================================================

    def render(self):

        # ==================================================
        # CAMERA SYNC
        # ==================================================

        # Recalculate from the live player rect and current viewport immediately
        # before drawing. This prevents stale camera offsets from being used by
        # world tiles, entities, loot, and damage numbers in this frame.
        self.camera.update(
            self.player.rect,
            self.world.get_width(),
            self.world.get_height(),
            *self.screen.get_size()
        )

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
        # LIGHTING
        # ==================================================

        # Shade only the world and actors. UI is rendered afterward so its
        # labels and panels remain readable in the dark dungeon.
        self.lighting.render(
            self.screen,
            self.world.torches,
            self.player,
            self.camera
        )

        # Re-draw flame silhouettes after the ambient pass so the fire remains
        # a crisp, bright focal point; keep enemy health bars similarly legible.
        self.world.render_torches(self.screen, self.camera)

        # Potions are drawn after ambient shading so the bottle silhouette
        # remains distinct enough to spot and collect in the dark dungeon.
        for loot in self.loot:
            loot.render(
                self.screen,
                self.camera
            )

        for enemy in self.enemies:
            if not enemy.is_dead():
                enemy.render_health_bar(self.screen, self.camera)

        # ==================================================
        # PHOTO-STYLE SCENE FINISHING
        # ==================================================

        # Process the world/actors only. The UI rendered below remains crisp,
        # readable, and visually identical to the approved HUD design.
        self.post_processing.apply(self.screen)

        # ==================================================
        # HUD
        # ==================================================

        self.hud.render(
            self.screen,
            self.player,
            self.enemies,
            self.player.inventory,
            self.wave_manager,
        )

        self.render_wave_status()

        # ==================================================
        # INVENTORY UI
        # ==================================================

        self.inventory_ui.render(
            self.screen,
            self.player.inventory,
            self.player
        )

        self.quest_ui.render(
            self.screen,
            self.quest_manager,
            self.wave_manager,
            sum(not enemy.is_dead() for enemy in self.enemies),
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

        if self.wave_manager.is_victory:
            self.render_victory()

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
import ctypes
import math
import sys
from datetime import datetime, timezone

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
from core.save_manager import SAVE_SCHEMA_VERSION, SaveManager, SettingsManager
from graphics.lighting import LightingSystem
from graphics.post_processing import ScenePostProcessor

from entities.player import Player
from entities.enemy import Enemy
from entities.dungeon_boss import DungeonBoss
from entities.npc import AshenWarden

from entities.item import (
    HEALTH_POTION,
    IRON_SWORD,
    SHIELD,
)

ITEMS_BY_NAME = {
    item.name: item
    for item in (HEALTH_POTION, IRON_SWORD, SHIELD)
}
VALID_ENEMY_TYPES = {"Goblin", "Skeleton", "Orc"}

from entities.loot import Loot

from world.world import World

from ui.hud import HUD
from ui.inventory_ui import InventoryUI
from ui.quest_ui import QuestJournalUI
from ui.dialogue_ui import DialogueUI


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

        # Preferences and save slots use a stable path independent of the
        # directory from which the game process was launched.
        self.settings_manager = SettingsManager()
        self.settings_manager.load()
        self.save_manager = SaveManager()
        self.persistence_status = ""
        self.settings_menu_visible = False
        self.settings_buttons = {}

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
        self.fullscreen = self.settings_manager.values["start_fullscreen"]

        if self.fullscreen:
            self.screen = pygame.display.set_mode(
                self.desktop_size,
                pygame.FULLSCREEN
            )
        else:
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

        # The Warden is placed on connected, clear floor near the safe spawn.
        self.npc = AshenWarden(*self._find_npc_position(spawn_x, spawn_y))

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
        # BOSS ENCOUNTER
        # ==================================================

        # Spawned only after the four survival waves have been cleared.
        self.boss = None

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
        self.dialogue_ui = DialogueUI()

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
                        # Settings is modal above the pause menu. Its toggles
                        # save immediately, so values survive a later restart.
                        if self.settings_menu_visible:
                            buttons = self.settings_buttons
                            if buttons.get("start_fullscreen", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                                self._toggle_setting("start_fullscreen")
                            elif buttons.get("lighting_enabled", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                                self._toggle_setting("lighting_enabled")
                            elif buttons.get("post_processing_enabled", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                                self._toggle_setting("post_processing_enabled")
                            elif buttons.get("autosave_on_quit", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                                self._toggle_setting("autosave_on_quit")
                            elif buttons.get("back", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                                self.settings_menu_visible = False
                            continue

                        buttons = self.pause_menu_buttons
                        if buttons.get("resume", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                            self.paused = False
                        elif buttons.get("restart", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                            self.restart()
                        elif buttons.get("quit", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                            self.running = False
                        elif buttons.get("fullscreen", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                            self.toggle_fullscreen()
                        elif buttons.get("save", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                            self.save_game()
                        elif buttons.get("load", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                            self.load_game()
                        elif buttons.get("settings", pygame.Rect(0, 0, 0, 0)).collidepoint(mouse_position):
                            self.settings_menu_visible = True
                        continue

                    if not self.player.is_dead:
                        # The top-right button remains a pause/menu control.
                        if self.hud.menu_button_contains(mouse_position):
                            self.inventory_ui.close()
                            self.quest_ui.close()
                            self.dialogue_ui.close()
                            self.paused = True
                            continue

                        if self.quest_ui.visible:
                            # The journal is modal; ignore world/hotbar clicks.
                            continue

                        if self.dialogue_ui.visible:
                            # Dialogue is modal; world and hotbar clicks are ignored.
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
                # QUICK SAVE / LOAD
                # ==================================================

                if event.key == pygame.K_F5:
                    self.save_game()
                    continue

                if event.key == pygame.K_F9:
                    self.load_game()
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
                # NPC DIALOGUE
                # ==================================================

                if self.dialogue_ui.visible:
                    if event.key == pygame.K_ESCAPE:
                        self.dialogue_ui.close()
                    elif event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        self.dialogue_ui.advance()
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
                    if self.settings_menu_visible:
                        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                            self.settings_menu_visible = False
                    elif event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
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
                # NPC INTERACTION
                # ==================================================

                if event.key == pygame.K_e:
                    if self.npc.is_in_range(self.player):
                        self.dialogue_ui.open(
                            self.npc.NAME,
                            self.npc.dialogue_for(
                                self.wave_manager, self.quest_manager
                            ),
                        )
                    continue

                # ==================================================
                # OPEN MENU
                # ==================================================

                if event.key == pygame.K_ESCAPE:
                    self.inventory_ui.close()
                    self.dialogue_ui.close()
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

    def _toggle_setting(self, key):
        """Toggle a supported option and persist it immediately."""
        try:
            success = self.settings_manager.toggle(key)
        except (KeyError, ValueError):
            success = False

        if success:
            setting_label = key.replace("_", " ").title()
            self.persistence_status = f"{setting_label} saved."
        else:
            self.persistence_status = (
                "Settings could not be saved: " + self.settings_manager.last_error
            )
        return success

    @staticmethod
    def _save_item_name(item):
        return None if item is None else item.name

    def _serialize_game_state(self):
        """Capture gameplay state only; graphics caches and transient UI stay local."""
        player = self.player
        wave = self.wave_manager
        boss = self.boss

        return {
            "player": {
                "x": int(player.rect.x),
                "y": int(player.rect.y),
                "health": int(player.health),
                "max_health": int(player.max_health),
                "base_max_health": int(player.base_max_health),
                "level": int(player.level),
                "xp": int(player.xp),
                "xp_to_next_level": int(player.xp_to_next_level),
                "base_attack_damage": int(player.base_attack_damage),
                "direction": player.direction,
                "damage_cooldown": float(player.damage_cooldown),
                "hit_flash_timer": float(player.hit_flash_timer),
                "is_attacking": bool(player.is_attacking),
                "attack_timer": float(player.attack_timer),
                "attack_cooldown_timer": float(player.attack_cooldown_timer),
                "attack_has_hit": bool(player.attack_has_hit),
                "inventory": [
                    None if slot is None else {
                        "item": slot["item"].name,
                        "quantity": int(slot["quantity"]),
                    }
                    for slot in player.inventory.slots
                ],
                "equipment": {
                    "weapon": self._save_item_name(player.equipped_weapon),
                    "shield": self._save_item_name(player.equipped_shield),
                    "armor": self._save_item_name(player.equipped_armor),
                },
            },
            "wave": {
                "current_wave": int(wave.current_wave),
                "phase": wave.phase,
                "pending_enemy_types": list(wave.pending_enemy_types),
                "spawn_timer": float(wave.spawn_timer),
                "intermission_remaining": float(wave.intermission_remaining),
                "announcement": wave.announcement,
                "announcement_timer": float(wave.announcement_timer),
                "spawned_this_wave": int(wave.spawned_this_wave),
                "total_spawned": int(wave.total_spawned),
            },
            "enemies": [
                {
                    "type": enemy.enemy_type,
                    "x": int(enemy.rect.x),
                    "y": int(enemy.rect.y),
                    "health": int(enemy.health),
                    "attack_timer": float(enemy.attack_timer),
                    "hit_flash_timer": float(enemy.hit_flash_timer),
                }
                for enemy in self.enemies
            ],
            "boss": None if boss is None else {
                "x": int(boss.rect.x),
                "y": int(boss.rect.y),
                "health": int(boss.health),
                "state": boss.state,
                "state_timer": float(boss.state_timer),
                "attack_cooldown": float(boss.attack_cooldown),
                "special_cooldown": float(boss.special_cooldown),
                "hit_flash_timer": float(boss.hit_flash_timer),
                "telegraph_position": (
                    list(boss.telegraph_position)
                    if boss.telegraph_position is not None else None
                ),
            },
            "loot": [
                {
                    "x": int(drop.rect.x),
                    "y": int(drop.rect.y),
                    "item": drop.item.name,
                }
                for drop in self.loot
                if not drop.is_collected
            ],
            "quest": {
                "completed": bool(self.quest_manager.completed),
                "reward_claimed": bool(self.quest_manager.reward_claimed),
            },
        }

    def save_game(self):
        """Write a complete run snapshot into the atomic manual/auto-save slot."""
        payload = {
            "schema_version": SAVE_SCHEMA_VERSION,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "game": self._serialize_game_state(),
        }
        if self.save_manager.save(payload):
            self.persistence_status = "Game saved successfully."
            return True

        self.persistence_status = "Save failed: " + self.save_manager.last_error
        return False

    def _restore_game_state(self, data):
        """Build and validate replacement objects before mutating the running game."""
        if not isinstance(data, dict):
            raise ValueError("Saved game data is not an object.")

        def number(source, key, minimum, maximum, integer=False, default=None):
            if not isinstance(source, dict):
                raise ValueError("A saved state section is invalid.")
            value = source.get(key, default)
            if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"Saved field '{key}' is missing or not numeric.")
            if not math.isfinite(float(value)) or value < minimum or value > maximum:
                raise ValueError(f"Saved field '{key}' is outside its allowed range.")
            if integer and int(value) != value:
                raise ValueError(f"Saved field '{key}' must be an integer.")
            return int(value) if integer else float(value)

        def flag(source, key, default=None):
            value = source.get(key, default) if isinstance(source, dict) else None
            if type(value) is not bool:
                raise ValueError(f"Saved field '{key}' must be true or false.")
            return value

        def resolve_item(name, expected_type=None):
            if name is None:
                return None
            if not isinstance(name, str) or name not in ITEMS_BY_NAME:
                raise ValueError(f"Unknown saved item: {name!r}")
            item = ITEMS_BY_NAME[name]
            if expected_type is not None and item.item_type != expected_type:
                raise ValueError(f"Saved item '{name}' is not a {expected_type}.")
            return item

        # PLAYER AND INVENTORY
        player_data = data.get("player")
        if not isinstance(player_data, dict):
            raise ValueError("Saved player data is missing.")
        new_player = Player()
        x = number(player_data, "x", 0, self.world.get_width() - new_player.width, True)
        y = number(player_data, "y", 0, self.world.get_height() - new_player.height, True)
        new_player.rect.topleft = (x, y)
        if self.world.collides_with_wall(new_player.rect):
            raise ValueError("The saved player position intersects a wall.")
        new_player.x, new_player.y = x, y

        new_player.max_health = number(player_data, "max_health", 1, 10000, True)
        new_player.base_max_health = number(
            player_data, "base_max_health", 1, new_player.max_health, True
        )
        new_player.health = number(
            player_data, "health", 0, new_player.max_health, True
        )
        new_player.level = number(player_data, "level", 1, 999, True)
        new_player.xp = number(player_data, "xp", 0, 10000000, True)
        new_player.xp_to_next_level = number(
            player_data, "xp_to_next_level", 1, 10000000, True
        )
        new_player.base_attack_damage = number(
            player_data, "base_attack_damage", 1, 100000, True
        )
        direction = player_data.get("direction", "down")
        if direction not in ("up", "down", "left", "right"):
            raise ValueError("The saved player direction is invalid.")
        new_player.direction = direction
        new_player.damage_cooldown = number(
            player_data, "damage_cooldown", 0, 5, default=0.0
        )
        new_player.hit_flash_timer = number(
            player_data, "hit_flash_timer", 0, 1, default=0.0
        )
        new_player.is_attacking = flag(player_data, "is_attacking", False)
        new_player.attack_timer = number(
            player_data, "attack_timer", 0, 5, default=0.0
        )
        new_player.attack_cooldown_timer = number(
            player_data, "attack_cooldown_timer", 0, 5, default=0.0
        )
        new_player.attack_has_hit = flag(player_data, "attack_has_hit", False)
        new_player.is_dead = new_player.health <= 0

        raw_slots = player_data.get("inventory")
        if not isinstance(raw_slots, list) or len(raw_slots) != new_player.inventory.max_slots:
            raise ValueError("Saved inventory slot count does not match this game version.")
        restored_slots = []
        for slot_data in raw_slots:
            if slot_data is None:
                restored_slots.append(None)
                continue
            if not isinstance(slot_data, dict):
                raise ValueError("A saved inventory slot is invalid.")
            item = resolve_item(slot_data.get("item"))
            quantity = number(slot_data, "quantity", 1, 999, True)
            if not item.stackable and quantity != 1:
                raise ValueError("A non-stackable saved item has an invalid quantity.")
            restored_slots.append({"item": item, "quantity": quantity})
        new_player.inventory.slots = restored_slots

        equipment = player_data.get("equipment")
        if not isinstance(equipment, dict):
            raise ValueError("Saved equipment data is missing.")
        new_player.equipped_weapon = resolve_item(equipment.get("weapon"), "weapon")
        new_player.equipped_shield = resolve_item(equipment.get("shield"), "armor")
        new_player.equipped_armor = resolve_item(equipment.get("armor"), "armor")
        new_player.recalculate_attack_damage()
        new_player.update_attack_rect()

        # WAVE STATE
        wave_data = data.get("wave")
        if not isinstance(wave_data, dict):
            raise ValueError("Saved wave data is missing.")
        new_wave = WaveManager()
        current_wave = number(
            wave_data, "current_wave", 1, new_wave.total_waves, True
        )
        phase = wave_data.get("phase")
        if phase not in (new_wave.ACTIVE, new_wave.INTERMISSION, new_wave.BOSS, new_wave.VICTORY):
            raise ValueError("The saved wave phase is invalid.")
        if phase in (new_wave.BOSS, new_wave.VICTORY) and current_wave != new_wave.total_waves:
            raise ValueError("The saved boss/finale phase has an invalid wave number.")
        pending = wave_data.get("pending_enemy_types")
        if (
            not isinstance(pending, list)
            or len(pending) > 100
            or any(kind not in VALID_ENEMY_TYPES for kind in pending)
        ):
            raise ValueError("The saved enemy queue is invalid.")
        new_wave.current_wave = current_wave
        new_wave.phase = phase
        new_wave.pending_enemy_types = list(pending)
        new_wave.spawn_timer = number(wave_data, "spawn_timer", 0, 60, default=0.0)
        new_wave.intermission_remaining = number(
            wave_data, "intermission_remaining", 0, new_wave.intermission_duration, default=0.0
        )
        announcement = wave_data.get("announcement", "")
        if not isinstance(announcement, str) or len(announcement) > 80:
            raise ValueError("The saved wave announcement is invalid.")
        new_wave.announcement = announcement
        new_wave.announcement_timer = number(
            wave_data, "announcement_timer", 0, 60, default=0.0
        )
        new_wave.spawned_this_wave = number(
            wave_data, "spawned_this_wave", 0, 5000, True, default=0
        )
        new_wave.total_spawned = number(
            wave_data, "total_spawned", 0, 10000, True, default=0
        )

        # REGULAR ENEMIES
        enemy_data = data.get("enemies")
        if not isinstance(enemy_data, list) or len(enemy_data) > 500:
            raise ValueError("Saved enemy data is invalid.")
        new_enemies = []
        for saved_enemy in enemy_data:
            if not isinstance(saved_enemy, dict):
                raise ValueError("A saved enemy is invalid.")
            enemy_type = saved_enemy.get("type")
            if enemy_type not in VALID_ENEMY_TYPES:
                raise ValueError(f"Unknown saved enemy type: {enemy_type!r}")
            enemy = Enemy(
                number(saved_enemy, "x", 0, self.world.get_width() - 40, True),
                number(saved_enemy, "y", 0, self.world.get_height() - 40, True),
                enemy_type,
            )
            enemy.health = number(saved_enemy, "health", 0, enemy.max_health, True)
            enemy.attack_timer = number(
                saved_enemy, "attack_timer", 0, 100, default=0.0
            )
            enemy.hit_flash_timer = number(
                saved_enemy, "hit_flash_timer", 0, 1, default=0.0
            )
            if not enemy.is_dead() and self.world.collides_with_wall(enemy.rect):
                raise ValueError("A saved enemy position intersects a wall.")
            new_enemies.append(enemy)

        # BOSS STATE, INCLUDING ANY ATTACK TELEGRAPH CURRENTLY IN PROGRESS
        boss_data = data.get("boss")
        new_boss = None
        if boss_data is not None:
            if not isinstance(boss_data, dict):
                raise ValueError("Saved boss data is invalid.")
            boss_x = number(boss_data, "x", 0, self.world.get_width() - 48, True)
            boss_y = number(boss_data, "y", 0, self.world.get_height() - 48, True)
            new_boss = DungeonBoss(boss_x, boss_y)
            new_boss.health = number(
                boss_data, "health", 0, new_boss.max_health, True
            )
            state = boss_data.get("state")
            if state not in ("approach", "slam_windup", "pulse_windup", "recover"):
                raise ValueError("The saved boss state is invalid.")
            new_boss.state = state
            new_boss.state_timer = number(boss_data, "state_timer", 0, 60, default=0.0)
            new_boss.attack_cooldown = number(
                boss_data, "attack_cooldown", 0, 60, default=0.0
            )
            new_boss.special_cooldown = number(
                boss_data, "special_cooldown", 0, 60, default=0.0
            )
            new_boss.hit_flash_timer = number(
                boss_data, "hit_flash_timer", 0, 1, default=0.0
            )
            telegraph = boss_data.get("telegraph_position")
            if telegraph is not None:
                if (
                    not isinstance(telegraph, list)
                    or len(telegraph) != 2
                    or any(
                        isinstance(part, bool)
                        or not isinstance(part, (int, float))
                        or not math.isfinite(float(part))
                        for part in telegraph
                    )
                ):
                    raise ValueError("The saved boss telegraph position is invalid.")
                if not (
                    0 <= telegraph[0] <= self.world.get_width()
                    and 0 <= telegraph[1] <= self.world.get_height()
                ):
                    raise ValueError("The saved boss telegraph lies outside the dungeon.")
                new_boss.telegraph_position = (int(telegraph[0]), int(telegraph[1]))
            else:
                new_boss.telegraph_position = None
            if not new_boss.is_dead() and self.world.collides_with_wall(new_boss.rect):
                raise ValueError("The saved boss position intersects a wall.")
            if phase != new_wave.BOSS and not new_boss.is_dead():
                raise ValueError("A living boss can only be saved during the boss encounter.")
        if phase == new_wave.VICTORY and new_boss is not None and not new_boss.is_dead():
            raise ValueError("A victory save still has a living boss.")

        # DROPPED ITEMS
        loot_data = data.get("loot")
        if not isinstance(loot_data, list) or len(loot_data) > 500:
            raise ValueError("Saved loot data is invalid.")
        new_loot = []
        for saved_drop in loot_data:
            if not isinstance(saved_drop, dict):
                raise ValueError("A saved loot item is invalid.")
            item = resolve_item(saved_drop.get("item"))
            if item is None:
                raise ValueError("A saved loot item is missing its item type.")
            drop_x = number(saved_drop, "x", 0, self.world.get_width(), True)
            drop_y = number(saved_drop, "y", 0, self.world.get_height(), True)
            new_loot.append(Loot(drop_x, drop_y, item))

        # QUEST STATE
        quest_data = data.get("quest")
        if not isinstance(quest_data, dict):
            raise ValueError("Saved quest data is missing.")
        new_quest = QuestManager()
        new_quest.completed = flag(quest_data, "completed", False)
        new_quest.reward_claimed = flag(quest_data, "reward_claimed", False)
        if new_quest.reward_claimed and not new_quest.completed:
            raise ValueError("The saved quest reward state is inconsistent.")

        # Commit only after every section has been checked and reconstructed.
        self.player = new_player
        self.wave_manager = new_wave
        self.enemies = new_enemies
        self.boss = new_boss
        self.loot = new_loot
        self.quest_manager = new_quest
        self.damage_numbers = []
        self.inventory_ui.close()
        self.quest_ui.close()
        self.dialogue_ui.close()
        self.settings_menu_visible = False
        self.settings_buttons = {}
        self.paused = False
        self.pause_menu_buttons = {}
        self.camera.update(
            self.player.rect,
            self.world.get_width(),
            self.world.get_height(),
            *self.screen.get_size()
        )

    def load_game(self):
        """Load and validate a save; leave the current run untouched on failure."""
        payload = self.save_manager.load()
        if payload is None:
            self.persistence_status = "Load failed: " + self.save_manager.last_error
            return False

        try:
            self._restore_game_state(payload["game"])
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            self.persistence_status = f"Load failed: {exc}"
            return False

        self.persistence_status = "Game loaded successfully."
        return True

    def _find_npc_position(self, spawn_x, spawn_y):
        """Find a connected floor tile a short distance from the player spawn."""
        tile_size = self.world.TILE_SIZE
        origin = (int(spawn_x // tile_size), int(spawn_y // tile_size))
        nearby = []

        # Prefer a nearby tile in the same chamber, but confirm reachability
        # through the dungeon's actual floor/corridor path graph.
        for row in range(1, self.world.rows - 1):
            for column in range(1, self.world.columns - 1):
                if self.world.tiles[row][column] != self.world.FLOOR:
                    continue

                dx = column - origin[0]
                dy = row - origin[1]
                distance_squared = dx * dx + dy * dy
                if distance_squared < 9 or distance_squared > 36:
                    continue

                npc_rect = pygame.Rect(
                    column * tile_size + 4,
                    row * tile_size + 2,
                    32,
                    36,
                )
                if self.world.collides_with_wall(npc_rect):
                    continue

                nearby.append(
                    (distance_squared, abs(dy), row, column)
                )

        nearby.sort()
        for _, _, row, column in nearby:
            if self.world.find_path(origin, (column, row)):
                return (column * tile_size + 4, row * tile_size + 2)

        # Defensive fallback: search any connected floor tile if the central
        # chamber is unusually small or altered by future dungeon generation.
        fallback = []
        for row in range(1, self.world.rows - 1):
            for column in range(1, self.world.columns - 1):
                if self.world.tiles[row][column] != self.world.FLOOR:
                    continue
                dx = column - origin[0]
                dy = row - origin[1]
                distance_squared = dx * dx + dy * dy
                if distance_squared < 4:
                    continue
                npc_rect = pygame.Rect(
                    column * tile_size + 4,
                    row * tile_size + 2,
                    32,
                    36,
                )
                if not self.world.collides_with_wall(npc_rect):
                    fallback.append(
                        (distance_squared, abs(dy), row, column)
                    )

        fallback.sort()
        for _, _, row, column in fallback:
            if self.world.find_path(origin, (column, row)):
                return (column * tile_size + 4, row * tile_size + 2)

        # The generated dungeon always has connected floor, but keeping a
        # final valid value makes construction robust against custom worlds.
        return (spawn_x + tile_size * 3, spawn_y)

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

        if self.inventory_ui.visible or self.quest_ui.visible or self.dialogue_ui.visible:

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
        # BOSS AI
        # ==================================================

        if self.wave_manager.is_boss:
            if self.boss is None:
                self._spawn_boss()
            if self.boss is not None and not self.boss.is_dead():
                self.boss.update(self.player, self.dt, self.world)

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

            # The boss shares the player's existing attack timing and hit
            # gating, so one swing can never damage it repeatedly.
            if (
                not self.player.attack_has_hit
                and self.wave_manager.is_boss
                and self.boss is not None
                and not self.boss.is_dead()
                and self.player.attack_rect.colliderect(self.boss.rect)
            ):
                damage = self.player.attack_damage
                self.boss.take_damage(damage)
                self.damage_numbers.append(
                    DamageNumber(
                        self.boss.rect.centerx,
                        self.boss.rect.top,
                        damage,
                    )
                )
                self.player.attack_has_hit = True

                if self.boss.is_dead():
                    self.player.add_xp(self.boss.xp_reward)
                    self.loot.append(
                        Loot(
                            self.boss.rect.centerx - 12,
                            self.boss.rect.centery - 12,
                            HEALTH_POTION,
                        )
                    )
                    self.wave_manager.defeat_boss()

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

    def _spawn_boss(self):
        """Place the guardian on safe edge floor away from the player and Warden."""
        avoid_positions = [
            (self.player.rect.x, self.player.rect.y),
            (self.npc.rect.x, self.npc.rect.y),
        ]
        avoid_positions.extend(
            (enemy.rect.x, enemy.rect.y)
            for enemy in self.enemies
            if not enemy.is_dead()
        )

        # Try each dungeon quadrant in turn. The boss has a slightly broader
        # collision rectangle than ordinary enemies, so reject any candidate
        # that would touch a wall before accepting the spawn.
        for spawn_index in range(self.wave_manager.total_waves):
            positions = self.world.get_edge_spawn_positions(
                1,
                avoid_positions=avoid_positions,
                start_index=spawn_index,
            )
            if not positions:
                continue
            boss = DungeonBoss(*positions[0])
            if not self.world.collides_with_wall(boss.rect):
                self.boss = boss
                self.wave_manager.announcement = "THE ASHEN TITAN"
                self.wave_manager.announcement_timer = max(
                    self.wave_manager.announcement_timer, 2.8
                )
                return True

        # The generated dungeon has clear edge floor; this defensive fallback
        # keeps a boss instance available even for custom test worlds.
        self.boss = DungeonBoss(*self.world.get_center_spawn_position())
        return not self.world.collides_with_wall(self.boss.rect)

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
        self.boss = None
        self.quest_manager = QuestManager()
        self.quest_ui.close()
        self.dialogue_ui.close()
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
            "ALL WAVES AND THE GUARDIAN DEFEATED",
            True, (231, 225, 210)
        )
        quest_reward_text = self.game_over_small_font.render(
            f"QUEST COMPLETE  +{self.quest_manager.REWARD_XP} XP",
            True, (132, 207, 143)
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
            quest_reward_text,
            (center_x - quest_reward_text.get_width() // 2, center_y + 8)
        )
        self.screen.blit(
            restart_text, (center_x - restart_text.get_width() // 2, center_y + 48)
        )
        self.screen.blit(
            quit_text, (center_x - quit_text.get_width() // 2, center_y + 88)
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
        # BOSS
        # ==================================================

        if self.boss is not None:
            self.boss.render(self.screen, self.camera)

        # ==================================================
        # NPC
        # ==================================================

        self.npc.render(self.screen, self.camera)

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

        # Draw the interaction hint after scene finishing so it remains crisp.
        self.npc.render_interaction_prompt(
            self.screen, self.camera, self.player
        )

        if self.boss is not None and self.wave_manager.is_boss:
            self.boss.render_telegraph(self.screen, self.camera)
            self.boss.render_health_bar(self.screen)

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

        self.dialogue_ui.render(self.screen)

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
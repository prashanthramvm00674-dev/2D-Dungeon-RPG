
import pygame
import math

from entities.inventory import Inventory


class Player:

    def __init__(self):

        # ==================================================
        # POSITION
        # ==================================================

        self.x = 640
        self.y = 360

        # ==================================================
        # SIZE
        # ==================================================

        self.width = 40
        self.height = 40

        # ==================================================
        # APPEARANCE
        # ==================================================

        self.color = (50, 150, 255)

        # ==================================================
        # MOVEMENT
        # ==================================================

        self.speed = 300

        self.direction = "down"
        self.is_moving = False

        # ==================================================
        # INVENTORY
        # ==================================================

        self.inventory = Inventory(12)

        # ==================================================
        # EQUIPMENT
        # ==================================================

        self.equipped_weapon = None
        self.equipped_shield = None
        self.equipped_armor = None

        # ==================================================
        # LEVEL / XP
        # ==================================================

        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100

        # ==================================================
        # HEALTH
        # ==================================================

        self.base_max_health = 100
        self.max_health = self.base_max_health
        self.health = self.max_health

        self.damage_cooldown = 0.0
        self.damage_invulnerability = 0.5

        self.is_dead = False

        # ==================================================
        # HIT FLASH
        # ==================================================

        self.hit_flash_timer = 0.0
        self.hit_flash_duration = 0.12

        # ==================================================
        # COMBAT
        # ==================================================

        self.is_attacking = False

        self.attack_timer = 0.0
        self.attack_duration = 0.15

        self.attack_cooldown = 0.25
        self.attack_cooldown_timer = 0.0

        self.attack_has_hit = False

        self.attack_width = 40
        self.attack_height = 40
        self.attack_distance = 10

        # ==================================================
        # BASE ATTACK DAMAGE
        # ==================================================

        self.base_attack_damage = 25
        self.attack_damage = self.base_attack_damage

        # ==================================================
        # EQUIPMENT / LEVEL BONUSES
        # ==================================================

        self.iron_sword_damage_bonus = 15

        self.level_health_bonus = 20
        self.level_damage_bonus = 5

        # ==================================================
        # PLAYER RECT
        # ==================================================

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

        # ==================================================
        # ATTACK RECT
        # ==================================================

        self.attack_rect = pygame.Rect(
            0,
            0,
            self.attack_width,
            self.attack_height
        )

    # ======================================================
    # RECALCULATE ATTACK DAMAGE
    # ======================================================

    def recalculate_attack_damage(self):

        self.attack_damage = self.base_attack_damage

        if (
            self.equipped_weapon is not None
            and self.equipped_weapon.name == "Iron Sword"
        ):

            self.attack_damage += (
                self.iron_sword_damage_bonus
            )

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        input_manager,
        dt,
        world
    ):

        if self.is_dead:
            return

        # ==================================================
        # DAMAGE COOLDOWN
        # ==================================================

        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

        # ==================================================
        # HIT FLASH
        # ==================================================

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        # ==================================================
        # COMBAT TIMERS
        # ==================================================

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt

        if self.is_attacking:

            self.attack_timer -= dt

            if self.attack_timer <= 0:
                self.is_attacking = False

        # ==================================================
        # ATTACK
        # ==================================================

        if (
            input_manager.is_pressed(pygame.K_SPACE)
            and not self.is_attacking
            and self.attack_cooldown_timer <= 0
        ):

            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.attack_cooldown_timer = self.attack_cooldown
            self.attack_has_hit = False

        # ==================================================
        # MOVEMENT
        # ==================================================

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
            direction_x != 0
            or direction_y != 0
        )

        # ==================================================
        # DIRECTION
        # ==================================================

        if direction_x < 0:
            self.direction = "left"

        elif direction_x > 0:
            self.direction = "right"

        elif direction_y < 0:
            self.direction = "up"

        elif direction_y > 0:
            self.direction = "down"

        # ==================================================
        # NORMALIZE MOVEMENT
        # ==================================================

        if self.is_moving:

            length = math.sqrt(
                direction_x ** 2
                + direction_y ** 2
            )

            direction_x /= length
            direction_y /= length

        # ==================================================
        # MOVEMENT AMOUNT
        # ==================================================

        movement_x = direction_x * self.speed * dt
        movement_y = direction_y * self.speed * dt

        # ==================================================
        # HORIZONTAL MOVEMENT
        # ==================================================

        new_rect = self.rect.copy()
        new_rect.x += int(movement_x)

        if not world.collides_with_wall(new_rect):
            self.rect.x = new_rect.x

        # ==================================================
        # VERTICAL MOVEMENT
        # ==================================================

        new_rect = self.rect.copy()
        new_rect.y += int(movement_y)

        if not world.collides_with_wall(new_rect):
            self.rect.y = new_rect.y

        # ==================================================
        # SYNC POSITION
        # ==================================================

        self.x = self.rect.x
        self.y = self.rect.y

        # ==================================================
        # ATTACK HITBOX
        # ==================================================

        self.update_attack_rect()

    # ======================================================
    # ADD XP
    # ======================================================

    def add_xp(self, amount):

        if self.is_dead or amount <= 0:
            return

        self.xp += amount

        # ==================================================
        # LEVEL UP
        # ==================================================

        while self.xp >= self.xp_to_next_level:

            self.xp -= self.xp_to_next_level
            self.level_up()

    # ======================================================
    # LEVEL UP
    # ======================================================

    def level_up(self):

        self.level += 1

        # ==================================================
        # HEALTH INCREASE
        # ==================================================

        self.max_health += self.level_health_bonus

        # ==================================================
        # BASE DAMAGE INCREASE
        # ==================================================

        self.base_attack_damage += self.level_damage_bonus

        # Recalculate damage without losing equipment bonuses.
        self.recalculate_attack_damage()

        # ==================================================
        # FULL HEAL
        # ==================================================

        self.health = self.max_health

        # ==================================================
        # NEXT XP REQUIREMENT
        # ==================================================

        self.xp_to_next_level = int(
            self.xp_to_next_level * 1.5
        )

    # ======================================================
    # TAKE DAMAGE
    # ======================================================

    def take_damage(self, damage):

        if self.is_dead:
            return

        if self.damage_cooldown > 0:
            return

        # ==================================================
        # SHIELD DAMAGE REDUCTION
        # ==================================================

        if (
            self.equipped_shield is not None
            and self.equipped_shield.name == "Shield"
        ):

            damage = int(damage * 0.75)

        # ==================================================
        # APPLY DAMAGE
        # ==================================================

        self.health -= damage

        # ==================================================
        # HIT FLASH
        # ==================================================

        self.hit_flash_timer = self.hit_flash_duration

        # ==================================================
        # TEMPORARY INVULNERABILITY
        # ==================================================

        self.damage_cooldown = self.damage_invulnerability

        # ==================================================
        # DEATH
        # ==================================================

        if self.health <= 0:

            self.health = 0
            self.is_dead = True

    # ======================================================
    # USE HEALTH POTION
    # ======================================================

    def use_health_potion(self):

        if self.is_dead:
            return False

        if self.health >= self.max_health:
            return False

        from entities.item import HEALTH_POTION

        if not self.inventory.has_item(HEALTH_POTION):
            return False

        removed = self.inventory.remove_item(
            HEALTH_POTION,
            1
        )

        if not removed:
            return False

        self.health += HEALTH_POTION.value

        if self.health > self.max_health:
            self.health = self.max_health

        return True

    # ======================================================
    # EQUIP ITEM
    # ======================================================

    def equip_item(self, item):

        if item is None:
            return False

        # ==================================================
        # WEAPON
        # ==================================================

        if item.item_type == "weapon":

            self.equipped_weapon = item
            self.recalculate_attack_damage()

            return True

        # ==================================================
        # SHIELD / ARMOR
        # ==================================================

        if item.item_type == "armor":

            self.equipped_shield = item

            return True

        return False

    # ======================================================
    # UNEQUIP WEAPON
    # ======================================================

    def unequip_weapon(self):

        self.equipped_weapon = None
        self.recalculate_attack_damage()

    # ======================================================
    # UNEQUIP SHIELD
    # ======================================================

    def unequip_shield(self):

        self.equipped_shield = None

    # ======================================================
    # UPDATE ATTACK RECT
    # ======================================================

    def update_attack_rect(self):

        if self.direction == "up":

            self.attack_rect.size = (
                self.attack_width,
                self.attack_height
            )

            self.attack_rect.midbottom = (
                self.rect.centerx,
                self.rect.top - self.attack_distance
            )

        elif self.direction == "down":

            self.attack_rect.size = (
                self.attack_width,
                self.attack_height
            )

            self.attack_rect.midtop = (
                self.rect.centerx,
                self.rect.bottom + self.attack_distance
            )

        elif self.direction == "left":

            self.attack_rect.size = (
                self.attack_height,
                self.attack_width
            )

            self.attack_rect.midright = (
                self.rect.left - self.attack_distance,
                self.rect.centery
            )

        elif self.direction == "right":

            self.attack_rect.size = (
                self.attack_height,
                self.attack_width
            )

            self.attack_rect.midleft = (
                self.rect.right + self.attack_distance,
                self.rect.centery
            )

    # ======================================================
    # RENDER
    # ======================================================

    def render(
        self,
        screen,
        camera
    ):

        screen_rect = camera.apply(self.rect)

        # ==================================================
        # PLAYER COLOR
        # ==================================================

        if self.hit_flash_timer > 0:
            player_color = (255, 255, 255)
        else:
            player_color = self.color

        pygame.draw.rect(
            screen,
            player_color,
            screen_rect
        )

        # ==================================================
        # ATTACK HITBOX
        # ==================================================

        if self.is_attacking:

            attack_screen_rect = camera.apply(
                self.attack_rect
            )

            pygame.draw.rect(
                screen,
                (255, 80, 80),
                attack_screen_rect
            )

        # ==================================================
        # HEALTH BAR
        # ==================================================

        bar_width = 100
        bar_height = 8

        health_ratio = max(
            0.0,
            min(1.0, self.health / self.max_health)
            if self.max_health > 0
            else 0.0
        )

        background_rect = pygame.Rect(
            screen_rect.centerx - bar_width // 2,
            screen_rect.top - 20,
            bar_width,
            bar_height
        )

        health_rect = pygame.Rect(
            screen_rect.centerx - bar_width // 2,
            screen_rect.top - 20,
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

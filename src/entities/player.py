
import pygame
import math

from entities.inventory import Inventory


class Player:

    def __init__(self):

        # ==================================================
        # POSITION
        # ==================================================

        self.x = 0
        self.y = 0

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

    def render(self, screen, camera):
        """Draw a compact, original pixel-art adventurer instead of a flat block."""
        screen_rect = camera.apply(self.rect)
        x, y = screen_rect.x, screen_rect.y
        cx = screen_rect.centerx
        bottom = screen_rect.bottom

        # Soft grounding shadow keeps the character connected to the flagstones.
        shadow = pygame.Surface((52, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 125), (2, 2, 48, 11))
        screen.blit(shadow, (cx - 26, bottom - 10))

        flash = self.hit_flash_timer > 0
        outline = (13, 19, 27)
        armor_dark = (22, 52, 92) if not flash else (170, 190, 205)
        armor = (38, 102, 177) if not flash else (250, 250, 245)
        armor_light = (86, 174, 236) if not flash else (255, 255, 255)
        steel = (189, 211, 222)
        leather = (95, 55, 33)
        gold = (224, 157, 59)

        # Boots and split greaves.
        pygame.draw.rect(screen, outline, (x + 8, y + 29, 11, 9))
        pygame.draw.rect(screen, outline, (x + 21, y + 29, 11, 9))
        pygame.draw.rect(screen, (39, 48, 62), (x + 9, y + 30, 9, 7))
        pygame.draw.rect(screen, (39, 48, 62), (x + 22, y + 30, 9, 7))
        pygame.draw.rect(screen, (12, 17, 23), (x + 7, y + 36, 13, 4))
        pygame.draw.rect(screen, (12, 17, 23), (x + 21, y + 36, 13, 4))
        pygame.draw.line(screen, (98, 126, 147), (x + 10, y + 31), (x + 17, y + 31), 1)
        pygame.draw.line(screen, (98, 126, 147), (x + 23, y + 31), (x + 30, y + 31), 1)

        # Arms sit behind the chest plate.
        pygame.draw.polygon(
            screen, outline,
            [(x + 10, y + 15), (x + 5, y + 19), (x + 7, y + 28),
             (x + 12, y + 29), (x + 15, y + 22)]
        )
        pygame.draw.polygon(
            screen, (64, 91, 125),
            [(x + 10, y + 16), (x + 7, y + 20), (x + 9, y + 26),
             (x + 12, y + 25), (x + 14, y + 20)]
        )
        pygame.draw.polygon(
            screen, outline,
            [(x + 29, y + 15), (x + 34, y + 18), (x + 33, y + 27),
             (x + 28, y + 29), (x + 25, y + 22)]
        )
        pygame.draw.polygon(
            screen, (64, 91, 125),
            [(x + 29, y + 16), (x + 32, y + 19), (x + 31, y + 25),
             (x + 28, y + 26), (x + 26, y + 21)]
        )

        # Chest silhouette, raised blue plates, and small brass rivets.
        torso = [
            (x + 11, y + 15), (x + 16, y + 13), (x + 24, y + 13),
            (x + 29, y + 16), (x + 27, y + 28), (x + 23, y + 31),
            (x + 16, y + 30), (x + 12, y + 27)
        ]
        pygame.draw.polygon(screen, outline, torso)
        pygame.draw.polygon(
            screen, armor_dark,
            [(x + 13, y + 16), (x + 17, y + 15), (x + 23, y + 15),
             (x + 27, y + 17), (x + 25, y + 27), (x + 22, y + 29),
             (x + 16, y + 28), (x + 14, y + 25)]
        )
        pygame.draw.polygon(
            screen, armor,
            [(x + 15, y + 17), (x + 20, y + 16), (x + 25, y + 18),
             (x + 23, y + 25), (x + 17, y + 25)]
        )
        pygame.draw.line(screen, armor_light, (x + 16, y + 17), (x + 20, y + 16), 2)
        pygame.draw.line(screen, (28, 69, 113), (x + 19, y + 19), (x + 18, y + 25), 2)
        pygame.draw.rect(screen, gold, (x + 19, y + 27, 5, 4))
        pygame.draw.rect(screen, (62, 39, 24), (x + 14, y + 28, 13, 3))
        pygame.draw.rect(screen, (255, 210, 91), (x + 20, y + 27, 3, 3))

        # Shoulder guards give the silhouette a readable fantasy-armour shape.
        pygame.draw.polygon(
            screen, outline,
            [(x + 9, y + 14), (x + 13, y + 12), (x + 17, y + 16),
             (x + 14, y + 21), (x + 10, y + 19)]
        )
        pygame.draw.polygon(
            screen, (48, 91, 138),
            [(x + 10, y + 15), (x + 13, y + 14), (x + 15, y + 17),
             (x + 13, y + 19), (x + 11, y + 18)]
        )
        pygame.draw.polygon(
            screen, outline,
            [(x + 25, y + 16), (x + 29, y + 12), (x + 33, y + 15),
             (x + 32, y + 19), (x + 28, y + 21)]
        )
        pygame.draw.polygon(
            screen, (48, 91, 138),
            [(x + 27, y + 16), (x + 29, y + 14), (x + 31, y + 16),
             (x + 30, y + 18), (x + 28, y + 19)]
        )

        # Helmet: dark rim, bright crown, visor slit, and central crest.
        helmet = [
            (x + 12, y + 11), (x + 13, y + 5), (x + 17, y + 2),
            (x + 24, y + 2), (x + 28, y + 6), (x + 29, y + 12),
            (x + 25, y + 17), (x + 16, y + 17)
        ]
        pygame.draw.polygon(screen, outline, helmet)
        pygame.draw.polygon(
            screen, (22, 83, 145),
            [(x + 14, y + 10), (x + 15, y + 6), (x + 18, y + 4),
             (x + 23, y + 4), (x + 26, y + 7), (x + 27, y + 11),
             (x + 24, y + 15), (x + 17, y + 15)]
        )
        pygame.draw.line(screen, (93, 185, 245), (x + 16, y + 6), (x + 20, y + 4), 2)
        pygame.draw.polygon(
            screen, (10, 19, 30),
            [(x + 15, y + 10), (x + 26, y + 10), (x + 25, y + 13),
             (x + 17, y + 13)]
        )
        pygame.draw.line(screen, gold, (x + 18, y + 12), (x + 24, y + 12), 1)
        pygame.draw.line(screen, armor_light, (x + 20, y + 3), (x + 20, y + 7), 2)
        pygame.draw.rect(screen, gold, (x + 20, y + 7, 2, 3))

        # Blade orientation follows the last movement direction. The weapon
        # extends beyond the body silhouette, like the supplied gameplay aim.
        weapon_points = {
            "right": ((x + 30, y + 23), (x + 39, y + 10)),
            "left": ((x + 10, y + 23), (x + 1, y + 10)),
            "up": ((x + 25, y + 13), (x + 34, y + 3)),
            "down": ((x + 27, y + 27), (x + 36, y + 37)),
        }
        start, tip = weapon_points.get(self.direction, weapon_points["right"])
        pygame.draw.line(screen, outline, start, tip, 5)
        pygame.draw.line(screen, leather, start, tip, 3)
        blade_start = (
            int(start[0] + (tip[0] - start[0]) * 0.34),
            int(start[1] + (tip[1] - start[1]) * 0.34),
        )
        pygame.draw.line(screen, outline, blade_start, tip, 4)
        pygame.draw.line(screen, steel, blade_start, tip, 2)
        pygame.draw.line(
            screen, (243, 249, 245),
            (blade_start[0], blade_start[1] - 1),
            (tip[0], tip[1] - 1), 1
        )
        pygame.draw.line(
            screen, gold,
            (int(start[0] - 2), int(start[1] + 2)),
            (int(start[0] + 2), int(start[1] - 2)), 3
        )

        # Attacks use a quick glowing slash, not a solid debug hitbox.
        if self.is_attacking:
            slash = pygame.Rect(x - 7, y - 8, 54, 54)
            arc_angles = {
                "right": (4.0, 2.1),
                "left": (0.9, 5.2),
                "up": (5.1, 3.6),
                "down": (2.1, 0.4),
            }
            start_angle, stop_angle = arc_angles.get(self.direction, (4.0, 2.1))
            pygame.draw.arc(screen, (66, 150, 232), slash, start_angle, stop_angle, 3)
            pygame.draw.arc(
                screen, (220, 244, 255),
                slash.inflate(-6, -6), start_angle, stop_angle, 1
            )

"""Tests for the Ashen Titan's telegraphs, dodge windows, and second phase."""

import sys
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from entities.dungeon_boss import DungeonBoss


class FakePlayer:
    def __init__(self, position=(110, 110)):
        self.rect = pygame.Rect(position[0], position[1], 40, 40)
        self.health = 100
        self.damage_taken = []

    def take_damage(self, damage):
        self.damage_taken.append(damage)
        self.health = max(0, self.health - damage)


class NoMovementWorld:
    TILE_SIZE = 40

    def find_path(self, start, goal):
        return [start, goal]

    def collides_with_wall(self, rect):
        return False


class IdentityCamera:
    def apply(self, rect):
        return rect.copy()


def test_slam_is_telegraphed_and_can_be_dodged():
    boss = DungeonBoss(100, 100)
    player = FakePlayer()
    world = NoMovementWorld()

    boss.update(player, 0.016, world)
    assert boss.state == "slam_windup"
    assert boss.is_telegraphing
    assert boss.telegraph_position == player.rect.center

    # The target is locked at windup start; moving away avoids the slam.
    player.rect.topleft = (450, 420)
    boss.update(player, boss.SLAM_WINDUP + 0.01, world)
    assert player.damage_taken == []
    assert boss.state == "recover"
    assert not boss.is_telegraphing


def test_slam_damages_a_player_who_stays_in_the_warning():
    boss = DungeonBoss(100, 100)
    player = FakePlayer()
    world = NoMovementWorld()

    boss.update(player, 0.016, world)
    boss.update(player, boss.SLAM_WINDUP + 0.01, world)

    assert player.damage_taken == [boss.SLAM_DAMAGE]
    assert boss.state == "recover"


def test_phase_two_shockwave_has_a_warning_and_can_hit():
    boss = DungeonBoss(100, 100)
    boss.health = boss.max_health // 2
    boss.special_cooldown = 0.0
    player = FakePlayer()
    world = NoMovementWorld()

    boss.update(player, 0.016, world)
    assert boss.is_phase_two
    assert boss.state == "pulse_windup"
    assert boss.is_telegraphing

    boss.update(player, boss.PULSE_WINDUP + 0.01, world)
    assert player.damage_taken == [boss.PULSE_DAMAGE]
    assert boss.state == "recover"


def test_damage_is_clamped_and_death_is_stable():
    boss = DungeonBoss(100, 100)
    boss.take_damage(125)
    assert boss.health == boss.max_health - 125
    boss.take_damage(10000)
    assert boss.health == 0
    assert boss.is_dead()
    boss.take_damage(100)
    assert boss.health == 0


def test_boss_art_telegraph_and_health_bar_render():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    boss = DungeonBoss(100, 100)
    boss.update(FakePlayer(), 0.016, NoMovementWorld())

    boss.render(screen, IdentityCamera())
    boss.render_telegraph(screen, IdentityCamera())
    boss.render_health_bar(screen)

    assert boss.is_telegraphing
    pygame.quit()


def main():
    pygame.init()
    test_slam_is_telegraphed_and_can_be_dodged()
    test_slam_damages_a_player_who_stays_in_the_warning()
    test_phase_two_shockwave_has_a_warning_and_can_hit()
    test_damage_is_clamped_and_death_is_stable()
    test_boss_art_telegraph_and_health_bar_render()
    print(
        "Boss tests passed: telegraphed slam, dodge window, phase-two pulse, "
        "damage bounds, sprite, telegraphs, and health bar."
    )


if __name__ == "__main__":
    main()

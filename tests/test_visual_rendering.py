import sys
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from core.camera import Camera
from entities.enemy import Enemy
from entities.player import Player
from graphics.lighting import LightingSystem
from ui.hud import HUD
from world.world import World


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))

    world = World()
    player = Player()
    player_x, player_y = world.get_center_spawn_position()
    player.rect.topleft = (player_x, player_y)
    player.x, player.y = player_x, player_y
    player.health = 73
    player.xp = 38
    player.is_attacking = True

    enemy_positions = world.get_edge_spawn_positions(
        1,
        avoid_positions=[(player_x, player_y)]
    )
    enemy_x, enemy_y = enemy_positions[0]
    enemy = Enemy(enemy_x, enemy_y, "Skeleton")
    enemy.hit_flash_timer = 0.05

    camera = Camera(*screen.get_size())
    camera.update(
        player.rect,
        world.get_width(),
        world.get_height(),
        *screen.get_size()
    )

    # Smoke-test the complete updated drawing stack on a headless surface.
    world.render(screen, camera)
    enemy.render(screen, camera)
    player.render(screen, camera)

    lighting = LightingSystem()
    lighting.render(screen, world.torches, player, camera)
    world.render_torches(screen, camera)
    enemy.render_health_bar(screen, camera)

    hud = HUD()
    hud.render(screen, player, [enemy])
    assert hud.menu_button_rect.width > 0
    assert hud.menu_button_contains(hud.menu_button_rect.center)
    assert screen.get_size() == (1280, 720)

    pygame.quit()
    print("Visual smoke test passed: world, sprites, lighting, and HUD rendered.")


if __name__ == "__main__":
    main()

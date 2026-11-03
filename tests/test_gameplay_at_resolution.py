import sys
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from core.game import Game


def main():
    pygame.init()

    assert SCREEN_WIDTH == 1920, f"Expected reference width 1920, got {SCREEN_WIDTH}"
    assert SCREEN_HEIGHT == 1080, f"Expected reference height 1080, got {SCREEN_HEIGHT}"
    print(f"Reference resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    game = Game()
    actual_width, actual_height = game.screen.get_size()
    assert actual_width > 0 and actual_height > 0, "Game created an empty display."

    if game.fullscreen:
        assert game.screen.get_size() == game.desktop_size
        print(f"[PASS] Fullscreen display matches desktop: {actual_width}x{actual_height}")
    else:
        assert game.screen.get_size() == game.windowed_size
        assert actual_width <= SCREEN_WIDTH
        assert actual_height <= SCREEN_HEIGHT
        print(f"[PASS] Adaptive window created: {actual_width}x{actual_height}")

    actual_ratio = actual_width / actual_height
    target_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
    assert abs(actual_ratio - target_ratio) < 0.01, (
        f"Display aspect ratio changed: expected {target_ratio:.3f}, got {actual_ratio:.3f}"
    )

    assert game.world is not None
    assert game.world.get_width() == 3200
    assert game.world.get_height() == 2000
    print(f"[PASS] World loaded: {game.world.get_width()}x{game.world.get_height()}")

    assert game.player is not None
    assert game.player.health > 0
    print(f"[PASS] Player loaded: health={game.player.health}")

    assert len(game.enemies) > 0
    print(f"[PASS] Enemies loaded: {len(game.enemies)} enemies")

    assert game.camera is not None
    assert game.camera.screen_width == actual_width
    assert game.camera.screen_height == actual_height
    print(f"[PASS] Camera matches display: {actual_width}x{actual_height}")

    assert game.hud is not None
    print("[PASS] HUD initialized")

    game.dt = 0.016
    game.input.update()
    game.update()
    print("[PASS] Single update cycle completed")

    game.render()
    print("[PASS] Single render cycle completed")

    pygame.quit()
    print("\n=== Gameplay Resolution Test Complete ===")
    print("All gameplay systems verified using the configured reference resolution.")


if __name__ == "__main__":
    main()

import sys
from pathlib import Path

import pygame

# Add the project's src directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from core.game import Game


def main():
    pygame.init()

    # Verify resolution
    assert SCREEN_WIDTH == 1920, f"Expected 1920, got {SCREEN_WIDTH}"
    assert SCREEN_HEIGHT == 1080, f"Expected 1080, got {SCREEN_HEIGHT}"

    print(f"Testing gameplay at {SCREEN_WIDTH}x{SCREEN_HEIGHT}...")

    # Initialize game
    game = Game()

    # Verify game uses new resolution
    assert game.screen.get_width() == SCREEN_WIDTH
    assert game.screen.get_height() == SCREEN_HEIGHT

    print(f"[PASS] Game initialized at {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    # Verify world exists
    assert game.world is not None
    assert game.world.get_width() == 1600
    assert game.world.get_height() == 1000

    print(f"[PASS] World loaded: {game.world.get_width()}x{game.world.get_height()}")

    # Verify player exists
    assert game.player is not None
    assert game.player.health > 0

    print(f"[PASS] Player loaded: health={game.player.health}")

    # Verify enemies exist
    assert len(game.enemies) > 0
    print(f"[PASS] Enemies loaded: {len(game.enemies)} enemies")

    # Verify camera exists
    assert game.camera is not None
    assert game.camera.screen_width == SCREEN_WIDTH
    assert game.camera.screen_height == SCREEN_HEIGHT

    print(f"[PASS] Camera initialized: {game.camera.screen_width}x{game.camera.screen_height}")

    # Verify HUD exists
    assert game.hud is not None
    print(f"[PASS] HUD initialized")

    # Test a single update cycle
    game.dt = 0.016  # ~60 FPS
    game.input.update()
    game.update()

    print(f"[PASS] Single update cycle completed")

    # Test a single render cycle
    game.render()

    print(f"[PASS] Single render cycle completed")

    pygame.quit()
    print("\n=== Gameplay Test Complete ===")
    print("All gameplay systems verified at 1920x1080!")


if __name__ == "__main__":
    main()

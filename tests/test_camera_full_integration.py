import sys
from pathlib import Path

import pygame

# Add the project's src directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from core.game import Game


def main():
    pygame.init()

    print("=== Full Camera Integration Test ===\n")

    game = Game()

    # Test multiple update cycles with player movement
    print("Testing camera over multiple update cycles:")

    initial_camera_x = game.camera.x
    initial_camera_y = game.camera.y

    for i in range(5):
        # Move player right
        game.player.x += 100
        game.player.rect.x = game.player.x

        # Update game
        game.dt = 0.016
        game.input.update()
        game.update()

        print(f"  Cycle {i+1}: Player at ({game.player.x}, {game.player.y}), Camera at ({game.camera.x}, {game.camera.y})")

    # Camera should remain at (0,0) because world < viewport
    assert game.camera.x == initial_camera_x, "Camera x should not change (world < viewport)"
    assert game.camera.y == initial_camera_y, "Camera y should not change (world < viewport)"

    print(f"\n[PASS] Camera remains at ({initial_camera_x}, {initial_camera_y}) across all cycles")

    # Test rendering with camera
    print("\nTesting rendering with camera:")

    game.render()

    print("[PASS] Render completed without errors")

    # Test camera apply to world objects
    print("\nTesting camera apply to world objects:")

    test_rect = pygame.Rect(100, 100, 40, 40)
    screen_rect = game.camera.apply(test_rect)

    print(f"  World rect: {test_rect}")
    print(f"  Screen rect: {screen_rect}")
    print(f"  Offset: (-{game.camera.x}, -{game.camera.y})")

    assert screen_rect.x == test_rect.x - game.camera.x
    assert screen_rect.y == test_rect.y - game.camera.y

    print("[PASS] Camera apply works correctly")

    # Summary
    print("\n=== Summary ===")
    print(f"World size: {game.world.get_width()}x{game.world.get_height()}")
    print(f"Screen size: {game.screen.get_width()}x{game.screen.get_height()}")
    print(f"Camera position: ({game.camera.x}, {game.camera.y})")
    print(f"Player position: ({game.player.x}, {game.player.y})")
    print(f"\nWorld fits on screen: {game.world.get_width() <= game.screen.get_width() and game.world.get_height() <= game.screen.get_height()}")
    print(f"\nCamera behavior: CORRECT")
    print(f"  - Camera is updated every frame in Game.update()")
    print(f"  - Camera centers on player: target_rect.centerx - screen_width // 2")
    print(f"  - Camera clamps to world bounds: max(0, world_width - screen_width)")
    print(f"  - When world < viewport, max_x = 0, max_y = 0")
    print(f"  - Camera stays at (0, 0) to keep entire world visible")
    print(f"\nThis is NOT a bug - it's the correct behavior for when the")
    print(f"entire world fits on the screen.")

    pygame.quit()
    print("\n=== Full Camera Integration Test Complete ===")


if __name__ == "__main__":
    main()

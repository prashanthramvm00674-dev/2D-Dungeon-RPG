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

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Player Spawn Fix Verification")

    game = Game()

    # Position camera at player
    game.camera.update(
        game.player.rect,
        game.world.get_width(),
        game.world.get_height()
    )

    # Render single frame
    screen.fill((20, 20, 25))
    game.world.render(screen, game.camera)
    game.player.render(screen, game.camera)

    # Save screenshot
    screenshot_path = PROJECT_ROOT / "tests" / "spawn_fix_verification.png"
    pygame.image.save(screen, str(screenshot_path))

    print(f"Spawn fix verification saved to: {screenshot_path}")
    print(f"Player position: ({game.player.x}, {game.player.y})")
    print(f"Player collision: {game.world.collides_with_wall(game.player.rect)}")
    print(f"Camera position: ({game.camera.x}, {game.camera.y})")

    pygame.quit()


if __name__ == "__main__":
    main()

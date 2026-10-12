import sys
from pathlib import Path

import pygame

# Add the project's src directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from world.world import World
from core.camera import Camera


def main():
    pygame.init()

    # Use new resolution (1920x1080)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Stage 3: Resolution Preview (1920x1080)")

    world = World()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Center camera on world (world is smaller than screen now)
    # Position to show the central corridor area
    camera.update(
        pygame.Rect(world.get_width() // 2, world.get_height() // 2, 40, 40),
        world.get_width(),
        world.get_height()
    )

    # Render single frame
    screen.fill((20, 20, 25))
    world.render(screen, camera)

    # Save screenshot
    screenshot_path = PROJECT_ROOT / "tests" / "stage3_preview.png"
    pygame.image.save(screen, str(screenshot_path))

    print(f"Stage 3 preview saved to: {screenshot_path}")
    print(f"Resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"World size: {world.get_width()}x{world.get_height()}")

    pygame.quit()


if __name__ == "__main__":
    main()

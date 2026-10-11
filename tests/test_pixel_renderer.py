
import sys
from pathlib import Path

import pygame

# Make the project root importable when this test is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from graphics.pixel_renderer import PixelRenderer
except ModuleNotFoundError:
    # Resolve imports when the tests directory is the current working directory.
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from graphics.pixel_renderer import PixelRenderer


def main():
    pygame.init()

    renderer = PixelRenderer()

    # Test transparent surface creation.
    surface = renderer.create_surface((40, 40))
    assert surface.get_size() == (40, 40)
    assert surface.get_flags() & pygame.SRCALPHA

    # Test crisp scaling.
    scaled = renderer.scale_pixel_art(surface, (80, 80))
    assert scaled.get_size() == (80, 80)

    # Test texture caching.
    renderer.cache_texture("test_texture", surface)
    assert renderer.get_cached_texture("test_texture") is surface

    # Test cache clearing.
    renderer.clear_cache()
    assert renderer.get_cached_texture("test_texture") is None

    pygame.quit()
    print("PixelRenderer tests passed!")


if __name__ == "__main__":
    main()

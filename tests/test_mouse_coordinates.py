import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from core.mouse import normalize_mouse_position


def main():
    # Window points map proportionally into a higher-resolution drawing surface.
    assert normalize_mouse_position(
        (150, 75),
        (800, 400),
        (1200, 600),
    ) == (100, 50)

    # Standard DPI and invalid size cases retain safe integer coordinates.
    assert normalize_mouse_position(
        (120, 48),
        (800, 400),
        (800, 400),
    ) == (120, 48)
    assert normalize_mouse_position(
        (12.4, 9.6),
        (800, 400),
        (0, 0),
    ) == (12, 10)

    print("Mouse-coordinate checks passed: DPI scaling, normal windows, and safe fallback.")


if __name__ == "__main__":
    main()

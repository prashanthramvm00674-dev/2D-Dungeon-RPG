import pygame


def normalize_mouse_position(position, surface_size, window_size=None):
    """Map window-coordinate mouse input to the display surface's pixel space.

    On Windows with display scaling, SDL may report a logical window size
    while Pygame draws to a higher-resolution surface. Keeping input in the
    same coordinate space as rendered UI prevents offset clicks.
    """
    x, y = position
    surface_width, surface_height = surface_size

    if window_size is None:
        try:
            window_size = pygame.display.get_window_size()
        except pygame.error:
            window_size = surface_size

    window_width, window_height = window_size
    if min(surface_width, surface_height, window_width, window_height) <= 0:
        return (int(round(x)), int(round(y)))

    if (surface_width, surface_height) == (window_width, window_height):
        return (int(round(x)), int(round(y)))

    return (
        int(round(x * surface_width / window_width)),
        int(round(y * surface_height / window_height)),
    )

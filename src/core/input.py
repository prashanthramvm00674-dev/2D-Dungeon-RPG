import pygame


class InputManager:
    def __init__(self):
        self.keys = pygame.key.get_pressed()
        self.previous_keys = self.keys

        self.mouse_buttons = pygame.mouse.get_pressed()
        self.previous_mouse_buttons = self.mouse_buttons

    def update(self):
        self.previous_keys = self.keys
        self.keys = pygame.key.get_pressed()

        self.previous_mouse_buttons = self.mouse_buttons
        self.mouse_buttons = pygame.mouse.get_pressed()

    def is_down(self, key):
        return self.keys[key]

    def is_pressed(self, key):
        return self.keys[key] and not self.previous_keys[key]

    def is_released(self, key):
        return not self.keys[key] and self.previous_keys[key]

    def mouse_down(self, button):
        return self.mouse_buttons[button - 1]

    def mouse_pressed(self, button):
        return (
            self.mouse_buttons[button - 1]
            and not self.previous_mouse_buttons[button - 1]
        )

    def mouse_released(self, button):
        return (
            not self.mouse_buttons[button - 1]
            and self.previous_mouse_buttons[button - 1]
        )

    def mouse_position(self):
        return pygame.mouse.get_pos()
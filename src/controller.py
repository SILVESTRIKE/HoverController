# -*- coding: utf-8 -*-
import pyautogui
from pynput.mouse import Controller as PynputController, Button

# Disable pyautogui fail-safe for smoother control
pyautogui.FAILSAFE = False


class SystemController:
    """
    Handles all interactions with the operating system:
    Mouse movement, clicking, scrolling, and keyboard input.
    """
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.mouse = PynputController()

    def move_mouse_relative(self, dx_raw, dy_raw, speed_multiplier):
        """Moves mouse relative to current position."""
        px_x = dx_raw * self.screen_width * speed_multiplier
        px_y = dy_raw * self.screen_height * speed_multiplier
        self.mouse.move(px_x, px_y)

    def move_mouse_absolute_normalized(self, x_norm, y_norm):
        """Moves mouse to an absolute position (0.0-1.0 mapped to screen)."""
        target_x = int(x_norm * self.screen_width)
        target_y = int(y_norm * self.screen_height)
        target_y = int(y_norm * self.screen_height)
        self.mouse.position = (target_x, target_y)

    def get_position(self):
        """Returns current mouse position (x, y)."""
        return self.mouse.position

    def move_mouse_pixels(self, dx, dy):
        """Moves mouse by exact pixels."""
        self.mouse.move(dx, dy)

    def mouse_click(self, button="left"):
        b = Button.left if button == "left" else Button.right
        self.mouse.click(b)

    def start_drag(self):
        self.mouse.press(Button.left)

    def stop_drag(self):
        self.mouse.release(Button.left)

    def scroll(self, clicks):
        """Scroll vertically. Positive = up, negative = down."""
        pyautogui.scroll(clicks)

    def scroll_horizontal(self, clicks):
        """Scroll horizontally. Positive = right, negative = left."""
        pyautogui.hscroll(clicks)

    # ================== KEYBOARD METHODS ==================

    def press_key(self, key):
        """Press a single key."""
        pyautogui.press(key)

    def type_text(self, text):
        """Type text string with small interval."""
        pyautogui.write(text, interval=0.02)

    def hotkey(self, *keys):
        """Execute keyboard shortcut."""
        pyautogui.hotkey(*keys)

    def press_enter(self):
        pyautogui.press('enter')

    def press_tab(self):
        pyautogui.press('tab')

    def press_backspace(self, times=1):
        """Press backspace multiple times."""
        for _ in range(times):
            pyautogui.press('backspace')

    def clear_field(self):
        """Select all and delete."""
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')

    def copy(self):
        pyautogui.hotkey('ctrl', 'c')

    def paste(self):
        pyautogui.hotkey('ctrl', 'v')

    def escape(self):
        pyautogui.press('escape')

    def zoom_browser(self, direction):
        """Zoom in/out using Ctrl+Plus/Minus."""
        if direction == "in":
            pyautogui.hotkey('ctrl', 'plus')
        else:
            pyautogui.hotkey('ctrl', 'minus')

    def alt_tab(self):
        pyautogui.hotkey('alt', 'tab')

# -*- coding: utf-8 -*-
"""
CẤU HÌNH (CONFIGURATION) - AIR CONTROLLER
Giá trị được tải từ settings.json (nếu có) thông qua SettingsManager.
"""
from src.settings import SettingsManager

# Global settings instance
settings_mgr = SettingsManager()

# Default getter helper
def get(key):
    return settings_mgr.get(key)

# ================== MOUSE CONTROL (ĐIỀU KHIỂN CHUỘT) ==================
MOUSE_SPEED_NORMAL = get("mouse_speed_normal")
MOUSE_SPEED_FAST = get("mouse_speed_fast")
FAST_MOVE_THRESHOLD = get("fast_move_threshold")
DEAD_ZONE_RADIUS = get("dead_zone_radius")
SMOOTHING_FACTOR = get("smoothing_factor")

# ================== GESTURES (CỬ CHỈ) ==================
SCROLL_SENSITIVITY = get("scroll_sensitivity")
SCROLL_DEAD_ZONE = get("scroll_dead_zone")
SCROLL_MULTIPLIER = get("scroll_multiplier")

PINCH_THRESHOLD = get("pinch_threshold")

GESTURE_CONFIRM_FRAMES = get("gesture_confirm_frames")
ACTION_COOLDOWN = get("action_cooldown")

# New Gesture Params (Configurable)
SWIPE_WINDOW = get("swipe_window")
SWIPE_THRESHOLD = get("swipe_threshold")
ZOOM_THRESH = get("zoom_thresh")


# ================== CAMERA ==================
CAMERA_INDEX = get("camera_index")
MIN_DETECTION_CONFIDENCE = get("min_detection_confidence")
MIN_TRACKING_CONFIDENCE = get("min_tracking_confidence")

# ================== SMART MAGNET (HÚT CHUỘT) ==================
MAGNET_STRENGTH = get("magnet_strength") or 0.15
MAGNET_RADIUS = get("magnet_radius") or 50

# ================== ONE EURO FILTER (BỘ LỌC CHỐNG RUNG) ==================
OEF_MIN_CUTOFF = get("oef_min_cutoff")
OEF_BETA = get("oef_beta")
OEF_D_CUTOFF = get("oef_d_cutoff")

# ================== COLORS (MÀU SẮC HUD) ==================
COLOR_PAUSED = (0, 0, 255)       # Đỏ
COLOR_NAVIGATION = (0, 255, 0)   # Xanh lá
COLOR_INPUT = (0, 0, 255)        # Đỏ (Mic đang bật)
COLOR_MOUSE = (0, 255, 0)        # Xanh lá
COLOR_DRAGGING = (0, 255, 255)   # Vàng
COLOR_TEXT = (255, 255, 255)     # Trắng
COLOR_HUD_BG = (40, 40, 40)      # Xám tối

# Helper for PyInstaller path resolution
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ================== VOICE CONFIG (CẤU HÌNH GIỌNG NÓI) ==================
VOSK_MODEL_PATH = resource_path("vosk-model-small-en-us-0.15")
MIC_RATE = 16000

# ================== GESTURE CONFIG ==================
HAND_MODEL_PATH = resource_path("hand_landmarker.task")

# ================== VOICE COMMANDS (LỆNH GIỌNG NÓI) ==================
VOICE_COMMANDS = {
    "enter": ["enter", "submit", "go", "next line"],
    "tab": ["tab", "next field", "move on"],
    "delete": ["delete", "back", "backspace"],
    "clear": ["clear", "clear all", "erase"],
    "copy": ["copy"],
    "paste": ["paste"],
    "zoom_in": ["zoom in", "enlarge", "bigger"],
    "zoom_out": ["zoom out", "smaller", "shrink"],
    "scroll_up": ["scroll up", "go up", "page up"],
    "scroll_down": ["scroll down", "go down", "page down"],
    "escape": ["escape", "cancel", "close"],
    "system_off": ["system off", "exit", "quit"],
}


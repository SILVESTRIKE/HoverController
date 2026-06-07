import json
import os

SETTINGS_FILE = 'settings.json'

DEFAULT_SETTINGS = {
    # Mouse
    "mouse_speed_normal": 2.5,
    "mouse_speed_fast": 5.0,
    "fast_move_threshold": 0.03,
    "dead_zone_radius": 0.005,
    "smoothing_factor": 0.3,
    
    # Gestures
    "scroll_sensitivity": 80,
    "scroll_dead_zone": 0.01,
    "scroll_multiplier": 12,
    "pinch_threshold": 0.05,
    "gesture_confirm_frames": 2,
    "action_cooldown": 0.25,
    "swipe_window": 0.3,       # New swipe gesture
    "swipe_threshold": 0.25,   # New swipe gesture
    "zoom_thresh": 0.03,       # New zoom gesture

    # Camera
    "camera_index": 0,
    "min_detection_confidence": 0.7,
    "min_tracking_confidence": 0.7,
    
    # Filters
    "oef_min_cutoff": 0.5,
    "oef_beta": 0.5,
    "oef_d_cutoff": 1.0,

    # App
    "debug_mode": True,  # Default to showing camera
    
    # Smart Magnet
    "magnet_strength": 0.15,
    "magnet_radius": 50
}

class SettingsManager:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Update defaults with loaded values (keeps new defaults if JSON is old)
                    self.settings.update(loaded)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save(self):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key):
        return self.settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value

    def reset_defaults(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.save()

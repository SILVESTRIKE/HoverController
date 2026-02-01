# -*- coding: utf-8 -*-
from collections import deque
import time
from config import GESTURE_CONFIRM_FRAMES, ACTION_COOLDOWN


class StateManager:
    """
    Manages application state including mode switching between NAVIGATION and INPUT.
    """
    def __init__(self):
        # Primary mode: NAVIGATION (gesture control) or INPUT (voice input)
        self.mode = "NAVIGATION"
        
        # Gesture Debouncing
        self.gesture_buffer = deque(maxlen=GESTURE_CONFIRM_FRAMES)
        self.last_confirmed_gesture = "None"
        
        # Action Cooldown
        self.last_action_time = 0
        
        # Mouse tracking
        self.prev_pos = None
        self.dragging = False
        
        # Scroll state (for Fist pan)
        self.scroll_anchor = None
        
        # Voice feedback
        self.last_voice_text = ""
        self.voice_feedback_time = 0

    def update_gesture(self, raw_gesture):
        """
        Adds raw gesture to buffer and updates confirmed gesture if consistent.
        Returns True if a new consistent gesture is detected.
        """
        self.gesture_buffer.append(raw_gesture)
        
        if len(self.gesture_buffer) == GESTURE_CONFIRM_FRAMES:
            first = self.gesture_buffer[0]
            if all(x == first for x in self.gesture_buffer):
                if first != self.last_confirmed_gesture:
                    self.last_confirmed_gesture = first
                    return True
        return False

    def can_perform_action(self):
        return time.time() - self.last_action_time > ACTION_COOLDOWN

    def record_action(self):
        self.last_action_time = time.time()

    def set_mode(self, mode, voice_engine=None):
        """Switch between NAVIGATION and INPUT modes."""
        if mode not in ["NAVIGATION", "INPUT"]:
            return
            
        self.mode = mode
        
        # Sync voice engine mute state
        if voice_engine:
            voice_engine.set_mute(mode == "NAVIGATION")
        
        # Reset states on mode switch
        self.dragging = False
        self.scroll_anchor = None
        self.prev_pos = None
        
        print(f"Mode switched to: {mode}")

    def request_mode_switch(self, gesture, voice_engine=None):
        """
        Handle gesture-triggered mode switches.
        Returns True if mode was switched.
        """
        if self.mode == "NAVIGATION" and gesture in ["ThumbsUp", "Shaka"]:
            self.set_mode("INPUT", voice_engine)
            return True
        elif self.mode == "INPUT" and gesture == "Fist":
            self.set_mode("NAVIGATION", voice_engine)
            return True
        return False

    def set_voice_feedback(self, text):
        """Store last recognized voice text for HUD display."""
        self.last_voice_text = text
        self.voice_feedback_time = time.time()

    def get_voice_feedback(self):
        """Get voice feedback if recent (< 3 seconds)."""
        if time.time() - self.voice_feedback_time < 3.0:
            return self.last_voice_text
        return ""

    def reset(self):
        """Reset all tracking states (called when hand is lost)."""
        self.prev_pos = None
        self.dragging = False
        self.scroll_anchor = None
        self.gesture_buffer.clear()
        self.last_confirmed_gesture = "None"

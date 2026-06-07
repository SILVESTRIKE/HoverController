# -*- coding: utf-8 -*-
import cv2
from config import COLOR_NAVIGATION, COLOR_INPUT, COLOR_DRAGGING, COLOR_TEXT, COLOR_HUD_BG


class Visualizer:
    """
    Draws hand landmarks and HUD overlay on camera feed.
    """
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        # Hand connection definitions
        self.CONNECTIONS = [
            (0,1), (1,2), (2,3), (3,4),         # Thumb
            (0,5), (5,6), (6,7), (7,8),         # Index
            (5,9), (9,10), (10,11), (11,12),    # Middle
            (9,13), (13,14), (14,15), (15,16),  # Ring
            (13,17), (17,18), (18,19), (19,20), # Pinky
            (0,17)                              # Wrist
        ]

    def draw_landmarks(self, img, hand_landmarks):
        """Draw hand landmarks and connections."""
        if not hand_landmarks:
            return

        h, w, _ = img.shape
        
        # Convert to pixel coordinates
        points = []
        for lm in hand_landmarks:
            px = int(lm.x * w)
            py = int(lm.y * h)
            points.append((px, py))
            cv2.circle(img, (px, py), 4, (0, 0, 255), -1)

        # Draw connections
        for start_idx, end_idx in self.CONNECTIONS:
            if start_idx < len(points) and end_idx < len(points):
                cv2.line(img, points[start_idx], points[end_idx], (0, 255, 0), 2)

    def draw_hud(self, img, state_manager, gesture="None"):
        """Draw comprehensive HUD overlay."""
        h, w, _ = img.shape
        
        # Semi-transparent background bar at top
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, 60), COLOR_HUD_BG, -1)
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
        
        # Mode indicator (left)
        mode = state_manager.mode
        if mode == "NAVIGATION":
            mode_text = "NAVIGATION"
            mode_color = COLOR_NAVIGATION
            mic_status = "MIC OFF"
            mic_color = (100, 100, 100)
        else:
            mode_text = "INPUT"
            mode_color = COLOR_INPUT
            mic_status = "LISTENING..."
            mic_color = (0, 0, 255)
        
        cv2.putText(img, mode_text, (10, 25), self.font, 0.7, mode_color, 2)
        
        # Mic status (center-right area)
        cv2.putText(img, mic_status, (w - 180, 25), self.font, 0.6, mic_color, 2)
        
        # Gesture indicator (second row left)
        gesture_display = gesture.upper() if gesture != "None" else "--"
        cv2.putText(img, f"Gesture: {gesture_display}", (10, 50), self.font, 0.5, COLOR_TEXT, 1)
        
        # Dragging indicator
        if state_manager.dragging:
            cv2.putText(img, "DRAGGING", (w - 120, 50), self.font, 0.5, COLOR_DRAGGING, 2)
        
        # Voice feedback (bottom bar)
        voice_text = state_manager.get_voice_feedback()
        if voice_text:
            # Bottom bar
            cv2.rectangle(img, (0, h - 40), (w, h), COLOR_HUD_BG, -1)
            cv2.putText(img, f'Voice: "{voice_text}"', (10, h - 12), 
                       self.font, 0.6, (0, 255, 255), 1)

    def draw_scroll_indicator(self, img, scroll_delta):
        """Draw scroll direction indicator when scrolling."""
        dx, dy = scroll_delta
        if abs(dy) > 0.1:
            h, w, _ = img.shape
            center_x = w // 2
            center_y = h // 2
            
            # Draw arrow
            if dy > 0:  # Scrolling up
                cv2.arrowedLine(img, (center_x, center_y + 30), 
                              (center_x, center_y - 30), (0, 255, 255), 3)
            else:  # Scrolling down
                cv2.arrowedLine(img, (center_x, center_y - 30), 
                              (center_x, center_y + 30), (0, 255, 255), 3)

# -*- coding: utf-8 -*-
import mediapipe as mp
import numpy as np
import time
import os
import math
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from config import (
    MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE, 
    PINCH_THRESHOLD, OEF_MIN_CUTOFF, OEF_BETA, OEF_D_CUTOFF,
    SCROLL_DEAD_ZONE, SCROLL_MULTIPLIER
)


class OneEuroFilter:
    """
    One Euro Filter for smooth cursor movement.
    """
    def __init__(self, t0, x0, dx0=0.0, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.t_prev = t0
        self.x_prev = x0
        self.dx_prev = dx0
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff

    def smoothing_factor(self, t_e, cutoff):
        r = 2 * math.pi * cutoff * t_e
        return r / (r + 1)

    def exponential_smoothing(self, a, x, x_prev):
        return a * x + (1 - a) * x_prev

    def __call__(self, t, x):
        t_e = t - self.t_prev
        if t_e <= 0:
            return x

        a_d = self.smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = self.exponential_smoothing(a_d, dx, self.dx_prev)

        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self.smoothing_factor(t_e, cutoff)
        x_hat = self.exponential_smoothing(a, x, self.x_prev)

        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        return x_hat


class GestureEngine:
    """
    Processes hand landmarks and recognizes gestures.
    Supports two-hand tracking for zoom gestures.
    """
    def __init__(self, model_path='hand_landmarker.task'):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file '{model_path}' not found.")

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
            running_mode=vision.RunningMode.VIDEO
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        
        # OneEuroFilters for smooth cursor
        self.oef_x = None
        self.oef_y = None
        
        # Scroll/Pan anchor
        self.scroll_anchor = None
        
        # Two-hand zoom tracking
        self.prev_two_hand_distance = None
        
        # Swipe detection
        self.swipe_history = []  # List of (time, x_pos)
        self.SWIPE_WINDOW = 0.3  # Seconds
        self.SWIPE_THRESHOLD = 0.25  # Min distance to trigger swipe
        self.last_swipe_time = 0

    def process(self, img_rgb, timestamp_ms):
        """
        Process image and return gesture data.
        Returns: (gestures_list, landmarks_list, filtered_pointer, scroll_delta, special_action)
        special_action: "ZOOM_IN", "ZOOM_OUT", "SWIPE_LEFT", "SWIPE_RIGHT", or None
        """
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        detection_result = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        
        gestures = []
        multi_hand_landmarks = []
        filtered_pointer = None
        scroll_delta = (0, 0)
        special_action = None
        
        curr_time = timestamp_ms / 1000.0
        
        if detection_result.hand_landmarks:
            multi_hand_landmarks = detection_result.hand_landmarks
            num_hands = len(multi_hand_landmarks)
            
            # === TWO HAND GESTURES ===
            if num_hands == 2:
                hand1 = multi_hand_landmarks[0]
                hand2 = multi_hand_landmarks[1]
                
                gesture1, _ = self._analyze_hand(hand1)
                gesture2, _ = self._analyze_hand(hand2)
                
                # Calculate distance between hands (wrist to wrist)
                dist = self._dist(hand1[0], hand2[0])
                
                # Two fists = zoom gesture
                if gesture1 == "Fist" and gesture2 == "Fist":
                    if self.prev_two_hand_distance is not None:
                        dist_change = dist - self.prev_two_hand_distance
                        if dist_change > 0.03:  # Spreading apart
                            special_action = "ZOOM_IN"
                        elif dist_change < -0.03:  # Coming together
                            special_action = "ZOOM_OUT"
                    self.prev_two_hand_distance = dist
                    gestures.append("TwoHandZoom")
                else:
                    self.prev_two_hand_distance = None
                    # Use primary hand for single-hand gestures
                    primary_hand = hand1
                    gesture_name, fingers = self._analyze_hand(primary_hand)
                    gestures.append(gesture_name)
            
            # === SINGLE HAND GESTURES ===
            else:
                primary_hand = multi_hand_landmarks[0]
                gesture_name, fingers = self._analyze_hand(primary_hand)
                gestures.append(gesture_name)
                self.prev_two_hand_distance = None
            
            # Get primary hand for pointer/scroll
            primary_hand = multi_hand_landmarks[0]
            primary_gesture = gestures[0] if gestures else "None"
            
            index_tip = primary_hand[8]
            wrist = primary_hand[0]
            
            # Apply OneEuroFilter to index finger
            if self.oef_x is None:
                self.oef_x = OneEuroFilter(curr_time, index_tip.x, 
                                           min_cutoff=OEF_MIN_CUTOFF, 
                                           beta=OEF_BETA,
                                           d_cutoff=OEF_D_CUTOFF)
                self.oef_y = OneEuroFilter(curr_time, index_tip.y,
                                           min_cutoff=OEF_MIN_CUTOFF,
                                           beta=OEF_BETA,
                                           d_cutoff=OEF_D_CUTOFF)
                filtered_pointer = (index_tip.x, index_tip.y)
            else:
                x_smooth = self.oef_x(curr_time, index_tip.x)
                y_smooth = self.oef_y(curr_time, index_tip.y)
                filtered_pointer = (x_smooth, y_smooth)
            
            # Scroll logic using Fist pan
            if primary_gesture == "Fist":
                current_pos = (wrist.x, wrist.y)
                
                if self.scroll_anchor is None:
                    self.scroll_anchor = current_pos
                else:
                    scroll_delta = self._calculate_scroll_delta(current_pos, self.scroll_anchor)
                    self.scroll_anchor = current_pos
            else:
                self.scroll_anchor = None
            
            # === SWIPE DETECTION (for OpenHand) ===
            if primary_gesture == "OpenHand":
                # Track wrist position for swipe
                self.swipe_history.append((curr_time, wrist.x))
                
                # Clean old entries
                self.swipe_history = [(t, x) for t, x in self.swipe_history 
                                      if curr_time - t < self.SWIPE_WINDOW]
                
                # Check for swipe if we have enough history
                if len(self.swipe_history) >= 3 and curr_time - self.last_swipe_time > 0.5:
                    start_x = self.swipe_history[0][1]
                    end_x = self.swipe_history[-1][1]
                    dx = end_x - start_x
                    
                    if abs(dx) > self.SWIPE_THRESHOLD:
                        if dx > 0:
                            special_action = "SWIPE_RIGHT"
                        else:
                            special_action = "SWIPE_LEFT"
                        self.last_swipe_time = curr_time
                        self.swipe_history.clear()
            else:
                self.swipe_history.clear()
                
        else:
            self._reset_filters()
              
        return gestures, multi_hand_landmarks, filtered_pointer, scroll_delta, special_action

    def _calculate_scroll_delta(self, current_pos, anchor_pos):
        dx = current_pos[0] - anchor_pos[0]
        dy = current_pos[1] - anchor_pos[1]
        
        if abs(dx) < SCROLL_DEAD_ZONE:
            dx = 0
        if abs(dy) < SCROLL_DEAD_ZONE:
            dy = 0
            
        return (dx * SCROLL_MULTIPLIER, -dy * SCROLL_MULTIPLIER)

    def _reset_filters(self):
        self.oef_x = None
        self.oef_y = None
        self.scroll_anchor = None
        self.prev_two_hand_distance = None
        self.swipe_history.clear()

    def _get_finger_states(self, landmarks):
        fingers = []
        
        wrist = landmarks[0]
        pinky_mcp = landmarks[17]
        is_right = wrist.x < pinky_mcp.x
        
        # Thumb
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        if is_right:
            fingers.append(thumb_tip.x < thumb_ip.x)
        else:
            fingers.append(thumb_tip.x > thumb_ip.x)
            
        # Other 4 fingers
        for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
            fingers.append(landmarks[tip].y < landmarks[pip].y)
            
        return fingers

    def _dist(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def _analyze_hand(self, landmarks):
        fingers = self._get_finger_states(landmarks)
        thumb, index, middle, ring, pinky = fingers
        
        pinch_dist = self._dist(landmarks[4], landmarks[8])
        is_pinch = pinch_dist < PINCH_THRESHOLD
        
        # Fist: All fingers closed
        if not any(fingers[1:]):
            if not thumb or self._dist(landmarks[4], landmarks[6]) < 0.1:
                return "Fist", fingers

        # ThumbsUp: Only thumb open
        if thumb and not any(fingers[1:]):
            return "ThumbsUp", fingers
            
        # Shaka: Thumb + Pinky
        if thumb and pinky and not index and not middle and not ring:
            return "Shaka", fingers
            
        # Pointer: Only index finger
        if index and not middle and not ring and not pinky:
            return "Pointer", fingers
            
        # TwoFingers: Index + Middle
        if index and middle and not ring and not pinky:
            return "TwoFingers", fingers
            
        # Pinch: Thumb + Index close together
        if is_pinch:
            return "Pinch", fingers
            
        # OpenHand: All fingers open
        if all(fingers):
            return "OpenHand", fingers
            
        return "None", fingers

# -*- coding: utf-8 -*-
"""
PRESENTATION GOD - AirController + Voice
Hands-free presentation control: gesture navigation + offline voice commands.

Achieving "3 NOs": No Touch, No Delay, No Network Dependency.
"""
import cv2
import time
import numpy as np
import sys

from config import (
    CAMERA_INDEX, SCROLL_SENSITIVITY, 
    DEAD_ZONE_RADIUS, FAST_MOVE_THRESHOLD,
    MOUSE_SPEED_NORMAL, MOUSE_SPEED_FAST
)
from src.gesture_engine import GestureEngine
from src.voice_engine import VoiceEngine
from src.controller import SystemController
from src.state_manager import StateManager
from src.visualizer import Visualizer


def process_voice_command(cmd, controller, state):
    """Execute voice command through controller."""
    if cmd["type"] == "command":
        action = cmd["action"]
        
        if action == "enter":
            controller.press_enter()
        elif action == "tab":
            controller.press_tab()
        elif action == "delete":
            controller.press_backspace(5)
        elif action == "clear":
            controller.clear_field()
        elif action == "copy":
            controller.copy()
        elif action == "paste":
            controller.paste()
        elif action == "escape":
            controller.escape()
        elif action == "zoom_in":
            controller.zoom_browser("in")
        elif action == "zoom_out":
            controller.zoom_browser("out")
        elif action == "scroll_up":
            controller.scroll(SCROLL_SENSITIVITY)
        elif action == "scroll_down":
            controller.scroll(-SCROLL_SENSITIVITY)
        elif action == "system_off":
            return False  # Signal to exit
            
    elif cmd["type"] == "text":
        # Type the recognized text
        text = cmd["value"]
        controller.type_text(text)
    
    # Store for HUD display
    state.set_voice_feedback(cmd.get("value", cmd.get("action", "")))
    return True


def main():
    print("=" * 50)
    print("  PRESENTATION GOD - AirController + Voice")
    print("  Hands-Free Presentation Control System")
def run_controller(stop_event=None):
    """
    Main loop for AirController.
    :param stop_event: Threading event to signal stop.
    """
    from src.gesture_engine import GestureEngine
    from src.voice_engine import VoiceEngine
    from src.controller import SystemController
    from src.state_manager import StateManager
    from src.state_manager import StateManager
    from src.visualizer import Visualizer
    from src.smart_cursor import SmartCursor
    from config import (
        CAMERA_INDEX, GESTURE_CONFIRM_FRAMES, ACTION_COOLDOWN, 
        PINCH_THRESHOLD, settings_mgr, HAND_MODEL_PATH, MAGNET_RADIUS
    )

    # Initialize Modules
    print()
    print("Initializing AirController modules...")
    
    try:
        gesture_engine = GestureEngine(model_path=HAND_MODEL_PATH)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Download hand_landmarker.task from MediaPipe.")
        return
    
    voice_engine = VoiceEngine()
    controller = SystemController()
    state_manager = StateManager()
    visualizer = Visualizer()
    smart_cursor = SmartCursor(radius=MAGNET_RADIUS)
    
    state = state_manager # Alias
    
    # Start voice engine (runs on separate thread)
    if not voice_engine.start():
        print("WARNING: Voice engine failed to initialize. Voice commands disabled.")

    # Initialize Camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        return
    
    print("Ready! AirController is running...")
    
    pinch_start_time = None
    scroll_accumulator_y = 0
    scroll_accumulator_x = 0
    
    # Check debug mode from settings
    debug_mode = settings_mgr.get("debug_mode")
    
    try:
        # Loop until stop_event is set OR variable is False
        while True:
            if stop_event and stop_event.is_set():
                break

            success, img = cap.read()
            if not success:
                continue

            # Flip for mirror effect and convert to RGB
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            timestamp_ms = int(time.time() * 1000)
            
            # === GESTURE PROCESSING ===
            gestures, landmarks, filtered_pointer, scroll_delta, special_action = gesture_engine.process(img_rgb, timestamp_ms)
            
            current_gesture = gestures[0] if gestures else "None"
            primary_landmarks = landmarks[0] if landmarks else None
            
            # Update gesture state
            is_new_gesture = state.update_gesture(current_gesture)
            confirmed_gesture = state.last_confirmed_gesture
            
            # === MODE SWITCHING ===
            if is_new_gesture and state.can_perform_action():
                if state.request_mode_switch(confirmed_gesture, voice_engine):
                    state.record_action()
            
            # === NAVIGATION MODE ACTIONS ===
            if state.mode == "NAVIGATION" and primary_landmarks:
                # Pointer: Move mouse
                if confirmed_gesture == "Pointer" and filtered_pointer:
                    from config import (
                        MOUSE_SPEED_FAST, FAST_MOVE_THRESHOLD, 
                        MOUSE_SPEED_NORMAL, DEAD_ZONE_RADIUS,
                        MAGNET_STRENGTH, MAGNET_RADIUS
                    )
                    
                    # Calculate intended position
                    target_x, target_y = filtered_pointer
                    
                    # === SMART MAGNET LOGIC ===
                    # Get current mouse pos to check for elements
                    curr_mx, curr_my = controller.get_position()
                    
                    # Only check magnet if we are moving relatively slow (precision mode)
                    magnet_center = smart_cursor.get_magnet_target(curr_mx, curr_my)
                    
                    if magnet_center:
                        mcx, mcy = magnet_center
                        # Calculate distance to magnet center
                        dist_to_magnet = np.sqrt((curr_mx - mcx)**2 + (curr_my - mcy)**2)
                        
                        if dist_to_magnet < MAGNET_RADIUS:
                            # Apply gravity: Pull intended movement towards center
                            # We modify the *relative* movement logic indirectly or direct absolute
                            # Since we use relative movement for pointer, we add a "gravity vector"
                            
                            grav_x = (mcx - curr_mx) * MAGNET_STRENGTH
                            grav_y = (mcy - curr_my) * MAGNET_STRENGTH
                            
                            # Add gravity to pointer delta (experimental)
                            # But wait, filtered_pointer is normalized coords (0-1) from camera.
                            # We need to apply this to the dx/dy sent to controller.
                            pass # Logic continued below
                            
                    if state.prev_pos:
                        dx = filtered_pointer[0] - state.prev_pos[0]
                        dy = filtered_pointer[1] - state.prev_pos[1]
                        dist = np.sqrt(dx**2 + dy**2)
                        
                        if dist > DEAD_ZONE_RADIUS:
                            speed = MOUSE_SPEED_FAST if dist > FAST_MOVE_THRESHOLD else MOUSE_SPEED_NORMAL
                            
                            # Apply movement
                            controller.move_mouse_relative(dx, dy, speed)
                            
                            # Apply Magnet Correction if active
                            if magnet_center and dist < FAST_MOVE_THRESHOLD: # Only when moving slow
                                mcx, mcy = magnet_center
                                mx, my = controller.get_position()
                                # Pull towards center pixel-wise
                                grav_x = (mcx - mx) * MAGNET_STRENGTH
                                grav_y = (mcy - my) * MAGNET_STRENGTH
                                controller.move_mouse_pixels(grav_x, grav_y)
                    
                    state.prev_pos = filtered_pointer
                    if state.dragging:
                        controller.stop_drag()
                        state.dragging = False
                else:
                    state.prev_pos = None
                
                # TwoFingers: LEFT CLICK
                if confirmed_gesture == "TwoFingers" and is_new_gesture and state.can_perform_action():
                    controller.mouse_click("left")
                    state.record_action()
                
                # Pinch: Drag (hold) or Right Click (quick)
                if confirmed_gesture == "Pinch":
                    if pinch_start_time is None:
                        pinch_start_time = time.time()
                    
                    pinch_duration = time.time() - pinch_start_time
                    
                    if pinch_duration > PINCH_THRESHOLD and not state.dragging:
                        controller.start_drag()
                        state.dragging = True
                    
                    if state.dragging and filtered_pointer:
                        controller.move_mouse_absolute_normalized(filtered_pointer[0], filtered_pointer[1])
                        
                else:
                    if pinch_start_time is not None:
                        pinch_duration = time.time() - pinch_start_time
                        
                        if state.dragging:
                            controller.stop_drag()
                            state.dragging = False
                        elif pinch_duration < PINCH_THRESHOLD:
                            # Quick pinch = RIGHT CLICK
                            controller.mouse_click("right")
                        
                        pinch_start_time = None
                
                # OpenHand: Pan/Drag
                if confirmed_gesture == "OpenHand":
                    if not state.dragging:
                        controller.start_drag()
                        state.dragging = True
                    if filtered_pointer:
                        controller.move_mouse_absolute_normalized(filtered_pointer[0], filtered_pointer[1])
                elif state.dragging and confirmed_gesture != "Pinch":
                    controller.stop_drag()
                    state.dragging = False
                
                # Fist: Scroll
                if confirmed_gesture == "Fist":
                    from config import SCROLL_SENSITIVITY
                    dx, dy = scroll_delta
                    scroll_accumulator_y += dy
                    scroll_accumulator_x += dx
                    
                    if abs(scroll_accumulator_y) > 0.1:
                        scroll_amount_y = int(scroll_accumulator_y * SCROLL_SENSITIVITY)
                        if scroll_amount_y != 0:
                            controller.scroll(scroll_amount_y)
                            scroll_accumulator_y = 0

                    if abs(scroll_accumulator_x) > 0.1:
                        scroll_amount_x = int(scroll_accumulator_x * SCROLL_SENSITIVITY)
                        if scroll_amount_x != 0:
                            controller.scroll_horizontal(scroll_amount_x)
                            scroll_accumulator_x = 0
                else:
                    scroll_accumulator_y = 0
                    scroll_accumulator_x = 0
                
                # Special Actions
                if special_action:
                    if special_action == "ZOOM_IN":
                        controller.zoom_browser("in")
                    elif special_action == "ZOOM_OUT":
                        controller.zoom_browser("out")
                    elif special_action in ["SWIPE_LEFT", "SWIPE_RIGHT"]:
                        controller.alt_tab()
                        state.record_action()
            
            # === HANDLE NO HAND DETECTED ===
            if not primary_landmarks:
                if state.dragging:
                    controller.stop_drag()
                state.reset()

            # === INPUT MODE - VOICE PROCESSING ===
            if state.mode == "INPUT":
                cmd = voice_engine.get_command()
                if cmd:
                    if process_voice_command(cmd, controller, state) is False:
                        break # System Off command
            
            # === DRAW VISUALIZATION ===
            # Only draw if debug_mode is True
            if debug_mode:
                visualizer.draw_landmarks(img, primary_landmarks)
                visualizer.draw_hud(img, state, confirmed_gesture)
                
                cv2.imshow("PRESENTATION GOD", img)
                
                if cv2.waitKey(1) & 0xFF == 27: # ESC
                    break
            else:
                # Sleep to reduce CPU usage when not displaying window
                time.sleep(0.01)
                # Check exit condition if needed (e.g., system off voice command logic handled above)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        import traceback
        with open("error.log", "a") as f:
            f.write(f"\n[{time.ctime()}] CRITICAL ERROR:\n")
            traceback.print_exc(file=f)
        print(f"Error in main loop: {e}")
    finally:
        print("Stopping AirController...")
        if 'voice_engine' in locals():
            voice_engine.stop()
        if 'cap' in locals() and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()
        print("Clean exit!")



if __name__ == "__main__":
    # If run directly, run forever with debug mode forced (or from settings)
    run_controller()

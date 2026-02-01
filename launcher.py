import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sv_ttk  # You might need to install this for better looks, or stick to default
from src.settings import SettingsManager
from main import run_controller

class AirControllerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("PRESENTATION GOD - Config & Launcher")
        self.root.geometry("600x500")
        self.settings_mgr = SettingsManager()
        
        self.running = False
        self.thread = None
        self.stop_event = threading.Event()
        
        self.create_widgets()
        self.load_settings_to_ui()
        
        # Apply theme if available, otherwise default
        try:
            import sv_ttk
            sv_ttk.set_theme("dark")
        except ImportError:
            pass

    def create_widgets(self):
        # === TOP: STATUS & CONTROL ===
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill="x")
        
        self.status_label = ttk.Label(top_frame, text="Status: STOPPED", foreground="red", font=("Arial", 12, "bold"))
        self.status_label.pack(side="left")
        
        self.btn_run = ttk.Button(top_frame, text="START CONTROLLER", command=self.toggle_run)
        self.btn_run.pack(side="right")
        
        # === MIDDLE: TABS ===
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tab_general = ttk.Frame(self.notebook, padding=10)
        self.tab_gestures = ttk.Frame(self.notebook, padding=10)
        self.tab_scroll = ttk.Frame(self.notebook, padding=10)
        self.tab_magnet = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.tab_general, text="General")
        self.notebook.add(self.tab_gestures, text="Gestures")
        self.notebook.add(self.tab_scroll, text="Scrolling")
        self.notebook.add(self.tab_magnet, text="Smart Magnet")
        
        self.build_general_tab()
        self.build_gestures_tab()
        self.build_scroll_tab()
        self.build_magnet_tab()
        
        # === BOTTOM: SAVE ===
        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill="x")
        
        ttk.Button(bottom_frame, text="Save Settings", command=self.save_settings).pack(side="right")
        ttk.Button(bottom_frame, text="Reset Defaults", command=self.reset_defaults).pack(side="right", padx=5)

    def build_general_tab(self):
        # Mouse Speed Normal
        self.var_mouse_normal = self.create_slider(self.tab_general, "Mouse Speed (Normal)", 0.5, 5.0)
        # Mouse Speed Fast
        self.var_mouse_fast = self.create_slider(self.tab_general, "Mouse Speed (Fast)", 1.0, 10.0)
        # Smoothing
        self.var_smoothing = self.create_slider(self.tab_general, "Smoothing Factor (Low = Smooth)", 0.01, 1.0)
        # Camera Index
        self.var_camera = self.create_entry(self.tab_general, "Camera Index (0=Default)", int)
        # Debug Mode
        self.var_debug = tk.BooleanVar()
        chk = ttk.Checkbutton(self.tab_general, text="Debug Mode (Show Camera Window)", variable=self.var_debug)
        chk.pack(anchor="w", pady=5)

    def build_gestures_tab(self):
        # Pinch Threshold
        self.var_pinch = self.create_slider(self.tab_gestures, "Pinch Threshold (Higher = Easier Click)", 0.01, 0.1)
        # Cooldown
        self.var_cooldown = self.create_slider(self.tab_gestures, "Action Cooldown (seconds)", 0.1, 1.0)
        # Confirm Frames
        self.var_confirm = self.create_entry(self.tab_gestures, "Gesture Confirm Frames (Integer)", int)

    def build_scroll_tab(self):
        # Scroll Sensitivity
        self.var_scroll_sens = self.create_slider(self.tab_scroll, "Scroll Sensitivity", 10, 200)
        # Scroll Multiplier
        self.var_scroll_mult = self.create_slider(self.tab_scroll, "Scroll Multiplier", 1, 20)
        # Scroll Deadzone
        self.var_scroll_dead = self.create_slider(self.tab_scroll, "Scroll Deadzone", 0.001, 0.1)

    def build_magnet_tab(self):
        # Magnet Strength
        self.var_mag_strength = self.create_slider(self.tab_magnet, "Magnet Strength (Gravity Force)", 0.0, 1.0)
        # Magnet Radius
        self.var_mag_radius = self.create_slider(self.tab_magnet, "Magnet Radius (Pixels)", 10, 300)

    def create_slider(self, parent, label_text, min_val, max_val):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)
        ttk.Label(frame, text=label_text).pack(anchor="w")
        var = tk.DoubleVar()
        scale = ttk.Scale(frame, from_=min_val, to=max_val, variable=var, orient="horizontal")
        scale.pack(fill="x")
        # Label to show value
        lbl_val = ttk.Label(frame, text="0.0")
        lbl_val.pack(anchor="e")
        def update_lbl(*args):
            lbl_val.config(text=f"{var.get():.2f}")
        var.trace_add("write", update_lbl)
        return var

    def create_entry(self, parent, label_text, type_func=float):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)
        ttk.Label(frame, text=label_text).pack(anchor="w")
        var = tk.StringVar() # Use StringVar for Entry to avoid errors on empty
        entry = ttk.Entry(frame, textvariable=var)
        entry.pack(fill="x")
        return var

    def load_settings_to_ui(self):
        s = self.settings_mgr.settings
        
        self.var_mouse_normal.set(s.get("mouse_speed_normal", 2.5))
        self.var_mouse_fast.set(s.get("mouse_speed_fast", 5.0))
        self.var_smoothing.set(s.get("smoothing_factor", 0.3))
        self.var_camera.set(str(s.get("camera_index", 0)))
        self.var_debug.set(s.get("debug_mode", True))
        
        self.var_pinch.set(s.get("pinch_threshold", 0.05))
        self.var_cooldown.set(s.get("action_cooldown", 0.25))
        self.var_confirm.set(str(s.get("gesture_confirm_frames", 2)))
        
        self.var_scroll_sens.set(s.get("scroll_sensitivity", 80))
        self.var_scroll_mult.set(s.get("scroll_multiplier", 12))
        self.var_scroll_dead.set(s.get("scroll_dead_zone", 0.01))
        
        self.var_mag_strength.set(s.get("magnet_strength", 0.15))
        self.var_mag_radius.set(s.get("magnet_radius", 50))

    def save_settings(self):
        try:
            s = self.settings_mgr.settings
            s["mouse_speed_normal"] = self.var_mouse_normal.get()
            s["mouse_speed_fast"] = self.var_mouse_fast.get()
            s["smoothing_factor"] = self.var_smoothing.get()
            s["camera_index"] = int(self.var_camera.get())
            s["debug_mode"] = self.var_debug.get()
            
            s["pinch_threshold"] = self.var_pinch.get()
            s["action_cooldown"] = self.var_cooldown.get()
            s["gesture_confirm_frames"] = int(self.var_confirm.get())
            
            s["scroll_sensitivity"] = self.var_scroll_sens.get()
            s["scroll_multiplier"] = self.var_scroll_mult.get()
            s["scroll_dead_zone"] = self.var_scroll_dead.get()
            
            s["magnet_strength"] = self.var_mag_strength.get()
            s["magnet_radius"] = int(self.var_mag_radius.get())
            
            self.settings_mgr.save()
            messagebox.showinfo("Success", "Settings saved!")
        except ValueError:
             messagebox.showerror("Error", "Invalid numeric values entered.")

    def reset_defaults(self):
        if messagebox.askyesno("Confirm", "Reset all settings to default?"):
            self.settings_mgr.reset_defaults()
            self.load_settings_to_ui()

    def toggle_run(self):
        if not self.running:
            # Start
            self.save_settings() # Auto save before run
            self.running = True
            self.stop_event.clear()
            self.btn_run.config(text="STOP CONTROLLER")
            self.status_label.config(text="Status: RUNNING", foreground="green")
            
            self.thread = threading.Thread(target=self.run_process)
            self.thread.daemon = True
            self.thread.start()
        else:
            # Stop
            self.running = False
            self.stop_event.set()
            self.btn_run.config(text="START CONTROLLER")
            self.status_label.config(text="Status: STOPPING...", foreground="orange")
            # We don't join/block in GUI thread, just let it die

    def run_process(self):
        try:
            run_controller(self.stop_event)
        except Exception as e:
            print(f"Thread Error: {e}")
        finally:
            self.running = False
            # Update UI from thread safest way is polling or callbacks but for simplicity:
            # Note: This might crash if root is destroyed. Ideally use root.after
            pass
            
    def check_status(self):
        if not self.running and self.status_label.cget("text") == "Status: RUNNING":
             self.status_label.config(text="Status: STOPPED", foreground="red")
             self.btn_run.config(text="START CONTROLLER")
        self.root.after(1000, self.check_status)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AirControllerLauncher(root)
        app.check_status()
        root.mainloop()
    except Exception as e:
        import traceback
        with open("launcher_error.log", "a") as f:
            f.write(f"\n[{time.ctime()}] LAUNCHER ERROR:\n")
            traceback.print_exc(file=f)
        messagebox.showerror("Critical Error", f"Application crashed!\nCheck launcher_error.log\n\nError: {e}")


import uiautomation as auto
import threading
import time

class SmartCursor:
    """
    Handles "magnetic" cursor features using Windows UI Automation.
    Detects clickable elements under the cursor and provides "gravity" coordinates.
    """
    def __init__(self, radius=50):
        self.radius = radius
        self.last_element = None
        self.last_rect = None
        self.last_check_time = 0
        self.check_interval = 0.1  # Check 10 times per second max to save CPU
        self.target_center = None
        self.last_pos = (0, 0)
        
        # Types of controls to snap to
        self.interactive_types = [
            auto.ControlType.ButtonControl,
            auto.ControlType.HyperlinkControl,
            auto.ControlType.MenuItemControl,
            auto.ControlType.TabItemControl,
            auto.ControlType.CheckBoxControl,
            auto.ControlType.RadioButtonControl,
            auto.ControlType.ComboBoxControl,
            auto.ControlType.ListItemControl
        ]

    def get_magnet_target(self, x, y):
        """
        Check if (x, y) is over or near an interactive element.
        Returns (center_x, center_y) if found, else None.
        """
        now = time.time()
        # If mouse hasn't moved much, don't re-scan UI (expensive)
        dist_moved = ((x - self.last_pos[0])**2 + (y - self.last_pos[1])**2)**0.5
        
        if dist_moved < 5 and (now - self.last_check_time < self.check_interval * 5):
            return self.target_center

        self.last_check_time = now
        self.last_pos = (x, y)
        
        try:
            # Get element at cursor position
            # This is fast enough for checking "under" cursor
            element = auto.ControlFromPoint(int(x), int(y))
            
            if element:
                # Use ControlType propery access
                c_type = element.ControlType
                
                # If valid interactive element
                if c_type in self.interactive_types:
                    rect = element.BoundingRectangle
                    if rect.width() > 0 and rect.height() > 0:
                        cx = rect.left + rect.width() // 2
                        cy = rect.top + rect.height() // 2
                        self.target_center = (cx, cy)
                        return (cx, cy)
            
            # Reset if nothing found
            self.target_center = None
            return None
            
        except Exception:
            # Ignore UIA errors (can happen if window closes, permissions etc)
            return None

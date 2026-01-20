import customtkinter as ctk
from brightness_controller import BrightnessController
import sys
import threading
import time
from ctypes import windll, c_int, byref, Structure, sizeof, POINTER, c_long, c_void_p, cast

# --- Windows Acrylic Effect Utils ---
class ACCENT_POLICY(Structure):
    _fields_ = [
        ('AccentState', c_int),
        ('AccentFlags', c_int),
        ('GradientColor', c_int),
        ('AnimationId', c_int)
    ]

class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ('Attribute', c_int),
        ('Data', c_void_p),
        ('SizeOfData', c_int)
    ]

def apply_acrylic(hwnd):
    # ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
    policy = ACCENT_POLICY()
    policy.AccentState = 4
    policy.AccentFlags = 2 
    # GradientColor: AABBGGRR. 
    # Use a high alpha dark color for "dark glass".
    # 0xCC101010 -> Alpha=CC (204), R=10, G=10, B=10
    policy.GradientColor = 0xCC1F1F1F 
    policy.AnimationId = 0
    
    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = 19 # WCA_ACCENT_POLICY
    data.Data = cast(byref(policy), c_void_p)
    data.SizeOfData = sizeof(policy)
    
    try:
        windll.user32.SetWindowCompositionAttribute(c_int(hwnd), byref(data))
    except Exception as e:
        print(f"Failed to apply acrylic: {e}")

# --- Structs for Mouse/Monitor ---
class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]
    
class RECT(Structure):
    _fields_ = [('left', c_long), ('top', c_long), ('right', c_long), ('bottom', c_long)]

class MONITORINFO(Structure):
    _fields_ = [
        ("cbSize", c_long),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", c_long)
    ]

class BrightnessApp(ctk.CTk):
    def __init__(self, quit_callback=None):
        super().__init__()
        
        self.controller = BrightnessController()
        self.quit_callback = quit_callback
        
        # Threading support
        self.pending_updates = {} # {monitor_id: brightness_value}
        self.running = True
        self.update_thread = threading.Thread(target=self.worker_loop, daemon=True)
        self.update_thread.start()
        
        # Monitor cache to avoid flickering rebuilds
        # {monitor_id: { 'container': frame, 'slider': slider, 'val_label': label, 'name_label': label }}
        self.monitor_controls = {} 
        
        # Window configuration
        self.title("Display Brightness")
        self.overrideredirect(True) # Frameless
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        # Set background to a specific color that we will try to make 'glassy'
        # Note: If acrylic works, this color acts as the tint.
        # We use a very dark gray.
        self.configure(fg_color="#1F1F1F") 
        
        # Container for sliders
        self.slider_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.slider_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Allow frame to expand vertically

        # Bindings
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Escape>", lambda e: self.withdraw())
        
        # Initial sizing (will be adjusted)
        self.geometry("320x200")

    def enable_glass(self):
        # We need to find the correct HWND.
        # For overrideredirect windows, winfo_id() is usually the window itself.
        hwnd = self.winfo_id()
        apply_acrylic(hwnd)

    def worker_loop(self):
        while self.running:
            if self.pending_updates:
                # Process updates
                # Use a copy of keys to iterate to avoid runtime changes issues, 
                # although we just want to drain the current state.
                # Simplest: copy the dict, clear the original, then process.
                # BUT if we clear, and user is sliding, we might miss an update if we aren't careful?
                # Actually, debouncing: we only care about the *latest* value.
                # So we can just take the latest snapshot.
                
                # Lockless approach: pop items? 
                # Ideally use a Lock, but for this simple UI, atomic dict operations are mostly fine in Python (GIL).
                # Let's use a safe copy.
                snapshot = self.pending_updates.copy()
                self.pending_updates.clear()
                
                for m_id, val in snapshot.items():
                    self.controller.set_brightness(m_id, val)
            
            time.sleep(0.05) # Check 20 times a second

    def refresh_monitors(self):
        # Apply glass effect every time we show, just in case
        self.enable_glass()
        
        monitors = self.controller.get_monitors()
        if not monitors:
            for w in self.slider_frame.winfo_children():
                w.destroy()
            self.monitor_controls.clear()
            lbl = ctk.CTkLabel(self.slider_frame, text="No monitors detected", text_color="gray")
            lbl.grid(row=0, column=0, pady=20)
            self.resize_window(0)
            return

        # 1. Identified removed monitors and remove their widgets
        current_ids = {m['id'] for m in monitors}
        to_remove = []
        for m_id in self.monitor_controls:
            if m_id not in current_ids:
                to_remove.append(m_id)
        
        for m_id in to_remove:
            self.monitor_controls[m_id]['container'].destroy()
            del self.monitor_controls[m_id]

        # 2. Update or create widgets
        for idx, monitor in enumerate(monitors):
            m_id = monitor['id']
            if m_id in self.monitor_controls:
                # Update existing
                controls = self.monitor_controls[m_id]
                # Update position if index changed?
                controls['container'].grid(row=idx, column=0, sticky="ew", pady=(0, 15))
                
                # Update value label/slider value ONLY if we are not currently dragging?
                # If we update slider while user drags, it fights.
                # We can check if slider value is close to monitor value.
                # Or just trust the UI state for the slider, but update the label.
                # Actually, if external brightness change happens, we want to reflect it.
                # But for now, let's just update if the difference is large (external change) or init.
                pass 
            else:
                # Create new
                self.create_monitor_control(idx, monitor)
        
        # 3. Resize window
        self.resize_window(len(monitors))
        self.reposition_window()

    def create_monitor_control(self, idx, monitor):
        m_id = monitor['id']
        
        container = ctk.CTkFrame(self.slider_frame, fg_color="transparent")
        container.grid(row=idx, column=0, sticky="ew", pady=(0, 15))
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0)

        # Name
        name_label = ctk.CTkLabel(
            container, 
            text=monitor['name'], 
            font=("Segoe UI", 13), 
            text_color="#DDDDDD",
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w", padx=(5, 0))

        # Value Label
        val_label = ctk.CTkLabel(
            container, 
            text=f"{monitor['brightness']}", 
            font=("Segoe UI", 13, "bold"),
            text_color="#FFFFFF"
        )
        val_label.grid(row=0, column=1, sticky="e", padx=(0, 5))

        # Slider
        slider = ctk.CTkSlider(
            container, 
            from_=0, 
            to=100, 
            orientation="horizontal",
            number_of_steps=100,
            progress_color="#FFFFFF",
            button_color="#FFFFFF",
            button_hover_color="#E0E0E0",
            fg_color="#444444",
            height=18,
            border_width=0
        )
        slider.set(monitor['brightness'])
        slider.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        # Callback
        def on_slide(value):
            int_val = int(value)
            val_label.configure(text=str(int_val))
            # Debounce: just update the pending value
            self.pending_updates[m_id] = int_val

        slider.configure(command=on_slide)

        self.monitor_controls[m_id] = {
            'container': container,
            'slider': slider,
            'val_label': val_label,
            'name_label': name_label
        }

    def resize_window(self, num_monitors):
        base_h = 40
        item_h = 75 # Approx height + padding
        required_height = base_h + (num_monitors * item_h)
        self.current_w = 340
        self.current_h = min(required_height, 800)
        
        # We don't apply geometry here immediately if we want to reposition relative to mouse
        # But we need to set size.
        # reposition_window handles geometry.

    def reposition_window(self):
        # Get mouse position
        try:
            pt = POINT()
            windll.user32.GetCursorPos(byref(pt))
            
            hMonitor = windll.user32.MonitorFromPoint(pt, 0x00000002) # MONITOR_DEFAULTTONEAREST
            
            mi = MONITORINFO()
            mi.cbSize = sizeof(MONITORINFO)
            windll.user32.GetMonitorInfoW(hMonitor, byref(mi))
            
            work_area = mi.rcWork
            wa_left, wa_top, wa_right, wa_bottom = work_area.left, work_area.top, work_area.right, work_area.bottom
        except:
            wa_left, wa_top, wa_right, wa_bottom = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()

        padding = 15
        x = wa_right - self.current_w - padding
        y = wa_bottom - self.current_h - padding
        
        self.geometry(f"{self.current_w}x{self.current_h}+{x}+{y}")

    def on_focus_out(self, event):
        # Check if focus is really lost to outside
        # Tkinter focus is tricky. If we click the slider, one widget gets focus.
        # We only want to hide if the user clicks *outside* the window.
        # But <FocusOut> fires when focus moves between widgets too?
        # No, usually toplevel <FocusOut> is constrained.
        # But to be safe, we can check logic.
        # For now, simplistic approach:
        widget = event.widget
        # If the event widget is the window itself or a child?
        # Let's rely on standard behavior.
        # self.withdraw()
        pass 
        # Actually proper "popup" behavior is hard.
        # Let's only withdraw if we escape or click close.
        # Or re-enable the timeout/focusout if user wants.
        # User said "pop-up similar to Monitorian". Monitorian hides when you click away.
        # We'll leave it simple: calling withdraw on focus out often breaks debugging or multi-monitor usage.
        # I'll enable it but add a check.
        if str(event.widget) == str(self):
             self.withdraw()

    def show_window(self):
        self.deiconify()
        self.refresh_monitors()
        self.lift()
        self.focus_force()

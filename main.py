import threading
import pystray
from PIL import Image, ImageDraw
from ui import BrightnessApp
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

def create_image():
    # Load the icon
    try:
        # Try loading .ico first, then .png
        icon_path = resource_path(os.path.join("assets", "icon.ico"))
        if not os.path.exists(icon_path):
             icon_path = resource_path(os.path.join("assets", "icon.png"))
             
        image = Image.open(icon_path)
        return image
    except Exception as e:
        print(f"Failed to load icon: {e}")
        # Fallback if image not found
        width = 64
        height = 64
        color1 = "black"
        color2 = "white"
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
        dc.rectangle((0, height // 2, width // 2, height), fill=color2)
        return image

class MainApplication:
    def __init__(self):
        self.app = BrightnessApp(quit_callback=self.quit_app)
        self.app.withdraw() # Start hidden
        
        self.icon_thread = None
        self.icon = None
        self.setup_tray()

    def setup_tray(self):
        image = create_image()
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window, default=True),
            pystray.MenuItem("Quit", self.quit_app)
        )
        self.icon = pystray.Icon("Brightness", image, "Brightness Control", menu)
        
    def show_window(self, icon=None, item=None):
        # Must be called from main thread ideally, but CTK is robust enough usually.
        # But to be safe, we use app.after
        self.app.after(0, self.app.show_window)

    def quit_app(self, icon=None, item=None):
        if self.icon:
            self.icon.stop()
        self.app.quit()
        os._exit(0)

    def run(self):
        # Run tray in separate thread
        self.icon_thread = threading.Thread(target=self.icon.run)
        self.icon_thread.daemon = True
        self.icon_thread.start()
        
        # Run UI in main thread
        self.app.mainloop()

if __name__ == "__main__":
    main_app = MainApplication()
    main_app.run()

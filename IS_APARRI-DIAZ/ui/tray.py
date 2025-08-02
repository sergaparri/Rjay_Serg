import pystray
from PIL import Image, ImageDraw
from threading import Thread
import tkinter as tk

class SystemTrayIcon:
    def __init__(self, root: tk.Tk, app):
        self.root = root
        self.app = app
        self.icon = None
        self.menu = None
        self._setup_icon()

    def _setup_icon(self):
        # Create menu
        self.menu = pystray.Menu(
            pystray.MenuItem('Show', self.show_window),
            pystray.MenuItem('Hide', self.hide_window),
            pystray.MenuItem('Exit', self.exit_app)
        )

        # Create icon image
        image = Image.new('RGB', (64, 64), 'white')
        dc = ImageDraw.Draw(image)
        dc.rectangle([0, 0, 63, 63], fill='white')
        dc.ellipse([10, 10, 54, 54], fill='#4CAF50')
        dc.text((18, 22), "DFU", fill='white')

        # Create icon
        self.icon = pystray.Icon(
            "duplicate_file_utility",
            image,
            "Duplicate File Utility",
            self.menu
        )

    def show_window(self):
        self.root.after(0, self._show_window_handler)

    def _show_window_handler(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self):
        self.root.withdraw()

    def exit_app(self):
        self.icon.stop()
        self.root.quit()

    def run(self):
        # Start the icon in a separate thread
        Thread(target=self.icon.run, daemon=True).start() 
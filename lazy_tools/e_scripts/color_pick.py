"""
Screen Color Picker for Krita
Picks colors from anywhere on screen (including PureRef) with a global hotkey
"""

from krita import *
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QScreen, QColor, QCursor, QPainter, QPen
import sys

try:
    # For Windows global hotkey
    import ctypes
    from ctypes import wintypes

    WINDOWS_AVAILABLE = True
except:
    WINDOWS_AVAILABLE = False


class GlobalHotkeyThread(QThread):
    """Thread to listen for global hotkey on Windows"""

    color_pick_triggered = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True
        self.hotkey_id = 1

    def run(self):
        if not WINDOWS_AVAILABLE:
            return

        # Register hotkey: Win + Shift + C
        MOD_WIN = 0x0008
        MOD_SHIFT = 0x0004
        VK_C = 0x43

        user32 = ctypes.windll.user32

        # Register the hotkey
        if not user32.RegisterHotKey(None, self.hotkey_id, MOD_WIN | MOD_SHIFT, VK_C):
            print("Failed to register hotkey. Try a different combination.")
            return

        print("Global hotkey registered: Win+Shift+C")

        try:
            # Message loop
            msg = wintypes.MSG()
            while (
                self.running and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0
            ):
                if msg.message == 0x0312:  # WM_HOTKEY
                    self.color_pick_triggered.emit()
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            # Unregister hotkey
            user32.UnregisterHotKey(None, self.hotkey_id)
            print("Global hotkey unregistered")

    def stop(self):
        self.running = False
        if WINDOWS_AVAILABLE:
            # Post quit message to exit the message loop
            ctypes.windll.user32.PostThreadMessageW(self.ident, 0x0012, 0, 0)  # WM_QUIT


class ScreenColorPicker(Extension):

    def __init__(self, parent):
        super().__init__(parent)
        self.hotkey_thread = None
        self.picking = False

    def setup(self):
        """Called when Krita starts"""
        # Start global hotkey listener
        self.start_hotkey_listener()

    def createActions(self, window):
        """Create menu actions"""
        action = window.createAction(
            "screen_color_picker", "Pick Color from Screen", "tools/scripts"
        )
        action.setToolTip("Pick color from anywhere on screen (Win+Shift+C)")
        action.triggered.connect(self.capture_color_at_cursor)

    def start_hotkey_listener(self):
        """Start listening for global hotkey"""
        if WINDOWS_AVAILABLE and self.hotkey_thread is None:
            self.hotkey_thread = GlobalHotkeyThread()
            self.hotkey_thread.color_pick_triggered.connect(
                self.capture_color_at_cursor
            )
            self.hotkey_thread.start()
        elif not WINDOWS_AVAILABLE:
            print(
                "Global hotkey only available on Windows. Use Tools > Scripts > Pick Color from Screen"
            )

    def capture_color_at_cursor(self):
        """Capture color at current cursor position"""
        try:
            # Get cursor position
            cursor_pos = QCursor.pos()

            # Capture screen at cursor position
            screen = QApplication.primaryScreen()
            pixmap = screen.grabWindow(0, cursor_pos.x(), cursor_pos.y(), 1, 1)

            # Get color from the pixel
            image = pixmap.toImage()
            qcolor = QColor(image.pixel(0, 0))

            # Convert to Krita ManagedColor
            color = ManagedColor("RGBA", "U8", "")
            components = color.components()
            components[0] = qcolor.blue() / 255.0
            components[1] = qcolor.green() / 255.0
            components[2] = qcolor.red() / 255.0
            components[3] = 1.0
            color.setComponents(components)

            # Set as foreground color
            view = Krita.instance().activeWindow().activeView()
            if view:
                view.setForeGroundColor(color)
                print(
                    f"Color picked: RGB({qcolor.red()}, {qcolor.green()}, {qcolor.blue()})"
                )
            else:
                print("No active view found")

        except Exception as e:
            print(f"Error picking color: {e}")
        finally:
            self.picking = False

    def __del__(self):
        """Cleanup when extension is destroyed"""
        if self.hotkey_thread:
            self.hotkey_thread.stop()
            self.hotkey_thread.wait()

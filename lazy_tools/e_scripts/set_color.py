from krita import Krita, Extension, ManagedColor
from lazy_tools.config.config_loader import get_foreground_color


def set_foreground_color(color_getter):
    """Set foreground color using the provided color getter function"""
    app = Krita.instance()
    view = app.activeWindow().activeView()
    if view:
        doc = app.activeDocument()
        color_data = color_getter()
        color = ManagedColor("RGBA", "U8", doc.colorProfile())
        # setComponents order is B, G, R, A
        color.setComponents(
            [
                color_data["b"] / 255,
                color_data["g"] / 255,
                color_data["r"] / 255,
                color_data["a"] / 255,
            ]
        )
        view.setForeGroundColor(color)


def create_set_color_extension(color_num):
    """Factory function to create SetForegroundColor extension classes"""

    class SetForegroundColorExtension(Extension):
        def __init__(self, parent):
            super().__init__(parent)

        def setup(self):
            pass

        def createActions(self, window):
            action = window.createAction(
                f"set_foreground_color{color_num}",
                f"Set Foreground Color{color_num}",
                "tools/scripts",
            )
            action.triggered.connect(
                lambda: set_foreground_color(lambda: get_foreground_color(color_num))
            )

    return SetForegroundColorExtension


# Create extension classes for colors 1-9
SetForegroundColor1 = create_set_color_extension(1)
SetForegroundColor2 = create_set_color_extension(2)
SetForegroundColor3 = create_set_color_extension(3)
SetForegroundColor4 = create_set_color_extension(4)
SetForegroundColor5 = create_set_color_extension(5)
SetForegroundColor6 = create_set_color_extension(6)
SetForegroundColor7 = create_set_color_extension(7)
SetForegroundColor8 = create_set_color_extension(8)
SetForegroundColor9 = create_set_color_extension(9)

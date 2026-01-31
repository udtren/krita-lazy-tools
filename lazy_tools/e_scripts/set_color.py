from krita import *
from lazy_tools.config.config_loader import (
    get_foreground_color1,
    get_foreground_color2,
    get_foreground_color3,
)


def set_foreground_color1():
    app = Krita.instance()
    view = app.activeWindow().activeView()
    if view:
        doc = app.activeDocument()
        color1 = get_foreground_color1()
        color = ManagedColor("RGBA", "U8", doc.colorProfile())
        # setComponents order is B, G, R, A
        color.setComponents(
            [
                color1["b"] / 255,
                color1["g"] / 255,
                color1["r"] / 255,
                color1["a"] / 255,
            ]
        )
        view.setForeGroundColor(color)


def set_foreground_color2():
    app = Krita.instance()
    view = app.activeWindow().activeView()
    if view:
        doc = app.activeDocument()
        color2 = get_foreground_color2()
        color = ManagedColor("RGBA", "U8", doc.colorProfile())
        # setComponents order is B, G, R, A
        color.setComponents(
            [
                color2["b"] / 255,
                color2["g"] / 255,
                color2["r"] / 255,
                color2["a"] / 255,
            ]
        )
        view.setForeGroundColor(color)


def set_foreground_color3():
    app = Krita.instance()
    view = app.activeWindow().activeView()
    if view:
        doc = app.activeDocument()
        color3 = get_foreground_color3()
        color = ManagedColor("RGBA", "U8", doc.colorProfile())
        # setComponents order is B, G, R, A
        color.setComponents(
            [
                color3["b"] / 255,
                color3["g"] / 255,
                color3["r"] / 255,
                color3["a"] / 255,
            ]
        )
        view.setForeGroundColor(color)


class SetForegroundColor1(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        """Create menu actions"""
        action = window.createAction(
            "set_foreground_color1",
            "Set Foreground Color1",
            "tools/scripts",
        )
        action.triggered.connect(lambda: set_foreground_color1())


class SetForegroundColor2(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        """Create menu actions"""
        action = window.createAction(
            "set_foreground_color2",
            "Set Foreground Color2",
            "tools/scripts",
        )
        action.triggered.connect(lambda: set_foreground_color2())


class SetForegroundColor3(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        """Create menu actions"""
        action = window.createAction(
            "set_foreground_color3",
            "Set Foreground Color3",
            "tools/scripts",
        )
        action.triggered.connect(lambda: set_foreground_color3())

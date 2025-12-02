from krita import *


def deselect_alternative():
    doc = Krita.instance().activeDocument()

    deselect_action = Krita.instance().action("deselect")

    if deselect_action:
        deselect_action.trigger()

    switch_brush_action = Krita.instance().action("KritaShape/KisToolBrush")

    if switch_brush_action:
        switch_brush_action.trigger()

    doc.refreshProjection()


class DeselectAlternative(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        """Create menu actions"""
        action = window.createAction(
            "deselect_alternative", "Deselect Alternative", "tools/scripts"
        )
        action.triggered.connect(lambda: deselect_alternative())

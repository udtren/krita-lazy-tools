from krita import *
from datetime import datetime


def create_selection_mask_alt():
    app = Krita.instance()
    doc = app.activeDocument()

    if not doc:
        return

    # Check if "selection_mask_group" exists
    selection_mask_group = doc.nodeByName("Selection_Mask_Group")

    if not selection_mask_group:
        # Create the group layer
        selection_mask_group = doc.createGroupLayer("Selection_Mask_Group")

        # Add it as the last (bottom) node of the root node
        # Pass the first child as the second parameter to position it at the bottom
        first_child = (
            doc.rootNode().childNodes()[0] if doc.rootNode().childNodes() else None
        )
        doc.rootNode().addChildNode(selection_mask_group, first_child)

        # Set visibility to false
        selection_mask_group.setVisible(False)

    # Get the current selection from the document
    selection = doc.selection()

    if not selection:
        # If there's no active selection, we can't create a meaningful selection mask
        return

    # Create selection mask with timestamp name
    current_time = datetime.now().strftime("%H%M%S")
    mask_name = f"selection_mask_{current_time}"

    # Create the selection mask
    selection_mask = doc.createSelectionMask(mask_name)

    # Set the selection data to the mask
    selection_mask.setSelection(selection)

    # Add the selection mask to the group
    selection_mask_group.addChildNode(selection_mask, None)

    deselect_action = Krita.instance().action("deselect")

    if deselect_action:
        deselect_action.trigger()

    # Refresh the document
    doc.refreshProjection()


class CreateSelectionMaskAlternative(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        """Create menu actions"""
        action = window.createAction(
            "create_selection_mask_alternative",
            "Create Selection Mask Alternative",
            "tools/scripts",
        )
        action.triggered.connect(lambda: create_selection_mask_alt())

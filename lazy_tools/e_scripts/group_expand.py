from krita import *


def expand_all_groups(expand=True):
    """
    Fold or expand all layer groups in the active document.

    Args:
        expand: True to expand all groups, False to collapse all groups
    """
    doc = Krita.instance().activeDocument()
    if not doc:
        return

    def process_node(node):
        """Recursively process nodes and toggle group layers"""
        if node.type() == "grouplayer":
            node.setCollapsed(not expand)

        # Process children
        for child in node.childNodes():
            process_node(child)

    # Start from root node
    root = doc.rootNode()
    for child in root.childNodes():
        process_node(child)

    # Refresh the layer docker to show changes
    doc.refreshProjection()


class ExpandAllGroups(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        """Create menu actions"""
        action = window.createAction(
            "expand_all_folders", "Expand All Folders", "tools/scripts"
        )
        action.triggered.connect(lambda: expand_all_groups(expand=True))

from krita import *


def folder_all_groups(expand=False):
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


class FolderAllGroups(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        """Create menu actions"""
        action = window.createAction(
            "folder_all_folder", "Fold All Folders", "tools/scripts"
        )
        action.triggered.connect(lambda: folder_all_groups(expand=False))

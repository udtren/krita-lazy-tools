from krita import *
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QApplication,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QCursor
import os
import sys

# Add parent directory to path to import from lazy_tools
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.config_loader import load_name_color_list
from utils.color_scheme import ColorScheme


class RenameDialog(QDialog):
    """Dialog for renaming layers using predefined name/color list"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename Layer")
        self.setMinimumSize(300, 400)
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()

        # Create list widget
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)

        # Load and parse name color list
        content = load_name_color_list()
        if content:
            lines = content.strip().split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Parse line: "layer_name" or "layer_name, Color"
                name = line
                color_name = None

                if "," in line:
                    parts = line.split(",", 1)
                    name = parts[0].strip()
                    color_name = parts[1].strip() if len(parts) > 1 else None

                # Create list item
                item = QListWidgetItem()
                item.setData(Qt.UserRole, name)
                item.setData(Qt.UserRole + 1, color_name)

                # Set display text and icon
                if color_name:
                    # Find color index from color name
                    color_index = self.get_color_index(color_name)
                    if color_index > 0:
                        # Create color icon
                        color = ColorScheme.COLORS.get(color_index)
                        if color:
                            pixmap = QPixmap(14, 14)
                            pixmap.fill(color)
                            item.setIcon(QIcon(pixmap))

                    item.setText(name)
                else:
                    item.setText(name)

                self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def get_color_index(self, color_name):
        """Get color index from color name

        Args:
            color_name (str): Color name (e.g., "Blue", "Red", "blue", "red")

        Returns:
            int: Color index (0-8), 0 if not found
        """
        if not color_name:
            return 0

        # Normalize color name: capitalize first letter
        normalized_name = color_name.strip().capitalize()

        color_map = {
            "Blue": 1,
            "Green": 2,
            "Yellow": 3,
            "Orange": 4,
            "Brown": 5,
            "Red": 6,
            "Purple": 7,
            "Grey": 8,
        }
        return color_map.get(normalized_name, 0)

    def on_item_clicked(self, item):
        """Handle item click - rename active layer

        Args:
            item (QListWidgetItem): Clicked item
        """
        name = item.data(Qt.UserRole)
        color_name = item.data(Qt.UserRole + 1)

        # Get active document and node
        app = Krita.instance()
        doc = app.activeDocument()

        if not doc:
            return

        active_node = doc.activeNode()
        if not active_node:
            return

        # Set layer name
        if name:
            active_node.setName(name)

        # Set color label
        # If color is specified, use that color
        # If no color specified, set to 0 (None/Transparent)
        if color_name:
            color_index = self.get_color_index(color_name)
        else:
            color_index = 0  # None/Transparent

        active_node.setColorLabel(color_index)

        # Close dialog after renaming
        self.accept()


def rename_alt():
    """Show rename dialog at mouse cursor position"""
    dialog = RenameDialog()

    # Get current mouse cursor position
    cursor_pos = QCursor.pos()

    # Move dialog to cursor position
    dialog.move(cursor_pos)

    dialog.exec_()


class RenameAlternative(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        """Create menu actions"""
        action = window.createAction(
            "rename_alternative",
            "Rename Alternative",
            "tools/scripts",
        )
        action.triggered.connect(lambda: rename_alt())

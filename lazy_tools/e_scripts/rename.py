from krita import *
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QApplication,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QPushButton,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QCursor, QColor
import os
import sys

try:
    from quick_access_manager.gesture.gesture_main import (
        pause_gesture_event_filter,
        resume_gesture_event_filter,
        is_gesture_filter_paused,
    )

    GESTURE_AVAILABLE = True
except ImportError:
    GESTURE_AVAILABLE = False

# Add parent directory to path to import from lazy_tools
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.config_loader import load_name_color_list, save_name_color_list
from ..utils.color_scheme import ColorScheme


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

        # Manual input section
        manual_layout = QHBoxLayout()

        # Color combo box with icons only (no text)
        self.color_combo = QComboBox()

        # Add None/Transparent with white icon
        white_pixmap = QPixmap(14, 14)
        white_pixmap.fill(QColor(255, 255, 255))
        self.color_combo.addItem(QIcon(white_pixmap), "")
        self.color_combo.setItemData(0, "None/Transparent", Qt.UserRole)

        # Add colors with icons only
        color_items = [
            ("Blue", 1),
            ("Green", 2),
            ("Yellow", 3),
            ("Orange", 4),
            ("Brown", 5),
            ("Red", 6),
            ("Purple", 7),
            ("Grey", 8),
        ]

        for idx, (color_name, color_index) in enumerate(color_items, start=1):
            color = ColorScheme.COLORS.get(color_index)
            if color:
                pixmap = QPixmap(14, 14)
                pixmap.fill(color)
                self.color_combo.addItem(QIcon(pixmap), "")
                self.color_combo.setItemData(idx, color_name, Qt.UserRole)

        manual_layout.addWidget(self.color_combo)

        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Layer name")
        manual_layout.addWidget(self.name_input)

        # Save checkbox
        self.save_checkbox = QCheckBox("Save")
        manual_layout.addWidget(self.save_checkbox)

        layout.addLayout(manual_layout)

        # Button layout
        button_layout = QHBoxLayout()

        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.on_manual_ok)
        button_layout.addWidget(ok_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

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

    def on_manual_ok(self):
        """Handle manual OK button - rename layer with manual input"""
        # Get manual input values
        name = self.name_input.text().strip()
        # Get color name from UserRole data
        color_text = self.color_combo.currentData(Qt.UserRole)
        should_save = self.save_checkbox.isChecked()

        # Validate name
        if not name:
            return

        # Get color index
        if color_text == "None/Transparent":
            color_index = 0
        else:
            color_index = self.get_color_index(color_text)

        # Get active document and node
        app = Krita.instance()
        doc = app.activeDocument()

        if not doc:
            return

        active_node = doc.activeNode()
        if not active_node:
            return

        # Set layer name and color
        active_node.setName(name)
        active_node.setColorLabel(color_index)

        # Save to config if checkbox is checked
        if should_save:
            # Load current content
            content = load_name_color_list()
            lines = content.strip().split("\n") if content else []

            # Create new line
            if color_text == "None/Transparent":
                new_line = name
            else:
                new_line = f"{name}, {color_text}"

            # Add new line if not already exists
            if new_line not in lines:
                lines.append(new_line)

            # Save updated content
            updated_content = "\n".join(lines)
            save_name_color_list(updated_content)

        # Close dialog
        self.accept()


def rename_alt():
    """Show rename dialog at mouse cursor position"""
    # Pause gesture if available and not already paused
    should_resume_gesture = False
    if GESTURE_AVAILABLE and not is_gesture_filter_paused():
        pause_gesture_event_filter()
        should_resume_gesture = True

    dialog = RenameDialog()

    # Get current mouse cursor position
    cursor_pos = QCursor.pos()

    # Move dialog to cursor position
    dialog.move(cursor_pos)

    dialog.exec_()

    # Resume gesture if we paused it
    if should_resume_gesture:
        resume_gesture_event_filter()


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

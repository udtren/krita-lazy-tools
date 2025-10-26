"""
Color Filter Widgets for Lazy Tools Docker

This module contains widgets for color-based layer filtering with visibility and opacity controls.
"""

from typing import Dict
from krita import Krita, Node  # type: ignore
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from lazy_tools.utils.color_scheme import ColorScheme


class ColorFilterSection(QWidget):
    """
    A widget containing all color filter rows.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_docker = parent
        self.color_rows: Dict[int, "ColorFilterRow"] = {}
        self.setup_ui()

    def setup_ui(self):
        """Setup the color filter section UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # Create rows for each color (excluding transparent/none)
        color_names = [
            "Blue",
            "Green",
            "Yellow",
            "Orange",
            "Brown",
            "Red",
            "Purple",
            "Grey",
        ]

        for i, name in enumerate(color_names, start=1):
            color = ColorScheme.COLORS[i]
            color_row = ColorFilterRow(i, name, color, self.parent_docker)
            self.color_rows[i] = color_row
            layout.addWidget(color_row)

        self.setLayout(layout)


class ColorFilterRow(QWidget):
    """
    A row widget containing color icon, toggle button, and opacity buttons for a specific color.
    """

    def __init__(self, color_index: int, color_name: str, color: QColor, parent=None):
        super().__init__(parent)
        self.color_index = color_index
        self.color_name = color_name
        self.color = color
        self.parent_docker = parent

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components for this color row."""
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Toggle visibility button
        self.toggle_button = QPushButton("👁")
        self.toggle_button.setFixedSize(30, 25)
        self.toggle_button.setStyleSheet(
            """
            QPushButton {
                background-color: #191919;
            }
            QPushButton:hover {
                background-color: #393939;
            }
        """
        )
        self.toggle_button.clicked.connect(self.toggle_visibility)
        layout.addWidget(self.toggle_button)

        # Color icon label
        self.color_icon = QLabel()
        self.color_icon.setFixedSize(20, 20)
        color_pixmap = QPixmap(20, 20)
        color_pixmap.fill(self.color)
        self.color_icon.setPixmap(color_pixmap)
        self.color_icon.setToolTip(f"Color: {self.color_name}")
        layout.addWidget(self.color_icon)

        self.opacity_buttons = {}
        opacity_values = [10, 25, 50, 75, 100]

        for opacity in opacity_values:
            btn = QPushButton(str(opacity))
            btn.setFixedSize(25, 25)
            btn.clicked.connect(lambda checked, op=opacity: self.set_opacity(op))
            self.opacity_buttons[opacity] = btn
            layout.addWidget(btn)

        # Add stretch to push everything to the left
        layout.addStretch()

        self.setLayout(layout)

    def toggle_visibility(self):
        """Toggle visibility of all layers with this color label."""
        try:
            doc = Krita.instance().activeDocument()
            if doc:
                root_node = doc.rootNode()
                self._toggle_layers_recursive(root_node)
                doc.refreshProjection()
        except Exception as e:
            print(f"Error toggling visibility for {self.color_name}: {e}")

    def set_opacity(self, opacity_percent: int):
        """Set opacity of all layers with this color label."""
        try:
            doc = Krita.instance().activeDocument()
            if doc:
                root_node = doc.rootNode()
                # Convert percentage to 0-255 range
                opacity_value = int((opacity_percent / 100.0) * 255)
                self._set_layers_opacity_recursive(root_node, opacity_value)
                doc.refreshProjection()
                print(f"Set {self.color_name} layers opacity to {opacity_percent}%")
        except Exception as e:
            print(f"Error setting opacity for {self.color_name}: {e}")

    def _toggle_layers_recursive(self, node: Node):
        """Recursively toggle visibility of layers with the target color label."""
        if not node:
            return

        # Don't process the root node
        if node.type() == "grouplayer" and node.parentNode() is None:
            for child in node.childNodes():
                self._toggle_layers_recursive(child)
            return

        # Check if this layer has the target color label
        if node.type() in ["paintlayer", "grouplayer", "vectorlayer", "filterlayer"]:
            layer_color = node.colorLabel()

            if layer_color == self.color_index:
                # Toggle visibility using Krita's built-in action
                self._toggle_node_visibility(node)

        # Process child nodes
        for child in node.childNodes():
            self._toggle_layers_recursive(child)

    def _set_layers_opacity_recursive(self, node: Node, opacity_value: int):
        """Recursively set opacity of layers with the target color label."""
        if not node:
            return

        # Don't process the root node
        if node.type() == "grouplayer" and node.parentNode() is None:
            for child in node.childNodes():
                self._set_layers_opacity_recursive(child, opacity_value)
            return

        # Check if this layer has the target color label
        try:
            layer_color = node.colorLabel()

            if layer_color == self.color_index:
                node.setOpacity(opacity_value)
        except Exception as e:
            print(f"Error setting opacity for {node.name()}: {e}")

        # Process child nodes
        for child in node.childNodes():
            self._set_layers_opacity_recursive(child, opacity_value)

    def _toggle_node_visibility(self, node: Node):
        """Toggle node visibility using Krita's built-in action."""
        try:
            window = Krita.instance().activeWindow()
            if not window:
                return

            view = window.activeView()
            if not view:
                return

            # Select the target node first
            view.setCurrentNode(node)

            # Use Krita's built-in toggle display selection action
            window.action("toggle_display_selection").trigger()

        except Exception as e:
            print(f"Error toggling node visibility: {e}")
            # Fallback to manual visibility toggle
            current_visibility = node.visible()
            node.setVisible(not current_visibility)

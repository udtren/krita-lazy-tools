from typing import Dict
from krita import Krita, Node  # type: ignore
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QColor
from lazy_tools.utils.color_scheme import ColorScheme

# from lazy_tools.utils.logs import write_log


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

        # Create ColorFilterRow widgets
        color_rows_list = []
        for i, name in enumerate(color_names, start=1):
            color = ColorScheme.COLORS[i]
            color_row = ColorFilterRow(i, name, color, self.parent_docker)
            self.color_rows[i] = color_row
            color_rows_list.append(color_row)

        # First row: 3 columns (Blue, Green, Yellow)
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(3)
        for color_row in color_rows_list[0:3]:
            row1_layout.addWidget(color_row)
        row1_layout.addStretch()
        layout.addLayout(row1_layout)

        # Second row: 3 columns (Orange, Brown, Red)
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(3)
        for color_row in color_rows_list[3:6]:
            row2_layout.addWidget(color_row)
        row2_layout.addStretch()
        layout.addLayout(row2_layout)

        # Third row: 2 columns (Purple, Grey)
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(3)
        for color_row in color_rows_list[6:8]:
            row3_layout.addWidget(color_row)
        row3_layout.addStretch()
        layout.addLayout(row3_layout)

        # Add vertical stretch to push everything to the top
        layout.addStretch()

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
        self.color_icon.mousePressEvent = self.on_label_clicked
        layout.addWidget(self.color_icon)
        layout.addStretch()

        self.setLayout(layout)

        # Set fixed width to ensure consistent alignment across rows
        self.setFixedWidth(60)

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

    def on_label_clicked(self, event):
        """Handle clicks on the label: Shift+click shows opacity popup, Ctrl+right click removes."""
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QCursor

        try:
            # Check if it's Shift+click
            if event.modifiers() & Qt.ShiftModifier:
                # Show opacity popup at cursor position
                cursor_pos = QCursor.pos()
                self.opacity_popup = OpacityPopup(self, cursor_pos)
                self.opacity_popup.show()
        except Exception as e:
            print(f"Error handling label click: {e}")

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


class OpacityPopup(QWidget):
    """Popup window that shows opacity buttons and auto-closes after 3 seconds."""

    def __init__(self, parent_row, cursor_pos):
        super().__init__(None)  # No parent to make it a top-level window
        self.parent_row = parent_row
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Setup UI
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        opacity_values = [10, 25, 50, 75, 100]

        for opacity in opacity_values:
            btn = QPushButton(str(opacity))
            btn.setFixedSize(40, 30)
            btn.clicked.connect(lambda checked, op=opacity: self.on_opacity_clicked(op))
            layout.addWidget(btn)

        self.setLayout(layout)

        # Style the popup
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2b2b2b;
                border: 2px solid #555555;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
            QPushButton:pressed {
                background-color: #5c5c5c;
            }
        """
        )

        # Position at cursor
        self.move(cursor_pos)

        # Setup auto-close timer (3 seconds)
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.close)
        self.close_timer.setSingleShot(True)
        self.close_timer.start(3000)  # 3000 ms = 3 seconds

    def on_opacity_clicked(self, opacity):
        """Handle opacity button click."""
        self.parent_row.set_opacity(opacity)
        self.close()

from typing import Dict
from krita import *  # type: ignore
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QColor
from lazy_tools.utils.color_scheme import ColorScheme

# from lazy_tools.utils.logs import write_log


class NameFilterSection(QWidget):

    def __init__(self, parent=None, use_prefix_match=True, default_filter="_"):
        super().__init__(parent)
        self.parent_docker = parent
        self.name_rows: Dict[int, "NameFilterRow"] = {}
        self.use_prefix_match = use_prefix_match
        self.default_filter = default_filter

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(1)

        # Create filter input row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(5)

        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet(
            "font-size: 14px; "
            "font-weight: bold;"
            "color: #a3a3a3; "
            "background-color: #191919;"
        )
        filter_label.setFixedWidth(60)
        filter_row.addWidget(filter_label)

        # Create text input with default value
        self.filter_input = QLineEdit()
        self.filter_input.setText(self.default_filter)
        self.filter_input.setPlaceholderText("Enter filter pattern...")
        self.filter_input.textChanged.connect(self.on_filter_changed)
        filter_row.addWidget(self.filter_input)

        main_layout.addLayout(filter_row)

        # Create container for node rows
        self.node_rows_layout = QVBoxLayout()
        self.node_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.node_rows_layout.setSpacing(1)
        main_layout.addLayout(self.node_rows_layout)

        self.setLayout(main_layout)

        # Setup timer to update UI every 1 second
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.on_timer_update)
        self.update_timer.start(1000)  # 1000 ms = 1 second

        # Initial UI setup
        self.update_ui(self.filter_input.text())

    def on_filter_changed(self):
        """Called when the filter text input changes."""
        self.update_ui(self.filter_input.text())

    def on_timer_update(self):
        """Called by the timer every second."""
        self.update_ui(self.filter_input.text())

    def update_ui(self, filter_pattern):
        """Update the UI by checking current nodes and refreshing the list."""
        # Get current node list
        current_nodes = self.generate_target_list(filter_pattern)

        # Remove duplicates: keep only unique node names
        seen_names = set()
        unique_nodes = []
        for node in current_nodes:
            node_name = node.name()
            if node_name not in seen_names:
                seen_names.add(node_name)
                unique_nodes.append(node)

        unique_nodes = sorted(unique_nodes, key=lambda node: node.name().lower())

        # Get current unique node names and existing node names as sorted lists
        current_node_names = sorted([node.name() for node in unique_nodes])
        existing_node_names = sorted([row.node_name for row in self.name_rows.values()])

        # If the node list hasn't changed, skip update
        if current_node_names == existing_node_names:
            return

        # Clear existing widgets
        for i in list(self.name_rows.keys()):
            widget = self.name_rows[i]
            self.node_rows_layout.removeWidget(widget)
            widget.deleteLater()
        self.name_rows.clear()

        # Add new widgets
        for i, node in enumerate(unique_nodes, start=0):
            name_row = NameFilterRow(node.name(), self.parent_docker)
            self.name_rows[i] = name_row
            self.node_rows_layout.addWidget(name_row)

    def generate_target_list(self, filter_pattern="_"):
        targetNodes = []
        doc = Krita.instance().activeDocument()
        if not doc:
            return targetNodes
        root = doc.rootNode()
        for node in self.get_all_nodes(root):
            node_name = node.name()
            if self.use_prefix_match:
                # Prefix match: node name starts with the filter pattern
                if node_name.startswith(filter_pattern) and filter_pattern != "":
                    targetNodes.append(node)
            else:
                # Any match: filter pattern appears anywhere in node name
                if filter_pattern in node_name and filter_pattern != "":
                    targetNodes.append(node)
        return targetNodes

    def get_all_nodes(self, node):
        nodes = [node]
        for child in node.childNodes():
            nodes.extend(self.get_all_nodes(child))
        return nodes

    def closeEvent(self, event):
        """Stop the timer when widget is closed."""
        if hasattr(self, "update_timer"):
            self.update_timer.stop()
        super().closeEvent(event)


class NameFilterRow(QWidget):

    def __init__(self, node_name: str, parent=None):
        super().__init__(parent)
        self.node_name = node_name
        self.parent_docker = parent

        self.setup_ui()

    def setup_ui(self):
        # Main vertical layout to hold two rows
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(1)

        # First row - node name and toggle button
        first_row = QHBoxLayout()
        first_row.setSpacing(1)

        # Toggle visibility button
        self.toggle_button = QPushButton("👁")
        self.toggle_button.setFixedSize(30, 25)
        self.toggle_button.clicked.connect(self.toggle_visibility)
        first_row.addWidget(self.toggle_button)

        # node name label
        self.node_name_label = QLabel(self.node_name)
        self.node_name_label.setMaximumWidth(300)
        self.node_name_label.setFixedHeight(30)
        self.node_name_label.setStyleSheet(
            "font-size: 16px; "
            "font-weight: bold;"
            "color: #a3a3a3; "
            "background-color: #191919;"
        )
        # Make label clickable
        self.node_name_label.mousePressEvent = self.on_label_clicked
        first_row.addWidget(self.node_name_label)

        # Add stretch to push everything to the left
        first_row.addStretch()

        # Second row - opacity buttons
        second_row = QHBoxLayout()
        second_row.setSpacing(1)

        self.opacity_buttons = {}
        opacity_values = [10, 25, 50, 75, 100]

        for opacity in opacity_values:
            btn = QPushButton(str(opacity))
            btn.setFixedSize(25, 25)
            btn.clicked.connect(lambda checked, op=opacity: self.set_opacity(op))
            self.opacity_buttons[opacity] = btn
            second_row.addWidget(btn)

        # Add stretch to push everything to the left
        second_row.addStretch()

        # Add both rows to main layout
        main_layout.addLayout(first_row)
        main_layout.addLayout(second_row)

        self.setLayout(main_layout)

    def on_label_clicked(self, event):
        """Handle clicks on the label: regular click activates, Ctrl+right click removes."""
        from PyQt5.QtCore import Qt

        try:
            # Check if it's Ctrl+right click
            if (event.button() == Qt.RightButton and
                event.modifiers() & Qt.ControlModifier):
                self.remove_first_node()
            else:
                # Regular click - activate the node
                self.activate_first_node()

        except Exception as e:
            print(f"Error handling label click for {self.node_name}: {e}")

    def activate_first_node(self):
        """Activate the first node with this name."""
        try:
            doc = Krita.instance().activeDocument()
            if not doc:
                return

            # Find the first node with this name
            root_node = doc.rootNode()
            target_node = self._find_first_node_by_name(root_node, self.node_name)

            if target_node:
                # Set this node as the active/current node
                doc.setActiveNode(target_node)
                print(f"Activated node: {self.node_name}")
            else:
                print(f"No node found with name: {self.node_name}")

        except Exception as e:
            print(f"Error activating node {self.node_name}: {e}")

    def remove_first_node(self):
        """Remove the first node with this name."""
        try:
            doc = Krita.instance().activeDocument()
            if not doc:
                return

            # Find the first node with this name
            root_node = doc.rootNode()
            target_node = self._find_first_node_by_name(root_node, self.node_name)

            if target_node:
                # Remove the node
                parent = target_node.parentNode()
                if parent:
                    parent.removeChildNode(target_node)
                    doc.refreshProjection()
                    print(f"Removed node: {self.node_name}")
                else:
                    print(f"Cannot remove root node: {self.node_name}")
            else:
                print(f"No node found with name: {self.node_name}")

        except Exception as e:
            print(f"Error removing node {self.node_name}: {e}")

    def _find_first_node_by_name(self, node: Node, target_name: str):
        """Recursively find the first node with the target name."""
        if not node:
            return None

        # Don't check the root node
        if node.type() == "grouplayer" and node.parentNode() is None:
            for child in node.childNodes():
                result = self._find_first_node_by_name(child, target_name)
                if result:
                    return result
            return None

        # Check if this node matches
        if node.name() == target_name:
            return node

        # Check child nodes
        for child in node.childNodes():
            result = self._find_first_node_by_name(child, target_name)
            if result:
                return result

        return None

    def toggle_visibility(self):
        """Toggle visibility of all layers with this color label."""
        try:
            doc = Krita.instance().activeDocument()
            if doc:
                root_node = doc.rootNode()
                self._toggle_layers_recursive(root_node)
                doc.refreshProjection()
        except Exception as e:
            print(f"Error toggling visibility for {self.node_name}: {e}")

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
                print(f"Set {self.node_name} layers opacity to {opacity_percent}%")
        except Exception as e:
            print(f"Error setting opacity for {self.node_name}: {e}")

    def _toggle_layers_recursive(self, node: Node):
        """Recursively toggle visibility of layers with the target color label."""
        if not node:
            return

        # Don't process the root node
        if node.type() == "grouplayer" and node.parentNode() is None:
            for child in node.childNodes():
                self._toggle_layers_recursive(child)
            return

        # Check if the node's name match the target
        if node.name() == self.node_name:
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

        # Check if this layer has the target name and type is correct
        if node.name() == self.node_name and node.type() in [
            "paintlayer",
            "grouplayer",
            "vectorlayer",
            "filterlayer",
        ]:
            node.setOpacity(opacity_value)

        # Process child nodes
        for child in node.childNodes():
            self._set_layers_opacity_recursive(child, opacity_value)

    def _toggle_node_visibility(self, node: Node):
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

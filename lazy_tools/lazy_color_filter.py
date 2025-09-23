"""
Lazy Color Filter Extension for Krita

This extension adds a color filter dropdown to the Layer Docker for showing/hiding layers by color label.
"""

from typing import Optional
from krita import Krita, Extension, Node  # type: ignore
from PyQt5.QtWidgets import QComboBox, QHBoxLayout
from PyQt5.QtGui import QIcon, QPixmap, QColor
from lazy_tools.utils.color_scheme import ColorScheme


class LazyColorFilter(Extension):
    """
    Extension class that adds color filter functionality to Krita's Layer Docker.
    Allows showing/hiding layers based on their color labels.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.filterComboBox: Optional[QComboBox] = None
        self.current_filter: int = -1  # -1 means show all
        self._setup_connections()

    def setup(self):
        """Called when Krita.instance() exists. Perform any setup work here."""
        pass

    def createActions(self, window):
        """Called after setup(). Create any actions here."""
        pass

    def _setup_connections(self):
        """Setup application connections."""
        application = Krita.instance()
        appNotifier = application.notifier()
        appNotifier.windowCreated.connect(self._add_element_to_docker)

    def _add_element_to_docker(self):
        """Add the color filter combo box to Krita's Layer Docker."""
        try:
            layer_docker = self._find_layer_docker()
            if not layer_docker:
                return

            layout = self._find_docker_layout(layer_docker)
            if not layout:
                return

            if not self.filterComboBox:
                self.filterComboBox = self._build_filter_combo_box()

            # Insert after the color label combo box (at position 1)
            layout.insertWidget(1, self.filterComboBox)
            self.filterComboBox.activated.connect(self._apply_color_filter)

        except Exception as e:
            print(f"Error adding color filter to Layer Docker: {e}")

    def _find_layer_docker(self):
        """Find and return the Layer Docker widget."""
        return next(
            (w for w in Krita.instance().dockers() if w.objectName() == "KisLayerBox"),
            None,
        )

    def _find_docker_layout(self, layer_docker):
        """Find and return the layout where layer controls are located."""
        return layer_docker.findChild(QHBoxLayout, "hbox2")

    def _apply_color_filter(self, index: int):
        """Apply color filter to toggle visibility of layers with selected color."""
        try:
            # Convert combo box index to color label index
            # Index maps directly to color labels (1=Blue, 2=Green, etc.)
            color_filter = index + 1
            self.current_filter = color_filter

            # Get current document and toggle layers with target color
            doc = Krita.instance().activeDocument()
            if doc:
                root_node = doc.rootNode()
                # Toggle visibility of layers with the selected color only
                self._filter_layers_recursive(root_node, color_filter)

        except Exception as e:
            print(f"Error applying color filter: {e}")

    def _filter_layers_recursive(self, node: Node, target_color: int):
        """Recursively toggle visibility of layers with the target color label using Krita's toggle action."""
        if not node:
            return

        # Don't process the root node
        if node.type() == "grouplayer" and node.parentNode() is None:
            # But still process its children
            for child in node.childNodes():
                self._filter_layers_recursive(child, target_color)
            return

        # Check if this layer has the target color label
        if node.type() in ["paintlayer", "grouplayer", "vectorlayer", "filterlayer"]:
            layer_color = node.colorLabel()

            # Only modify layers that have the target color label
            if layer_color == target_color:
                # Use Krita's built-in toggle action for cleaner visibility management
                self._toggle_layer_visibility(node)

        # Process child nodes
        for child in node.childNodes():
            self._filter_layers_recursive(child, target_color)

    def _toggle_layer_visibility(self, node: Node):
        """Toggle layer visibility using Krita's built-in action."""
        try:
            # Get the current window and view
            window = Krita.instance().activeWindow()
            if not window:
                return

            view = window.activeView()
            if not view:
                return

            # Select the target node first
            view.setCurrentNode(node)

            # Use Krita's built-in toggle display selection action
            # This properly handles groups and their children automatically
            window.action("toggle_display_selection").trigger()

            # Force canvas refresh to immediately show visibility changes
            doc = Krita.instance().activeDocument()
            if doc:
                # Refresh the projection to update the canvas display
                doc.refreshProjection()
                # Also refresh the layer docker to ensure UI consistency
                if view:
                    view.refreshCanvas()

        except Exception as e:
            print(f"Error toggling layer visibility: {e}")
            # Fallback to manual visibility toggle if action fails
            current_visibility = node.visible()
            node.setVisible(not current_visibility)

            # Force refresh for fallback method too
            try:
                doc = Krita.instance().activeDocument()
                if doc:
                    doc.refreshProjection()
                    view = Krita.instance().activeWindow().activeView()
                    if view:
                        view.refreshCanvas()
            except:
                pass

    def _restore_all_layers(self):
        """Restore visibility of all previously hidden layers."""
        # Note: This method is kept for potential future use
        # but with toggle_display_selection, manual restoration is less needed
        pass

    def restore_all_layers(self):
        """Public method to restore all layer visibility."""
        self._restore_all_layers()

    def _build_filter_combo_box(self) -> QComboBox:
        """Build and configure the color filter combo box."""
        combo_box = QComboBox()
        combo_box.setAccessibleName("colorFilterBox")
        combo_box.setObjectName("colorFilterBox")
        combo_box.setFixedSize(ColorScheme.COMBO_SIZE)
        combo_box.setToolTip("Filter layers by color label")

        self._populate_filter_combo_box(combo_box)
        return combo_box

    def _populate_filter_combo_box(self, combo_box: QComboBox):
        """Populate the filter combo box with color icons."""
        # Add colored options in the same order as LazyColorLabel
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
            icon = self._create_color_icon(color)
            combo_box.addItem(icon, name)

    def _create_color_icon(self, color: QColor) -> QIcon:
        """Create an icon for a specific color."""
        pixmap = QPixmap(ColorScheme.ICON_SIZE)
        pixmap.fill(color)
        return QIcon(pixmap)

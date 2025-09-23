"""
Lazy Color Label Extension for Krita

This extension adds a color label dropdown to the Layer Docker for quick layer color labeling.
"""

from typing import List, Optional
from krita import Krita, Extension, Node  # type: ignore
from PyQt5.QtWidgets import QComboBox, QHBoxLayout
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QPen
from lazy_tools.utils.layer_utils import get_current_layer, get_selected_layers
from lazy_tools.utils.color_scheme import ColorScheme


class LazyColorLabel(Extension):
    """
    Main extension class that adds color label functionality to Krita's Layer Docker.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.comboBox: Optional[QComboBox] = None
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
        """Add the color combo box to Krita's Layer Docker."""
        try:
            layer_docker = self._find_layer_docker()
            if not layer_docker:
                return

            layout = self._find_docker_layout(layer_docker)
            if not layout:
                return

            if not self.comboBox:
                self.comboBox = self._build_combo_box()

            layout.insertWidget(0, self.comboBox)
            self.comboBox.activated.connect(self._update_layer_color_label)

        except Exception as e:
            print(f"Error adding element to Layer Docker: {e}")

    def _find_layer_docker(self):
        """Find and return the Layer Docker widget."""
        return next(
            (w for w in Krita.instance().dockers() if w.objectName() == "KisLayerBox"),
            None,
        )

    def _find_docker_layout(self, layer_docker):
        """Find and return the layout where layer controls are located."""
        return layer_docker.findChild(QHBoxLayout, "hbox2")

    def _update_layer_color_label(self, index: int):
        """Update the color label for selected layers or current layer."""
        try:
            selected_layers = get_selected_layers()

            if selected_layers:
                self._apply_color_to_layers(selected_layers, index)
            else:
                current_layer = get_current_layer()
                if current_layer:
                    self._apply_color_to_layers([current_layer], index)

        except Exception as e:
            print(f"Error updating layer color label: {e}")

    def _apply_color_to_layers(self, layers: List[Node], color_index: int):
        """Apply color label to a list of layers."""
        for layer in layers:
            if layer:
                layer.setColorLabel(color_index)

    def _build_combo_box(self) -> QComboBox:
        """Build and configure the color selection combo box."""
        combo_box = QComboBox()
        combo_box.setAccessibleName("colorLabelBox")
        combo_box.setObjectName("colorLabelBox")
        combo_box.setFixedSize(ColorScheme.COMBO_SIZE)
        combo_box.setToolTip("Select color label for layer(s)")

        self._populate_combo_box(combo_box)
        return combo_box

    def _populate_combo_box(self, combo_box: QComboBox):
        """Populate the combo box with color icons."""
        # Add transparent/none option first
        transparent_icon = self._create_transparent_icon()
        combo_box.addItem(transparent_icon, "None")

        # Add colored options
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

    def _create_transparent_icon(self) -> QIcon:
        """Create an icon for the transparent/none color option."""
        pixmap = QPixmap(ColorScheme.ICON_SIZE)
        pixmap.fill(ColorScheme.COLORS[0])  # Transparent

        # Draw border around transparent area
        painter = QPainter(pixmap)
        try:
            pen = QPen()
            pen.setWidth(ColorScheme.BORDER_WIDTH)
            painter.setPen(pen)
            painter.drawRect(
                0, 0, ColorScheme.ICON_SIZE.width(), ColorScheme.ICON_SIZE.height()
            )
        finally:
            painter.end()

        return QIcon(pixmap)

    def _create_color_icon(self, color: QColor) -> QIcon:
        """Create an icon for a specific color."""
        pixmap = QPixmap(ColorScheme.ICON_SIZE)
        pixmap.fill(color)
        return QIcon(pixmap)

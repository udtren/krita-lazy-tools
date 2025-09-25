"""
Lazy Tools Docker for Krita

This docker provides advanced color-based layer filtering with visibility and opacity controls.
"""

from typing import Optional, List, Dict
from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita, Node  # type: ignore
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QDockWidget,
    QFrame,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QColor
from lazy_tools.widgets.color_filter_widgets import ColorFilterSection
from lazy_tools.widgets.scripts_widgets import ScriptsSection
from lazy_tools.widgets.segment_widgets import SegmentSection


class CollapsibleSection(QWidget):
    """
    A collapsible section widget that can show/hide its content.
    """

    def __init__(self, title: str, parent=None, collapsed=False):
        super().__init__(parent)
        self.title = title
        self.is_collapsed = collapsed
        self.content_widget = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the collapsible section UI."""
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create header button
        self.header_button = QPushButton()
        self.header_button.setFlat(True)
        self.header_button.setStyleSheet(
            """
            QPushButton {
                text-align: left;
                padding: 5px;
                border: 1px solid #888;
                background-color: #555;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """
        )
        self.header_button.clicked.connect(self.toggle_collapsed)
        self.update_header_text()

        self.main_layout.addWidget(self.header_button)

        # Create content frame
        self.content_frame = QFrame()
        self.content_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.content_frame.setStyleSheet("QFrame { border: 1px solid #888; }")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_frame.setLayout(self.content_layout)

        self.main_layout.addWidget(self.content_frame)
        self.setLayout(self.main_layout)

        # Set initial visibility based on collapsed state
        self.content_frame.setVisible(not self.is_collapsed)

    def set_content_widget(self, widget: QWidget):
        """Set the widget to be shown/hidden in this section."""
        if self.content_widget:
            self.content_layout.removeWidget(self.content_widget)

        self.content_widget = widget
        self.content_layout.addWidget(widget)

    def toggle_collapsed(self):
        """Toggle the collapsed state of this section."""
        self.is_collapsed = not self.is_collapsed
        self.content_frame.setVisible(not self.is_collapsed)
        self.update_header_text()

    def update_header_text(self):
        """Update the header button text with collapse indicator."""
        arrow = "▼" if not self.is_collapsed else "▶"
        self.header_button.setText(f"{arrow} {self.title}")


class LazyToolsDockerWidget(QDockWidget):
    """
    Main docker widget for color-based layer filtering with opacity controls.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lazy Tools")
        self.setup_ui()

    def setup_ui(self):
        """Setup the main UI."""
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Create collapsible Color Filter section
        self.color_filter_section = CollapsibleSection("Color Filter")
        self.color_filter_content = ColorFilterSection(self)
        self.color_filter_section.set_content_widget(self.color_filter_content)

        main_layout.addWidget(self.color_filter_section)

        # Add control buttons directly below Color Filter section
        self.add_control_buttons(main_layout)

        # Create collapsible AI Segmentation section
        self.segment_section = CollapsibleSection("AI Segmentation")
        self.segment_content = SegmentSection(self)
        self.segment_section.set_content_widget(self.segment_content)

        main_layout.addWidget(self.segment_section)

        # Create collapsible Scripts section
        self.scripts_section = CollapsibleSection("Scripts")
        self.scripts_content = ScriptsSection(self)
        self.scripts_section.set_content_widget(self.scripts_content)

        main_layout.addWidget(self.scripts_section)

        # Add small stretch at the end to push content up slightly
        main_layout.addStretch(1)

        main_widget.setLayout(main_layout)
        self.setWidget(main_widget)

    def add_control_buttons(self, layout: QVBoxLayout):
        """Add control buttons for global operations."""
        button_layout = QHBoxLayout()

        # Show All button
        show_all_btn = QPushButton("Show All")
        show_all_btn.setToolTip("Make all layers visible")
        show_all_btn.clicked.connect(self.show_all_layers)
        button_layout.addWidget(show_all_btn)

        # Reset Opacity button
        reset_opacity_btn = QPushButton("Reset Opacity")
        reset_opacity_btn.setToolTip("Set all layers opacity to 100%")
        reset_opacity_btn.clicked.connect(self.reset_all_opacity)
        button_layout.addWidget(reset_opacity_btn)

        layout.addLayout(button_layout)

    def show_all_layers(self):
        """Make all layers visible."""
        try:
            doc = Krita.instance().activeDocument()
            if doc:
                root_node = doc.rootNode()
                self._show_all_recursive(root_node)
                doc.refreshProjection()
                print("All layers are now visible")
        except Exception as e:
            print(f"Error showing all layers: {e}")

    def reset_all_opacity(self):
        """Reset all layers opacity to 100%."""
        try:
            doc = Krita.instance().activeDocument()
            if doc:
                root_node = doc.rootNode()
                self._reset_opacity_recursive(root_node)
                doc.refreshProjection()
                print("All layers opacity reset to 100%")
        except Exception as e:
            print(f"Error resetting opacity: {e}")

    def _show_all_recursive(self, node: Node):
        """Recursively make all layers visible."""
        if not node:
            return

        # Don't process the root node
        if node.type() == "grouplayer" and node.parentNode() is None:
            for child in node.childNodes():
                self._show_all_recursive(child)
            return

        # Make layer visible
        if node.type() in ["paintlayer", "grouplayer", "vectorlayer", "filterlayer"]:
            node.setVisible(True)

        # Process child nodes
        for child in node.childNodes():
            self._show_all_recursive(child)

    def _reset_opacity_recursive(self, node: Node):
        """Recursively reset opacity of all layers to 100%."""
        if not node:
            return

        # Don't process the root node
        if node.type() == "grouplayer" and node.parentNode() is None:
            for child in node.childNodes():
                self._reset_opacity_recursive(child)
            return

        # Reset opacity
        if node.type() in ["paintlayer", "grouplayer", "vectorlayer", "filterlayer"]:
            node.setOpacity(255)  # 255 = 100%

        # Process child nodes
        for child in node.childNodes():
            self._reset_opacity_recursive(child)


class LazyToolsDockerFactory(DockWidgetFactoryBase):

    def __init__(self):
        super().__init__("LazyToolsDocker", DockWidgetFactory.DockRight)

    def createDockWidget(self):
        return LazyToolsDockerWidget()

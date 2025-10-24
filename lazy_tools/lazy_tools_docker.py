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
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QPixmap, QColor
from lazy_tools.widgets.color_filter_widgets import ColorFilterSection
from lazy_tools.widgets.scripts_widgets import ScriptsSection
from lazy_tools.widgets.segment_widgets import SegmentSection
from lazy_tools.widgets.name_filter_widgets import NameFilterSection
import os


class LazyToolsDockerWidget(QDockWidget):
    """
    Main docker widget for color-based layer filtering with opacity controls.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lazy Tools")
        self.setup_ui()

        # Setup timer to update UI every 1 second
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_docker_size)
        self.update_timer.start(2000)  # 1000 ms = 1 second

    def setup_ui(self):
        """Setup the main UI."""
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        ##############################
        # Create collapsible Color Filter section
        ##############################

        self.color_filter_section = CollapsibleSection("Color Filter", collapsed=True)
        self.color_filter_content = ColorFilterSection(self)
        self.color_filter_section.set_content_widget(self.color_filter_content)

        main_layout.addWidget(self.color_filter_section)

        ##############################
        # Create collapsible Name Filter (Prefix) section
        ##############################

        self.name_filter_section = CollapsibleSection("Name Filter (Prefix)")
        self.name_filter_content = NameFilterSection(
            self, default_filter="_", use_prefix_match=True
        )
        self.name_filter_section.set_content_widget(self.name_filter_content)

        main_layout.addWidget(self.name_filter_section)

        ##############################
        # Create collapsible Name Filter  section
        ##############################

        self.name_filter_section2 = CollapsibleSection("Name Filter (Any)")
        self.name_filter_content2 = NameFilterSection(
            self, default_filter="", use_prefix_match=False
        )
        self.name_filter_section2.set_content_widget(self.name_filter_content2)

        main_layout.addWidget(self.name_filter_section2)

        ##############################
        # Check if .pt files exist in models directory before adding AI Segmentation section
        ##############################
        if self._has_pt_models():
            self.segment_section = CollapsibleSection("AI Segmentation", collapsed=True)
            self.segment_content = SegmentSection(self)
            self.segment_section.set_content_widget(self.segment_content)
            main_layout.addWidget(self.segment_section)

        ##############################
        # Create collapsible Scripts section
        ##############################
        self.scripts_section = CollapsibleSection("Scripts")
        self.scripts_content = ScriptsSection(self)
        self.scripts_section.set_content_widget(self.scripts_content)

        main_layout.addWidget(self.scripts_section)

        ##############################
        # Add small stretch at the end to push content up slightly
        main_layout.addStretch()

        main_widget.setLayout(main_layout)
        self.setWidget(main_widget)

    def _has_pt_models(self):
        try:
            # Get the models directory path (lazy_tools/models)
            models_dir = os.path.join(os.path.dirname(__file__), "models")

            print(f"Checking models directory: {models_dir}")

            # Check if directory exists
            if not os.path.exists(models_dir):
                print(f"Directory does not exist: {models_dir}")
                return False
            else:
                print(f"Directory exists: {models_dir}")
                return True

        except Exception as e:
            print(f"Error checking for .pt models: {e}")
            return False

    def update_docker_size(self):
        # Force immediate size recalculation
        self.updateGeometry()
        self.adjustSize()

        # Find and update parent docker size more aggressively
        parent_widget = self.parent()
        while parent_widget:
            parent_widget.updateGeometry()
            if hasattr(parent_widget, "layout") and parent_widget.layout():
                parent_widget.layout().invalidate()
                parent_widget.layout().activate()

            if isinstance(parent_widget, QDockWidget):
                # Force the docker to resize by setting size policies and hints
                parent_widget.updateGeometry()
                parent_widget.adjustSize()

                # Get the main widget and force it to recalculate
                main_widget = parent_widget.widget()
                if main_widget:
                    main_widget.updateGeometry()
                    main_widget.adjustSize()
                break
            parent_widget = parent_widget.parent()


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
                padding: 1px;
                border: 1px solid #888;
                color: white;
                font-size: 12px;
                font-weight: bold;
                color: #1b1918;
                background-color: #6a6a6a;
            }
            QPushButton:hover {
                background-color: #818181;
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
        self.content_layout.setContentsMargins(1, 1, 1, 1)
        self.content_frame.setLayout(self.content_layout)

        self.main_layout.addWidget(self.content_frame)
        self.setLayout(self.main_layout)

        # Set initial visibility based on collapsed state
        self.content_frame.setVisible(not self.is_collapsed)
        self.content_layout.addStretch()

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

    def sizeHint(self):
        """Return appropriate size hint based on collapsed state."""
        if self.is_collapsed:
            # Only return height for header button when collapsed
            return self.header_button.sizeHint()
        else:
            # Return full size when expanded
            return super().sizeHint()

    def minimumSizeHint(self):
        """Return minimum size hint based on collapsed state."""
        if self.is_collapsed:
            return self.header_button.minimumSizeHint()
        else:
            return super().minimumSizeHint()


class LazyToolsDockerFactory(DockWidgetFactoryBase):

    def __init__(self):
        super().__init__("LazyToolsDocker", DockWidgetFactory.DockRight)

    def createDockWidget(self):
        return LazyToolsDockerWidget()

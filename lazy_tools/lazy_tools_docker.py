from krita import DockWidgetFactoryBase, Krita  # type: ignore
from .compat import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QDockWidget,
    QFrame,
    QTimer,
    QSize,
    QIcon,
)
from lazy_tools.widgets.color_filter_widgets import ColorFilterSection
from lazy_tools.widgets.scripts_widgets import ScriptsSection
from lazy_tools.widgets.segment_widgets import SegmentSection
from lazy_tools.widgets.name_filter_widgets import NameFilterSection
from lazy_tools.config.config_loader import (
    get_script_enabled,
    get_section_enabled,
    get_icon_dir,
)
from lazy_tools.dialogs import SettingsDialog
import os

try:
    from quick_access_manager.gesture.gesture_main import (
        pause_gesture_event_filter,
        resume_gesture_event_filter,
        is_gesture_filter_paused,
    )

    GESTURE_AVAILABLE = True
except ImportError:
    GESTURE_AVAILABLE = False


class LazyToolsDockerWidget(QDockWidget):
    """
    Main docker widget for color-based layer filtering with opacity controls.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lazy Tools")
        self.setup_ui()

        ## Disable top menu shortcuts
        if get_script_enabled("disable_top_menu_shortcuts"):
            application = Krita.instance()
            appNotifier = application.notifier()
            appNotifier.windowCreated.connect(self.disable_top_menu_shortcuts)

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

        if get_section_enabled("name_filter_prefix_section"):
            self.name_filter_section = CollapsibleSection("Name Filter (Prefix)")
            self.name_filter_content = NameFilterSection(
                self, default_filter="_", use_prefix_match=True
            )
            self.name_filter_section.set_content_widget(self.name_filter_content)
            main_layout.addWidget(self.name_filter_section)

        ##############################
        # Create collapsible Name Filter section
        ##############################

        if get_section_enabled("name_filter_section"):
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
        self.scripts_section = CollapsibleSection("Scripts", collapsed=True)
        self.scripts_content = ScriptsSection(self)
        self.scripts_section.set_content_widget(self.scripts_content)

        main_layout.addWidget(self.scripts_section)

        ##############################
        # Add small stretch at the end to push content up slightly
        main_layout.addStretch()

        ##############################
        # Add Settings button at the bottom
        ##############################
        settings_button_layout = QHBoxLayout()
        settings_button_layout.setContentsMargins(0, 0, 0, 0)

        self.settings_button = QPushButton()
        icon_path = os.path.join(get_icon_dir(), "setting.png")
        self.settings_button.setIcon(QIcon(icon_path))
        self.settings_button.setIconSize(QSize(18, 18))
        self.settings_button.setFixedSize(24, 24)
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(self.open_settings_dialog)

        settings_button_layout.addWidget(self.settings_button)
        settings_button_layout.addStretch()

        main_layout.addLayout(settings_button_layout)

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
        self.resize(self.width(), self.sizeHint().height())

    def disable_top_menu_shortcuts(self):
        ########################################################
        ## Disable top menu shortcuts
        qwin = Krita.instance().activeWindow().qwindow()
        # Disable top menu shortcuts by removing "&" from their texts
        actions = qwin.menuWidget().actions()
        for action in actions:
            action.setText(action.text().replace("&", ""))
        ########################################################

    def open_settings_dialog(self):
        """Open the settings configuration dialog"""
        # Pause gesture if available and not already paused
        should_resume_gesture = False
        if GESTURE_AVAILABLE and not is_gesture_filter_paused():
            pause_gesture_event_filter()
            should_resume_gesture = True

        dialog = SettingsDialog(self)
        dialog.exec()

        # Resume gesture if we paused it
        if should_resume_gesture:
            resume_gesture_event_filter()


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
        self.header_button.setStyleSheet("""
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
        """)
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
        try:
            _dock_pos = DockWidgetFactoryBase.DockRight
        except AttributeError:
            _dock_pos = DockWidgetFactoryBase.DockPosition.DockRight  # Krita 6
        super().__init__("LazyToolsDocker", _dock_pos)

    def createDockWidget(self):
        return LazyToolsDockerWidget()

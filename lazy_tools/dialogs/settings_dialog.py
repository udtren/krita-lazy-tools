from ..compat import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QDialog,
    QTabWidget,
    QCheckBox,
    QFormLayout,
    QTextEdit,
    QColorDialog,
    QColor,
)
from ..config.config_loader import (
    load_config,
    save_config,
    set_script_enabled,
    load_name_color_list,
    save_name_color_list,
    get_foreground_color,
    get_section_enabled,
    set_section_enabled,
    get_blending_modes,
    save_blending_modes,
)


class SettingsDialog(QDialog):
    """Settings dialog for Lazy Tools configuration"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lazy Tools Settings")
        self.setMinimumSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        """Setup the settings dialog UI"""
        layout = QVBoxLayout()

        self.tab_widget = QTabWidget()

        self.common_tab = QWidget()
        self.setup_common_tab()
        self.tab_widget.addTab(self.common_tab, "Common")

        self.name_list_tab = QWidget()
        self.setup_name_list_tab()
        self.tab_widget.addTab(self.name_list_tab, "Name List")

        self.blending_modes_tab = QWidget()
        self.setup_blending_modes_tab()
        self.tab_widget.addTab(self.blending_modes_tab, "Blending Modes")

        layout.addWidget(self.tab_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def setup_common_tab(self):
        """Setup the Common settings tab"""
        layout = QFormLayout()

        config = load_config()

        self.checkboxes = {}

        screen_color_picker_enabled = config.get("screen_color_picker", {}).get(
            "enabled", True
        )
        self.screen_color_picker_checkbox = QCheckBox("Enable Screen Color Picker")
        self.screen_color_picker_checkbox.setChecked(screen_color_picker_enabled)
        self.checkboxes["screen_color_picker"] = self.screen_color_picker_checkbox
        layout.addRow(self.screen_color_picker_checkbox)

        disable_top_menu_enabled = config.get("disable_top_menu_shortcuts", {}).get(
            "enabled", True
        )
        self.disable_top_menu_checkbox = QCheckBox("Disable Top Menu Shortcuts")
        self.disable_top_menu_checkbox.setChecked(disable_top_menu_enabled)
        self.checkboxes["disable_top_menu_shortcuts"] = self.disable_top_menu_checkbox
        layout.addRow(self.disable_top_menu_checkbox)

        # Section visibility options
        self.section_checkboxes = {}

        self.name_filter_prefix_checkbox = QCheckBox("Enable Name Filter (Prefix) section")
        self.name_filter_prefix_checkbox.setChecked(
            get_section_enabled("name_filter_prefix_section")
        )
        self.section_checkboxes["name_filter_prefix_section"] = self.name_filter_prefix_checkbox
        layout.addRow(self.name_filter_prefix_checkbox)

        self.name_filter_checkbox = QCheckBox("Enable Name Filter section")
        self.name_filter_checkbox.setChecked(
            get_section_enabled("name_filter_section")
        )
        self.section_checkboxes["name_filter_section"] = self.name_filter_checkbox
        layout.addRow(self.name_filter_checkbox)

        # Foreground Color settings (1-9)
        self.colors = {}
        self.color_buttons = {}
        for i in range(1, 10):
            color_data = get_foreground_color(i)
            self.colors[i] = QColor(
                color_data.get("r", 136),
                color_data.get("g", 136),
                color_data.get("b", 136),
                color_data.get("a", 255),
            )
            button = QPushButton()
            button.setFixedSize(60, 24)
            button.clicked.connect(lambda _, num=i: self.pick_color(num))
            self.color_buttons[i] = button
            self.update_color_button(i)
            layout.addRow(f"Foreground Color {i}:", button)

        note_label = QLabel("Note: Changes will take effect after restarting Krita.")
        note_label.setStyleSheet("color: #888; font-style: italic; margin-top: 10px;")
        layout.addRow(note_label)

        self.common_tab.setLayout(layout)

    def update_color_button(self, color_num):
        """Update the color button background to show the selected color"""
        self.color_buttons[color_num].setStyleSheet(
            f"background-color: {self.colors[color_num].name()}; border: 1px solid #888;"
        )

    def pick_color(self, color_num):
        """Open color picker dialog for the specified color"""
        color = QColorDialog.getColor(
            self.colors[color_num], self, f"Select Foreground Color {color_num}"
        )
        if color.isValid():
            self.colors[color_num] = color
            self.update_color_button(color_num)

    def setup_name_list_tab(self):
        """Setup the Name List tab"""
        layout = QVBoxLayout()

        description_label = QLabel(
            "Configure layer names and optional colors.\n"
            "Format: layer_name or layer_name, Color\n"
            "\n"
            "Supported colors: Blue, Green, Yellow, Orange, Brown, Red, Purple, Grey\n"
            "\n"
            "Example:\n"
            "  layer_name1\n"
            "  layer_name2\n"
            "  layer_name3, Blue"
        )
        description_label.setStyleSheet(
            "color: #888; font-size: 11px; margin-bottom: 5px;"
        )
        layout.addWidget(description_label)

        self.name_color_list_text = QTextEdit()
        self.name_color_list_text.setPlaceholderText(
            "Enter layer names here, one per line...\n"
            "Optionally add color: layer_name, Color"
        )

        current_content = load_name_color_list()
        self.name_color_list_text.setPlainText(current_content)

        layout.addWidget(self.name_color_list_text)

        self.name_list_tab.setLayout(layout)

    def setup_blending_modes_tab(self):
        """Setup the Blending Modes tab"""
        layout = QVBoxLayout()

        description_label = QLabel(
            "Configure available blending modes.\n"
            "One mode per line. Used in New Layer and Duplicate dialogs."
        )
        description_label.setStyleSheet(
            "color: #888; font-size: 11px; margin-bottom: 5px;"
        )
        layout.addWidget(description_label)

        self.blending_modes_text = QTextEdit()
        self.blending_modes_text.setPlaceholderText("Enter blending modes, one per line...")

        current_modes = get_blending_modes()
        self.blending_modes_text.setPlainText("\n".join(current_modes))

        layout.addWidget(self.blending_modes_text)

        self.blending_modes_tab.setLayout(layout)

    def save_settings(self):
        """Save settings to config file"""
        for script_name, checkbox in self.checkboxes.items():
            set_script_enabled(script_name, checkbox.isChecked())

        for section_name, checkbox in self.section_checkboxes.items():
            set_section_enabled(section_name, checkbox.isChecked())

        config = load_config()
        if "foreground_color" not in config:
            config["foreground_color"] = {}
        for i, color in self.colors.items():
            config["foreground_color"][f"color{i}"] = {
                "r": color.red(),
                "g": color.green(),
                "b": color.blue(),
                "a": color.alpha(),
            }
        save_config(config)

        name_color_content = self.name_color_list_text.toPlainText()
        save_name_color_list(name_color_content)

        modes_text = self.blending_modes_text.toPlainText()
        modes = [m.strip() for m in modes_text.splitlines() if m.strip()]
        save_blending_modes(modes)

        self.accept()

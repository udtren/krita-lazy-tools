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
    QSpinBox,
    QLineEdit,
    QFileDialog,
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
    get_export_settings,
    save_export_settings,
    get_export_button_font_size,
    save_export_button_font_size,
    get_export_default_folder,
    save_export_default_folder,
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

        self.image_export_tab = QWidget()
        self.setup_image_export_tab()
        self.tab_widget.addTab(self.image_export_tab, "Image Export")

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

    def setup_image_export_tab(self):
        """Setup the Image Export settings tab."""
        layout = QFormLayout()

        png = get_export_settings("png")
        jpg = get_export_settings("jpg")

        # UI section
        ui_label = QLabel("UI")
        ui_label.setStyleSheet("font-weight: bold; margin-top: 6px;")
        layout.addRow(ui_label)

        self.export_button_font_size = QSpinBox()
        self.export_button_font_size.setRange(8, 24)
        self.export_button_font_size.setSuffix(" px")
        self.export_button_font_size.setValue(get_export_button_font_size())
        layout.addRow("Button font size:", self.export_button_font_size)

        folder_row = QHBoxLayout()
        self.export_default_folder = QLineEdit()
        self.export_default_folder.setPlaceholderText("(not set)")
        self.export_default_folder.setText(get_export_default_folder())
        self._browse_btn = QPushButton("Browse…")
        self._browse_btn.setFixedWidth(70)
        self._browse_btn.clicked.connect(self._pick_default_folder)
        folder_row.addWidget(self.export_default_folder)
        folder_row.addWidget(self._browse_btn)
        layout.addRow("Default export folder:", folder_row)

        # PNG section
        png_label = QLabel("PNG")
        png_label.setStyleSheet("font-weight: bold; margin-top: 6px;")
        layout.addRow(png_label)

        self.png_compression = QSpinBox()
        self.png_compression.setRange(0, 9)
        self.png_compression.setValue(int(png.get("compression", 6)))
        self.png_compression.setToolTip("0 = no compression (fast), 9 = max compression (slow)")
        layout.addRow("Compression (0–9):", self.png_compression)

        self.png_alpha = QCheckBox("Save alpha channel")
        self.png_alpha.setChecked(bool(png.get("alpha", True)))
        layout.addRow(self.png_alpha)

        # JPEG section
        jpg_label = QLabel("JPEG")
        jpg_label.setStyleSheet("font-weight: bold; margin-top: 6px;")
        layout.addRow(jpg_label)

        self.jpg_quality = QSpinBox()
        self.jpg_quality.setRange(0, 100)
        self.jpg_quality.setValue(int(jpg.get("quality", 90)))
        self.jpg_quality.setToolTip("0 = smallest file, 100 = best quality")
        layout.addRow("Quality (0–100):", self.jpg_quality)

        self.image_export_tab.setLayout(layout)

    def _pick_default_folder(self):
        dialog = QFileDialog()
        dialog.setWindowTitle("Select default export folder")
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        current = self.export_default_folder.text()
        if current:
            dialog.setDirectory(current)
        if dialog.exec_() == QFileDialog.Accepted:
            folders = dialog.selectedFiles()
            if folders:
                self.export_default_folder.setText(folders[0])

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

        save_export_settings("png", {
            "compression": self.png_compression.value(),
            "alpha": self.png_alpha.isChecked(),
        })
        save_export_settings("jpg", {
            "quality": self.jpg_quality.value(),
        })

        save_export_button_font_size(self.export_button_font_size.value())

        save_export_default_folder(self.export_default_folder.text().strip())

        self.accept()

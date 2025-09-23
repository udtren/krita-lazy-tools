"""
Lazy Scripts Extension for Krita

This extension adds a script dropdown to the Layer Docker for running custom scripts.
"""

import os
from typing import Optional, List
from krita import Krita, Extension  # type: ignore
from PyQt5.QtWidgets import QComboBox, QHBoxLayout
from PyQt5.QtGui import QIcon, QPixmap, QColor
from lazy_tools.utils.color_scheme import ColorScheme


class LazyScripts(Extension):
    """
    Extension class that adds script execution functionality to Krita's Layer Docker.
    Allows running custom Python scripts from the scripts folder.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.scriptsComboBox: Optional[QComboBox] = None
        self.scripts_folder = os.path.join(os.path.dirname(__file__), "scripts")
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
        """Add the scripts combo box to Krita's Layer Docker."""
        try:
            layer_docker = self._find_layer_docker()
            if not layer_docker:
                return

            layout = self._find_docker_layout(layer_docker)
            if not layout:
                return

            if not self.scriptsComboBox:
                self.scriptsComboBox = self._build_scripts_combo_box()

            # Insert after the color filter combo box (at position 2)
            layout.insertWidget(2, self.scriptsComboBox)
            self.scriptsComboBox.activated.connect(self._execute_script)

        except Exception as e:
            print(f"Error adding scripts combo box to Layer Docker: {e}")

    def _find_layer_docker(self):
        """Find and return the Layer Docker widget."""
        return next(
            (w for w in Krita.instance().dockers() if w.objectName() == "KisLayerBox"),
            None,
        )

    def _find_docker_layout(self, layer_docker):
        """Find and return the layout where layer controls are located."""
        return layer_docker.findChild(QHBoxLayout, "hbox2")

    def _execute_script(self, index: int):
        """Execute the selected script or perform special actions."""
        try:
            if index == 0:  # "Reload Scripts" option
                self._reload_scripts()
                return

            # Get the script filename from combo box
            script_name = self.scriptsComboBox.itemText(index)
            script_filename = script_name + ".py"
            script_path = os.path.join(self.scripts_folder, script_filename)

            if not os.path.exists(script_path):
                print(f"Script file not found: {script_path}")
                return

            # Execute the script
            self._run_script_file(script_path, script_name)

        except Exception as e:
            print(f"Error executing script: {e}")

    def _reload_scripts(self):
        """Reload the scripts list and refresh the combo box."""
        try:
            if self.scriptsComboBox:
                # Store current selection (if any)
                current_text = self.scriptsComboBox.currentText()

                # Clear and repopulate
                self.scriptsComboBox.clear()
                self._populate_scripts_combo_box(self.scriptsComboBox)

                # Try to restore previous selection if it still exists
                if current_text and current_text != "Reload Scripts":
                    index = self.scriptsComboBox.findText(current_text)
                    if index >= 0:
                        self.scriptsComboBox.setCurrentIndex(index)

                print("Scripts list reloaded successfully")

        except Exception as e:
            print(f"Error reloading scripts: {e}")

    def _run_script_file(self, script_path: str, script_name: str):
        """Run a Python script file."""
        try:
            # Read and execute the script content
            with open(script_path, "r", encoding="utf-8") as f:
                script_content = f.read()

            # Create a namespace for the script execution
            script_globals = {
                "__name__": "__main__",
                "__file__": script_path,
                "Krita": Krita,  # Make Krita available to scripts
            }

            # Execute the script
            exec(script_content, script_globals)
            print(f"Successfully executed script: {script_name}")

        except Exception as e:
            print(f"Error running script '{script_name}': {e}")

    def _get_script_files(self) -> List[str]:
        """Get list of Python script files in the scripts folder."""
        script_files = []

        if not os.path.exists(self.scripts_folder):
            print(f"Scripts folder not found: {self.scripts_folder}")
            return script_files

        try:
            for filename in os.listdir(self.scripts_folder):
                if filename.endswith(".py") and not filename.startswith("__"):
                    # Remove .py extension for display
                    script_name = filename[:-3]
                    script_files.append(script_name)
        except Exception as e:
            print(f"Error reading scripts folder: {e}")

        return sorted(script_files)

    def _build_scripts_combo_box(self) -> QComboBox:
        """Build and configure the scripts combo box."""
        combo_box = QComboBox()
        combo_box.setAccessibleName("scriptsBox")
        combo_box.setObjectName("scriptsBox")
        combo_box.setFixedSize(ColorScheme.COMBO_SIZE)
        combo_box.setToolTip("Execute custom scripts")

        self._populate_scripts_combo_box(combo_box)
        return combo_box

    def _populate_scripts_combo_box(self, combo_box: QComboBox):
        """Populate the scripts combo box with available scripts."""
        # Add reload option first
        reload_icon = self._create_reload_icon()
        combo_box.addItem(reload_icon, "Reload Scripts")

        # Add script files (text only, no icons)
        script_files = self._get_script_files()
        for script_name in script_files:
            combo_box.addItem(script_name)

        if not script_files:
            combo_box.addItem("No Scripts Found")

    def _create_script_icon(self) -> QIcon:
        """Create an icon for the script options."""
        pixmap = QPixmap(ColorScheme.ICON_SIZE)
        pixmap.fill(QColor(100, 150, 255))  # Light blue color for scripts
        return QIcon(pixmap)

    def _create_reload_icon(self) -> QIcon:
        """Create an icon for the reload option."""
        pixmap = QPixmap(ColorScheme.ICON_SIZE)
        pixmap.fill(QColor(50, 200, 50))  # Green color for reload
        return QIcon(pixmap)

    def refresh_scripts(self):
        """Public method to refresh the scripts list."""
        if self.scriptsComboBox:
            self.scriptsComboBox.clear()
            self._populate_scripts_combo_box(self.scriptsComboBox)

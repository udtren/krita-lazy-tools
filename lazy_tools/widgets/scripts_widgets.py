"""
Scripts Widgets for Lazy Tools Docker

This module contains widgets for executing custom Python scripts.
"""

import os
from typing import List
from krita import Krita  # type: ignore
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QColor
from lazy_tools.utils.color_scheme import ColorScheme


class ScriptsSection(QWidget):
    """
    A widget containing script execution controls.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_docker = parent
        self.scripts_folder = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "scripts"
        )
        self._ensure_scripts_folder_exists()
        self.setup_ui()

    def _ensure_scripts_folder_exists(self):
        """Create the scripts folder if it doesn't exist."""
        try:
            if not os.path.exists(self.scripts_folder):
                os.makedirs(self.scripts_folder)
                print(f"Created scripts folder: {self.scripts_folder}")
            else:
                print(f"Scripts folder exists: {self.scripts_folder}")
        except Exception as e:
            print(f"Error creating scripts folder: {e}")

    def setup_ui(self):
        """Setup the scripts section UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # Reload button at the top
        reload_layout = QHBoxLayout()
        reload_layout.setContentsMargins(0, 0, 0, 0)

        self.reload_btn = QPushButton("🔄 Reload Scripts")
        self.reload_btn.setStyleSheet(
            """
            QPushButton {
                text-align: left;
                padding: 1px;
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
        self.reload_btn.setToolTip("Reload scripts list")
        self.reload_btn.clicked.connect(self._reload_scripts)
        reload_layout.addWidget(self.reload_btn)
        reload_layout.addStretch()

        layout.addLayout(reload_layout)

        # Scroll area for script buttons
        self.scripts_container = QWidget()
        self.scripts_layout = QVBoxLayout()
        self.scripts_layout.setContentsMargins(2, 2, 2, 2)
        self.scripts_layout.setSpacing(2)
        self.scripts_container.setLayout(self.scripts_layout)

        layout.addWidget(self.scripts_container)
        layout.addStretch()

        self.setLayout(layout)
        self._populate_script_buttons()

    def _populate_script_buttons(self):
        """Create buttons for each available script."""
        # Clear existing buttons
        self._clear_script_buttons()

        # Get script files
        script_files = self._get_script_files()

        if not script_files:
            # Show "No scripts found" message
            no_scripts_label = QLabel("No scripts found")
            no_scripts_label.setStyleSheet(
                "QLabel { color: #7065a7; font-style: italic; padding: 10px; }"
            )
            no_scripts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scripts_layout.addWidget(no_scripts_label)
        else:
            # Create button for each script
            for script_name in script_files:
                script_btn = QPushButton(f"▶ {script_name}")
                script_btn.setToolTip(f"Execute script: {script_name}")
                script_btn.setStyleSheet(
                    """
                    QPushButton {
                        text-align: left;
                        padding: 1px 1px;
                        color: #a3a3a3; 
                        background-color: #191919;
                    }
                    QPushButton:hover {
                        color: #a3a3a3;
                        background-color: #333333;
                    }
                    QPushButton:pressed {
                        color: #a3a3a3;
                        background-color: #555555;
                    }
                """
                )
                # Connect to execution with the script name
                script_btn.clicked.connect(
                    lambda checked, name=script_name: self._run_script(name)
                )
                self.scripts_layout.addWidget(script_btn)

        # Add stretch to push buttons to top
        self.scripts_layout.addStretch()

    def _clear_script_buttons(self):
        """Remove all existing script buttons and labels."""
        while self.scripts_layout.count():
            child = self.scripts_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

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

    def _run_script(self, script_name: str):
        """Run a script by name."""
        try:
            script_filename = script_name + ".py"
            script_path = os.path.join(self.scripts_folder, script_filename)

            if not os.path.exists(script_path):
                print(f"Script file not found: {script_path}")
                return

            # Execute the script
            self._run_script_file(script_path, script_name)

        except Exception as e:
            print(f"Error executing script: {e}")

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

    def _reload_scripts(self):
        """Reload the scripts list and refresh the buttons."""
        try:
            self._populate_script_buttons()
            print("Scripts list reloaded successfully")
        except Exception as e:
            print(f"Error reloading scripts: {e}")

    def refresh_scripts(self):
        """Public method to refresh the scripts list."""
        self._reload_scripts()

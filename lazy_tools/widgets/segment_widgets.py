"""
Segment Widgets for Krita

This module provides segmentation functionality using Florence-2 + SAM2 pipeline.
"""

import os
import tempfile
import threading
from typing import Optional
from krita import Krita, Document, Node  # type: ignore
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QProgressBar,
    QMessageBox,
    QTextEdit,
    QRadioButton,
    QButtonGroup,
    QComboBox,
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

# Import configuration from widgets package
from . import (
    VENV_PYTHON_PATH,
    LAZY_SEGMENT_SCRIPT_PATH,
    get_temp_input_path,
    get_temp_output_path,
    get_clean_subprocess_env,
    validate_paths,
    DEFAULT_OUTPUT_TYPE,
    SAM2_MODELS,
    DEFAULT_SAM2_MODEL,
    get_sam2_model_options,
    get_sam2_model_key,
)


class SegmentationWorker(QThread):
    """Worker thread for running segmentation pipeline."""

    progress_update = pyqtSignal(str)  # Progress message
    finished = pyqtSignal(str)  # Result image path
    error = pyqtSignal(str)  # Error message

    def __init__(
        self,
        image_path: str,
        prompt: str,
        output_path: str,
        output_type: str = "overlay",
        sam2_model: str = "base_plus",
    ):
        super().__init__()
        self.image_path = image_path
        self.prompt = prompt
        self.output_path = output_path
        self.output_type = output_type
        self.sam2_model = sam2_model

    def run(self):
        """Run the segmentation pipeline in a separate thread."""
        try:
            self.progress_update.emit("Initializing Florence-2 + SAM2 pipeline...")

            # Use subprocess to run the segmentation with the correct Python environment
            import subprocess
            import sys
            import os

            # Validate paths before proceeding
            path_errors = validate_paths()
            if path_errors:
                for error in path_errors:
                    self.error.emit(error)
                return

            # Run the segmentation script as subprocess
            self.progress_update.emit("Running segmentation pipeline...")

            cmd = [
                VENV_PYTHON_PATH,
                LAZY_SEGMENT_SCRIPT_PATH,
                self.image_path,
                self.prompt,
                self.output_path,
            ]

            # Add cutout flag if needed
            if self.output_type == "cutout":
                cmd.append("--cutout")

            # Add model selection if not default
            if self.sam2_model != DEFAULT_SAM2_MODEL:
                cmd.extend(["--model", self.sam2_model])

            # Get clean environment to avoid Python path conflicts with Krita
            clean_env = get_clean_subprocess_env()

            # Run the command and capture output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
                env=clean_env,  # Use clean environment
            )

            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    self.progress_update.emit(output.strip())

            # Wait for completion
            return_code = process.poll()

            if return_code == 0:
                # Check if output was created
                if os.path.exists(self.output_path):
                    self.progress_update.emit("Segmentation completed successfully!")
                    self.finished.emit(self.output_path)
                else:
                    self.error.emit(
                        "Segmentation completed but no output file was generated"
                    )
            else:
                self.error.emit(
                    f"Segmentation process failed with return code: {return_code}"
                )

        except Exception as e:
            import traceback

            self.error.emit(f"Segmentation error: {str(e)}\\n{traceback.format_exc()}")


class SegmentSection(QWidget):
    """Widget section for AI-powered segmentation using Florence-2 + SAM2."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_docker = parent
        self.worker_thread = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the segmentation section UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(1)

        # Prompt input
        prompt_layout = QVBoxLayout()
        prompt_layout.setSpacing(1)

        prompt_label = QLabel("Object to find:")
        prompt_layout.addWidget(prompt_label)

        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("e.g., girl, car, person with hat...")
        self.prompt_input.returnPressed.connect(self.run_segmentation)
        prompt_layout.addWidget(self.prompt_input)

        layout.addLayout(prompt_layout)

        # SAM2 Model selection
        model_layout = QVBoxLayout()
        model_layout.setSpacing(3)

        model_label = QLabel("SAM2 Model:")
        model_layout.addWidget(model_label)

        self.model_combo = QComboBox()
        model_options = get_sam2_model_options()
        for model_key, display_name in model_options:
            self.model_combo.addItem(display_name, model_key)

        # Set default selection
        default_index = 0
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == DEFAULT_SAM2_MODEL:
                default_index = i
                break
        self.model_combo.setCurrentIndex(default_index)

        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # Output type selection
        output_type_layout = QVBoxLayout()
        output_type_layout.setSpacing(3)

        output_type_label = QLabel("Output type:")
        output_type_layout.addWidget(output_type_label)

        radio_layout = QVBoxLayout()

        self.output_type_group = QButtonGroup()

        self.overlay_radio = QRadioButton("Red Overlay")
        self.overlay_radio.setChecked(
            DEFAULT_OUTPUT_TYPE == "overlay"
        )  # Use config default
        self.overlay_radio.setToolTip(
            "Show segmented areas with red overlay on original image"
        )
        self.output_type_group.addButton(self.overlay_radio, 0)
        radio_layout.addWidget(self.overlay_radio)

        self.cutout_radio = QRadioButton("Transparent Cutout")
        self.cutout_radio.setChecked(
            DEFAULT_OUTPUT_TYPE == "cutout"
        )  # Use config default
        self.cutout_radio.setToolTip(
            "Create cutout with transparent background (perfect for layers)"
        )
        self.output_type_group.addButton(self.cutout_radio, 1)
        radio_layout.addWidget(self.cutout_radio)

        output_type_layout.addLayout(radio_layout)
        layout.addLayout(output_type_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_segmentation)
        self.run_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: #000000;
                border: none;
                padding: 2px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        )
        button_layout.addWidget(self.run_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_segmentation)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet(
            """
            QPushButton {
                background-color: #797979;
                color: #000000;
                border: none;
                padding: 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #545454;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        )
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status text
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        self.status_text.setVisible(False)
        self.status_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #000000;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: monospace;
                font-size: 10px;
                font-color: #ffffff;
            }
        """
        )
        layout.addWidget(self.status_text)

        self.setLayout(layout)

    def run_segmentation(self):
        """Run the segmentation process."""
        try:
            # Get current document
            doc = Krita.instance().activeDocument()
            if not doc:
                QMessageBox.warning(
                    self, "No Document", "Please open a document first."
                )
                return

            # Get prompt
            prompt = self.prompt_input.text().strip()
            if not prompt:
                QMessageBox.warning(
                    self, "No Prompt", "Please enter what object to find."
                )
                return

            # Get selected output type and model
            output_type = "cutout" if self.cutout_radio.isChecked() else "overlay"
            selected_model = self.model_combo.currentData()

            # Get temporary file paths from configuration
            input_path = get_temp_input_path()
            output_path = get_temp_output_path(output_type)

            # Export current document as PNG
            self.update_status("Exporting current document...")

            # Get the flattened image as pixel data and save it
            try:
                # Get document dimensions
                width = doc.width()
                height = doc.height()

                # Get pixel data from the projection (flattened view)
                pixel_data = doc.pixelData(0, 0, width, height)

                # Convert to QImage
                from PyQt5.QtGui import QImage

                qimage = QImage(pixel_data, width, height, QImage.Format_ARGB32)

                # Convert ARGB to RGB for better compatibility
                rgb_image = qimage.convertToFormat(QImage.Format_RGB32)

                # Save as PNG
                if not rgb_image.save(input_path, "PNG"):
                    QMessageBox.critical(
                        self, "Export Error", "Failed to save document as PNG."
                    )
                    return

            except Exception as export_error:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export document: {str(export_error)}",
                )
                return

            # Start segmentation in worker thread
            self.start_processing()

            self.worker_thread = SegmentationWorker(
                input_path, prompt, output_path, output_type, selected_model
            )
            self.worker_thread.progress_update.connect(self.update_status)
            self.worker_thread.finished.connect(self.on_segmentation_finished)
            self.worker_thread.error.connect(self.on_segmentation_error)
            self.worker_thread.start()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to start segmentation: {str(e)}"
            )
            self.stop_processing()

    def cancel_segmentation(self):
        """Cancel the running segmentation."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
            self.update_status("Segmentation cancelled by user.")
            self.stop_processing()

    def start_processing(self):
        """Update UI to processing state."""
        self.run_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.status_text.setVisible(True)
        self.status_text.clear()
        self.update_status("Starting segmentation process...")

    def stop_processing(self):
        """Update UI to stopped state."""
        self.run_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        # Keep status text visible to show results

    def update_status(self, message: str):
        """Update the status text."""
        self.status_text.append(message)
        # Auto-scroll to bottom
        cursor = self.status_text.textCursor()
        cursor.movePosition(cursor.End)
        self.status_text.setTextCursor(cursor)

    def on_segmentation_finished(self, output_path: str):
        """Handle successful segmentation completion."""
        try:
            self.stop_processing()
            self.update_status(f"✅ Segmentation completed! Loading result...")

            # Load the result image as a new layer
            doc = Krita.instance().activeDocument()
            if not doc:
                self.update_status("❌ No active document to add layer to.")
                return

            # Create a new paint layer
            prompt = self.prompt_input.text().strip()
            output_type = "cutout" if self.cutout_radio.isChecked() else "overlay"
            selected_model = self.model_combo.currentData()
            model_name = SAM2_MODELS[selected_model]["name"]
            layer_name = f"AI Segment ({output_type.title()}, {model_name}): {prompt}"

            # Load the segmented image using Krita's createNodeFromPaintDevice
            from krita import QImage  # type: ignore

            # Load the result image
            qimage = QImage(output_path)
            if qimage.isNull():
                self.update_status("❌ Failed to load result image.")
                return

            # Create new paint layer
            root_node = doc.rootNode()
            paint_layer = doc.createNode(layer_name, "paintLayer")

            # Convert QImage to the format Krita expects
            if qimage.format() != QImage.Format_ARGB32:
                qimage = qimage.convertToFormat(QImage.Format_ARGB32)

            # Get image dimensions
            width = qimage.width()
            height = qimage.height()

            # Get pixel data as bytes
            ptr = qimage.constBits()
            pixel_bytes = ptr.asstring(width * height * 4)  # 4 bytes per pixel (ARGB)

            # Set the pixel data on the layer
            paint_layer.setPixelData(pixel_bytes, 0, 0, width, height)

            # Add the layer to the document
            root_node.addChildNode(paint_layer, None)

            # Refresh the document
            doc.refreshProjection()

            self.update_status(f"✅ Added new layer: '{layer_name}'")
            self.update_status("🎉 Segmentation process completed successfully!")

            # Clean up temporary files
            try:
                os.remove(output_path)
                temp_input = get_temp_input_path()
                if os.path.exists(temp_input):
                    os.remove(temp_input)
            except:
                pass  # Ignore cleanup errors

        except Exception as e:
            import traceback

            self.update_status(f"❌ Error adding layer: {str(e)}")
            self.update_status(f"Stack trace: {traceback.format_exc()}")
            QMessageBox.critical(
                self, "Layer Error", f"Failed to add segmented layer: {str(e)}"
            )

    def on_segmentation_error(self, error_message: str):
        """Handle segmentation errors."""
        self.stop_processing()
        self.update_status(f"❌ {error_message}")
        QMessageBox.critical(self, "Segmentation Error", error_message)

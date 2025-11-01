import uuid
from krita import Krita, Extension
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QCheckBox,
)

BLENDING_MODES = [
    "normal",
    "multiply",
    "screen",
    "color_dodge",
    "overlay",
    "soft_light_svg",
    "darken",
    "lighten",
]


class DuplicateLayerDialog(QDialog):
    def __init__(self, parent=None, name="", blendingMode="normal"):
        super().__init__(parent)
        self.setWindowTitle("Duplicate Layer")
        self.setMinimumWidth(300)

        # Initialize result
        self.node_name = name
        self.blending_mode = blendingMode

        # Create layout
        layout = QVBoxLayout()

        # Layer name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.name_input.setText(self.node_name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Blending mode selection
        blending_mode_layout = QHBoxLayout()
        blending_mode_label = QLabel("Blending Mode:")
        self.blending_mode_combo = QComboBox()
        self.blending_mode_combo.setEditable(True)
        self.blending_mode_combo.addItems(BLENDING_MODES)
        self.blending_mode_combo.setCurrentText(self.blending_mode)
        blending_mode_layout.addWidget(blending_mode_label)
        blending_mode_layout.addWidget(self.blending_mode_combo)
        layout.addLayout(blending_mode_layout)

        # Hide original checkbox
        self.hide_original_checkbox = QCheckBox("hide original")
        self.hide_original_checkbox.setChecked(False)
        layout.addWidget(self.hide_original_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_values(self):
        """Get the user input values"""
        node_name = self.name_input.text().strip()
        blending_mode = self.blending_mode_combo.currentText()
        hide_original = self.hide_original_checkbox.isChecked()

        return (node_name, blending_mode, hide_original)


class DuplicateLayerExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction(
            "duplicate_layer_alternative", "Duplicate Layer Alternative"
        )
        action.triggered.connect(self.DuplicateLayer)

    def DuplicateLayer(self):
        try:
            # Get the active document
            doc = Krita.instance().activeDocument()
            if not doc:
                return

            dialog = DuplicateLayerDialog(
                name=doc.activeNode().name(),
                blendingMode=doc.activeNode().blendingMode(),
            )
            if dialog.exec_() == QDialog.Accepted:
                # Get values from dialog
                (node_name, blending_mode, hide_original) = dialog.get_values()

                current_layer = doc.activeNode()

                duplicated_layer = current_layer.duplicate()
                if duplicated_layer:
                    parent = current_layer.parentNode()
                    if parent:
                        parent.addChildNode(duplicated_layer, current_layer)

                        duplicated_layer.setName(node_name)
                        duplicated_layer.setBlendingMode(blending_mode)
                        if hide_original:
                            current_layer.setVisible(False)

                        doc.setActiveNode(duplicated_layer)
                        doc.refreshProjection()
                    else:
                        print("Could not find parent node")

        except Exception as e:
            print(f"Error duplicating active layer: {e}")


# Required: Register the extension
Krita.instance().addExtension(DuplicateLayerExtension(Krita.instance()))

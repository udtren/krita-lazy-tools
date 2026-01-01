import uuid
import os
import sys
from krita import Krita, Extension, InfoObject, Selection
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

try:
    from quick_access_manager.gesture.gesture_main import (
        pause_gesture_event_filter,
        resume_gesture_event_filter,
        is_gesture_filter_paused,
    )

    GESTURE_AVAILABLE = True
except ImportError:
    GESTURE_AVAILABLE = False

# Add parent directory to path to import from lazy_tools
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.config_loader import load_name_color_list

BLENDING_MODES = [
    "normal",
    "multiply",
    "screen",
    "dodge",
    "overlay",
    "soft_light_svg",
    "hard_light",
    "darken",
    "lighten",
    "greater",
]


class NewLayerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Layer")
        self.setMinimumWidth(300)

        # Initialize result
        self.layer_name = ""
        self.layer_type = "paintlayer"

        # Create layout
        layout = QVBoxLayout()

        # Layer name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Layer Name:")
        self.name_input = QComboBox()
        self.name_input.setEditable(True)
        self.name_input.lineEdit().setPlaceholderText("auto-generate if empty")

        # Add empty string as first item
        self.name_input.addItem("")

        # Load and add names from name_color_list.txt
        content = load_name_color_list()
        if content:
            lines = content.strip().split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Parse line: "layer_name" or "layer_name, Color"
                # Extract only the name part (before comma if present)
                if "," in line:
                    name = line.split(",", 1)[0].strip()
                else:
                    name = line

                if name:
                    self.name_input.addItem(name)

        # Set current text to empty (first item)
        self.name_input.setCurrentText("")

        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Layer type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Layer Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["paintlayer", "grouplayer", "filllayer"])
        self.type_combo.setCurrentText("paintlayer")
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Blending mode selection
        blending_mode_layout = QHBoxLayout()
        blending_mode_label = QLabel("Blending Mode:")
        self.blending_mode_combo = QComboBox()
        self.blending_mode_combo.setEditable(True)
        self.blending_mode_combo.addItems(BLENDING_MODES)
        self.blending_mode_combo.setCurrentText("normal")
        blending_mode_layout.addWidget(blending_mode_label)
        blending_mode_layout.addWidget(self.blending_mode_combo)
        layout.addLayout(blending_mode_layout)

        # Add below checkbox
        self.add_below_checkbox = QCheckBox("add below")
        self.add_below_checkbox.setChecked(False)
        layout.addWidget(self.add_below_checkbox)

        # Add as child checkbox
        self.add_as_child_checkbox = QCheckBox("add as child")
        self.add_as_child_checkbox.setChecked(False)
        layout.addWidget(self.add_as_child_checkbox)

        # inheritAlpha
        self.inherit_alpha_checkbox = QCheckBox("inherit alpha")
        self.inherit_alpha_checkbox.setChecked(False)
        layout.addWidget(self.inherit_alpha_checkbox)

        # PassThrough
        self.pass_through_checkbox = QCheckBox("pass through")
        self.pass_through_checkbox.setChecked(False)
        layout.addWidget(self.pass_through_checkbox)

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
        name = self.name_input.currentText().strip()
        layer_type = self.type_combo.currentText()
        blending_mode = self.blending_mode_combo.currentText()
        add_below = self.add_below_checkbox.isChecked()
        add_as_child = self.add_as_child_checkbox.isChecked()
        inherit_alpha = self.inherit_alpha_checkbox.isChecked()
        pass_through = self.pass_through_checkbox.isChecked()

        # Generate auto name if empty
        if not name:
            if layer_type == "paintlayer":
                name = f"Paint-{uuid.uuid4().hex[:4]}"
            elif layer_type == "grouplayer":
                name = f"Group-{uuid.uuid4().hex[:4]}"
            elif layer_type == "filllayer":
                name = f"Fill-{uuid.uuid4().hex[:4]}"

        return (
            name,
            layer_type,
            blending_mode,
            add_below,
            add_as_child,
            inherit_alpha,
            pass_through,
        )


class AddNewLayerExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction(
            "add_new_layer_alternative", "Add New Layer Alternative"
        )
        action.triggered.connect(self.AddNewLayer)

    def AddNewLayer(self):
        try:
            # Get active document
            application = Krita.instance()
            doc = application.activeDocument()
            if not doc:
                print("No active document")
                return

            # Pause gesture if available and not already paused
            should_resume_gesture = False
            if GESTURE_AVAILABLE and not is_gesture_filter_paused():
                pause_gesture_event_filter()
                should_resume_gesture = True

            # Show dialog
            dialog = NewLayerDialog()
            result = dialog.exec_()

            # Resume gesture if we paused it
            if should_resume_gesture:
                resume_gesture_event_filter()

            if result == QDialog.Accepted:
                # Get values from dialog
                (
                    layer_name,
                    layer_type,
                    blending_mode,
                    add_below,
                    add_as_child,
                    inherit_alpha,
                    pass_through,
                ) = dialog.get_values()

                # Create new node
                if layer_type == "paintlayer":
                    new_node = doc.createNode(layer_name, layer_type)
                elif layer_type == "grouplayer":
                    new_node = doc.createGroupLayer(layer_name)
                    if pass_through:
                        new_node.setPassThroughMode(True)
                elif layer_type == "filllayer":
                    foreground_color_xml = (
                        application.activeWindow()
                        .activeView()
                        .foregroundColor()
                        .toXML()
                    )
                    modified_xml = foreground_color_xml.replace(
                        "<Color bitdepth=", "<!DOCTYPE color>\n<color channeldepth="
                    )
                    modified_xml = modified_xml.replace("</Color>", "</color>")
                    infoObject = InfoObject()
                    infoObject.setProperty("color", modified_xml)
                    selection = Selection()
                    selection.select(0, 0, doc.width(), doc.height(), 255)

                    new_node = doc.createFillLayer(
                        layer_name, "color", infoObject, selection
                    )
                else:
                    new_node = doc.createNode(layer_name, layer_type)

                new_node.setBlendingMode(blending_mode)

                if inherit_alpha:
                    new_node.setInheritAlpha(True)

                # Get root node and active node
                root_node = doc.rootNode()
                active_node = doc.activeNode()

                # Add the new node
                if active_node:
                    # Check if "add as child" is checked and active node is a group
                    if add_as_child and active_node.type() == "grouplayer":
                        # Add as child inside the group layer
                        active_node.addChildNode(new_node, None)
                    else:
                        parent = active_node.parentNode()
                        if add_below:
                            # Add below the active node
                            child_nodes = parent.childNodes()
                            active_index = child_nodes.index(active_node)
                            if active_index > 0:
                                # Insert below by adding at the position of the node below
                                below_node = child_nodes[active_index - 1]
                                parent.addChildNode(new_node, below_node)
                            elif active_index == 0:
                                active_node_duplicate = active_node.duplicate()
                                parent.addChildNode(active_node_duplicate, active_node)
                                doc.refreshProjection()
                                child_nodes = parent.childNodes()
                                below_node = child_nodes[
                                    child_nodes.index(active_node_duplicate) - 1
                                ]
                                parent.addChildNode(new_node, below_node)
                                active_node.remove()
                                doc.refreshProjection()
                            else:
                                # Active node is at the bottom, add at bottom
                                parent.addChildNode(new_node, None)
                        else:
                            # Add above the active node (default)
                            parent.addChildNode(new_node, active_node)
                else:
                    root_node.addChildNode(new_node, None)

                # Set the new node as active
                doc.setActiveNode(new_node)

                # Refresh the document
                doc.refreshProjection()

                print(f"Created new layer: {layer_name} ({layer_type})")

        except Exception as e:
            print(f"Error creating new layer: {e}")

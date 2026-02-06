from krita import Krita
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QWidget,
)
from PyQt6.QtCore import Qt


class FilterConfigViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Layer Configuration Viewer")
        self.resize(500, 400)

        # Create layout
        layout = QVBoxLayout()

        # Title label
        self.title_label = QLabel("<b>Current Filter Layer Information</b>")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Filter name label
        self.filter_name_label = QLabel("Filter Name: ")
        layout.addWidget(self.filter_name_label)

        # Node name label
        self.node_name_label = QLabel("Layer Name: ")
        layout.addWidget(self.node_name_label)

        # Configuration display (text edit for XML)
        self.config_label = QLabel("Configuration Parameters:")
        layout.addWidget(self.config_label)

        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        layout.addWidget(self.config_text)

        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_filter_config)
        layout.addWidget(self.refresh_btn)

        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)

        # Load initial data
        self.load_filter_config()

    def load_filter_config(self):
        """Load and display the current filter layer configuration"""
        doc = Krita.instance().activeDocument()

        if not doc:
            self.show_error("No active document")
            return

        node = doc.activeNode()

        if not node:
            self.show_error("No active node")
            return

        if node.type() != "filterlayer":
            self.show_error(f"Active node is not a filter layer.\nType: {node.type()}")
            return

        # Get filter configuration
        filter_config = node.filter()
        config_info = filter_config.configuration()

        # Display information
        self.filter_name_label.setText(f"<b>Filter Name:</b> {filter_config.name()}")
        self.node_name_label.setText(f"<b>Layer Name:</b> {node.name()}")

        # Get all properties from InfoObject
        result = ""
        properties = config_info.properties()

        if properties:
            result += "Configuration Properties:\n"
            result += "-" * 40 + "\n"
            for key in properties:
                value = config_info.property(key)
                result += f"{key}: {value}\n"
        else:
            result += "No properties found in configuration."

        self.config_text.setPlainText(result)

    def show_error(self, message):
        """Display error message"""
        self.filter_name_label.setText("<b>Filter Name:</b> N/A")
        self.node_name_label.setText("<b>Layer Name:</b> N/A")
        self.config_text.setPlainText(f"Error: {message}")


# Create and show the dialog
dialog = FilterConfigViewer()
dialog.exec()

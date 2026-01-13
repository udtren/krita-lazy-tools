"""
Show Current Brush Preset XML

This script displays the XML data of the current brush preset in a popup dialog.
The XML data is retrieved using Krita's Preset.toXML() method.
"""

from krita import Krita, Preset
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt


class PresetXMLDialog(QDialog):
    """Dialog window to display brush preset XML data"""

    def __init__(self, xml_data, preset_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Brush Preset XML: {preset_name}")
        self.setMinimumSize(800, 600)

        # Create layout
        layout = QVBoxLayout()

        # Create text edit widget for XML display
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(xml_data)
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)

        # Use monospace font for better XML readability
        font = self.text_edit.font()
        font.setFamily("Courier New")
        font.setPointSize(10)
        self.text_edit.setFont(font)

        layout.addWidget(self.text_edit)

        # Create button layout
        button_layout = QHBoxLayout()

        # Copy button
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_button)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def copy_to_clipboard(self):
        """Copy the XML content to clipboard"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())


def remove_cdata_from_xml(xml_string):
    """
    Remove CDATA content from resource tags that have md5sum attribute.
    This avoids displaying huge base64-encoded image data.

    Args:
        xml_string: The XML string to process

    Returns:
        Modified XML string with CDATA content removed from resource tags
    """
    import re

    # Pattern to match <resource> tags with md5sum attribute and CDATA content
    # This matches:
    # 1. Opening resource tag with md5sum attribute
    # 2. CDATA section with large image data
    # 3. Closing resource tag
    pattern = r'(<resource[^>]*md5sum="[^"]*">)<!\[CDATA\[.*?\]\]>(</resource>)'

    # Replace CDATA content with a placeholder, keeping the resource tag structure
    cleaned_xml = re.sub(
        pattern,
        r'\1<![CDATA[[REMOVED - Contains large image data]]]>\2',
        xml_string,
        flags=re.DOTALL
    )

    return cleaned_xml


def show_current_preset_xml():
    """
    Display the XML data of the current brush preset in a popup dialog.
    """
    try:
        # Get Krita instance
        app = Krita.instance()

        # Get active view
        active_view = app.activeWindow().activeView() if app.activeWindow() else None
        if not active_view:
            print("No active view found")
            return

        # Get current brush preset resource
        current_preset_resource = active_view.currentBrushPreset()
        if not current_preset_resource:
            print("No current brush preset found")
            return

        # Get preset name
        preset_name = current_preset_resource.name()

        # Convert resource to Preset object
        preset = Preset(current_preset_resource)

        # Get XML data from preset
        xml_data = preset.toXML()

        if not xml_data:
            print(f"No XML data available for preset: {preset_name}")
            return

        # Remove CDATA content to avoid displaying huge image data
        cleaned_xml = remove_cdata_from_xml(xml_data)

        # Create and show dialog
        dialog = PresetXMLDialog(cleaned_xml, preset_name)
        dialog.exec_()

    except Exception as e:
        print(f"Error showing preset XML: {e}")
        import traceback
        traceback.print_exc()


# Execute the function
if __name__ == "__main__":
    show_current_preset_xml()

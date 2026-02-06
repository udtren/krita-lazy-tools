from krita import *
from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon


class SelectionMaskThumbnailButton(QPushButton):
    """Custom button that displays a selection mask thumbnail"""

    def __init__(self, selection_mask, parent=None):
        super().__init__(parent)
        self.selection_mask = selection_mask
        self.setFixedSize(64, 64)
        self.setToolTip(selection_mask.name())

        # Generate and set thumbnail
        thumbnail = self.generate_thumbnail()
        if thumbnail:
            self.setIcon(QIcon(thumbnail))
            self.setIconSize(QSize(64, 64))
        else:
            self.setText(selection_mask.name())

    def generate_thumbnail(self):
        """Generate thumbnail from selection mask"""
        try:
            # Get thumbnail from the node (returns QImage directly)
            qimage = self.selection_mask.thumbnail(64, 64)

            if qimage and not qimage.isNull():
                pixmap = QPixmap.fromImage(qimage)
                return pixmap

        except Exception as e:
            print(f"Error generating thumbnail for {self.selection_mask.name()}: {e}")

        return None


class SelectionMaskPopup(QDialog):
    """Popup window showing all selection masks in a grid"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selection Masks")

        # Get Krita instance and document
        self.app = Krita.instance()
        self.doc = self.app.activeDocument()

        self.setup_ui()
        self.load_selection_masks()
        self.adjust_size()

    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create container widget for grid
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(10)

        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)

    def load_selection_masks(self):
        """Load all selection masks from the selection_mask_group"""
        if not self.doc:
            label = QLabel("No active document")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(label, 0, 0, 1, 4)
            return

        # Find the selection mask group
        selection_mask_group = self.doc.nodeByName("Selection_Mask_Group")

        if not selection_mask_group:
            label = QLabel("No 'Selection_Mask_Group' found")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(label, 0, 0, 1, 4)
            return

        # Get all child nodes (selection masks)
        selection_masks = selection_mask_group.childNodes()

        if not selection_masks:
            label = QLabel("No selection masks found")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(label, 0, 0, 1, 4)
            return

        # Add thumbnails to grid (4 columns)
        row = 0
        col = 0

        for mask in selection_masks:
            # Create thumbnail button
            btn = SelectionMaskThumbnailButton(mask)
            btn.clicked.connect(lambda checked, m=mask: self.activate_selection(m))

            # Add to grid
            self.grid_layout.addWidget(btn, row, col)

            # Update position
            col += 1
            if col >= 6:
                col = 0
                row += 1

    def activate_selection(self, selection_mask):
        """Activate the selection from the clicked mask"""
        try:
            if not self.doc:
                return

            # Get the selection from the mask
            selection = selection_mask.selection()

            if selection:
                # Set the document's selection
                self.doc.setSelection(selection)

                # Refresh the document
                self.doc.refreshProjection()
        except Exception as e:
            print(f"Error activating selection: {e}")

    def adjust_size(self):
        """Adjust window size based on content"""
        # Get the number of selection masks
        if not self.doc:
            self.resize(400, 200)
            return

        selection_mask_group = self.doc.nodeByName("Selection_Mask_Group")
        if not selection_mask_group:
            self.resize(400, 200)
            return

        selection_masks = selection_mask_group.childNodes()
        if not selection_masks:
            self.resize(400, 200)
            return

        # Calculate required size
        num_masks = len(selection_masks)
        num_rows = (num_masks + 5) // 6  # Ceiling division for 6 columns
        num_cols = min(num_masks, 6)

        # Calculate width and height
        # Width: (thumbnail_width * columns) + (spacing * (columns - 1)) + margins + scrollbar
        width = (64 * num_cols) + (10 * (num_cols - 1)) + 50
        # Height: (thumbnail_height * rows) + (spacing * (rows - 1)) + margins + title bar
        height = (64 * num_rows) + (10 * (num_rows - 1)) + 70

        # Cap maximum size
        max_width = 600
        max_height = 700

        width = min(width, max_width)
        height = min(height, max_height)

        self.resize(width, height)


def create_selection_mask_popup():
    """Main entry point"""
    app = Krita.instance()

    # Create and show the popup (non-modal)
    popup = SelectionMaskPopup(app.activeWindow().qwindow())
    popup.show()


class CreateSelectionMaskPopup(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        """Create menu actions"""
        action = window.createAction(
            "create_selection_mask_popup",
            "Create Selection Mask Popup",
            "tools/scripts",
        )
        action.triggered.connect(lambda: create_selection_mask_popup())

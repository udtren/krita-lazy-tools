from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QSize


class ColorScheme:
    """Color scheme constants based on Krita's KisNodeViewColorScheme.cpp"""

    # Color definitions with their corresponding indices
    COLORS = {
        0: QColor(Qt.GlobalColor.transparent),  # None/Transparent
        1: QColor(91, 173, 220),  # Blue
        2: QColor(151, 202, 63),  # Green
        3: QColor(247, 229, 61),  # Yellow
        4: QColor(255, 170, 63),  # Orange
        5: QColor(177, 102, 63),  # Brown
        6: QColor(238, 50, 51),  # Red
        7: QColor(191, 106, 209),  # Purple
        8: QColor(118, 119, 114),  # Grey
    }

    # Icon size for combo box items
    ICON_SIZE = QSize(20, 20)
    COMBO_SIZE = QSize(43, 32)
    BORDER_WIDTH = 2

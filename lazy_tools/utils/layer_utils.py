"""
Layer Utilities for Krita

This module provides utility functions for working with Krita layers and documents.
"""

from typing import Optional, List
from krita import Krita, Document, Node, Window, View  # type: ignore


def get_current_layer() -> Optional[Node]:
    """
    Get the currently active layer/node.

    Returns:
        The active node/layer, or None if no document is open.
    """
    krita_instance = Krita.instance()
    active_document = krita_instance.activeDocument()

    if not active_document:
        return None

    current_layer = active_document.activeNode()
    return current_layer


def get_selected_layers() -> List[Node]:
    """
    Get all currently selected layers/nodes.

    Returns:
        List of selected nodes, or empty list if none are selected.
    """
    krita_instance = Krita.instance()
    active_window = krita_instance.activeWindow()

    if not active_window:
        return []

    active_view = active_window.activeView()

    if not active_view:
        return []

    selected_nodes = active_view.selectedNodes()
    return selected_nodes if selected_nodes else []

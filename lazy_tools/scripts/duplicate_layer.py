"""
Sample Script: Duplicate Current Layer
This script duplicates the currently active layer.
"""

from krita import Krita


def main():
    """Main function to duplicate the current layer."""
    try:
        # Get the active document
        doc = Krita.instance().activeDocument()
        if not doc:
            print("No active document found")
            return

        # Get the current active layer
        current_layer = doc.activeNode()
        if not current_layer:
            print("No active layer found")
            return

        # Duplicate the layer
        duplicated_layer = current_layer.duplicate()
        if duplicated_layer:
            # Insert the duplicated layer above the original
            parent = current_layer.parentNode()
            if parent:
                parent.addChildNode(duplicated_layer, current_layer)
                duplicated_layer.setName(current_layer.name() + " Copy")
                print(f"Successfully duplicated layer: {current_layer.name()}")
            else:
                print("Could not find parent node")
        else:
            print("Failed to duplicate layer")

        # Refresh the document
        doc.refreshProjection()

    except Exception as e:
        print(f"Error duplicating layer: {e}")


# Execute the main function
if __name__ == "__main__":
    main()

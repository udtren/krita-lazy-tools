"""
Duplicate Active Layer Script

This script:
1. Duplicates the currently active layer or group (Krita auto-activates the duplicate)
2. Moves one layer down to the original layer and hides it
3. Moves back up to activate the new duplicate layer
"""

from krita import Krita


def duplicate_active_layer():
    """
    Duplicate the active layer/group using Krita's navigation.
    """
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

        duplicated_layer = current_layer.duplicate()
        if duplicated_layer:
            # Insert the duplicated layer above the original
            parent = current_layer.parentNode()
            if parent:
                parent.addChildNode(duplicated_layer, current_layer)
                duplicated_layer.setName(current_layer.name() + " Copy")
                print(f"Successfully duplicated layer: {current_layer.name()}")

                # Hide the original layer directly (no need to find it)
                current_layer.setVisible(False)

                # Set the duplicated layer as active using the document
                doc.setActiveNode(duplicated_layer)

                # Refresh the document to show changes
                doc.refreshProjection()

                print(f"Hidden original layer: {current_layer.name()}")
                print(f"Activated duplicate layer: {duplicated_layer.name()}")
            else:
                print("Could not find parent node")

    except Exception as e:
        print(f"Error duplicating active layer: {e}")
        import traceback

        traceback.print_exc()


# Execute the function
if __name__ == "__main__":
    duplicate_active_layer()

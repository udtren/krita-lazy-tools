"""
Sample Script: Create New Paint Layer
This script creates a new paint layer above the current layer.
"""

from krita import Krita


def main():
    """Main function to create a new paint layer."""
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

        # Create a new paint layer
        new_layer = doc.createNode("New Paint Layer", "paintlayer")
        if new_layer:
            # Add the new layer above the current layer
            parent = current_layer.parentNode()
            if parent:
                parent.addChildNode(new_layer, current_layer)

                # Set the new layer as active
                doc.setActiveNode(new_layer)

                print(f"Successfully created new paint layer")
            else:
                print("Could not find parent node")
        else:
            print("Failed to create new layer")

        # Refresh the document
        doc.refreshProjection()

    except Exception as e:
        print(f"Error creating new layer: {e}")


# Execute the main function
if __name__ == "__main__":
    main()

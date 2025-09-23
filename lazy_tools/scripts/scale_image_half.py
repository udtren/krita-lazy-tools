"""
Scale Image to Half Size Script

This script scales the active document to 50% of its original width and height
using Krita's scaleImage API with high-quality Bicubic interpolation.
"""

from krita import Krita


def scale_image_to_half():
    """
    Scale the active document to 50% of its original size.
    """
    try:
        # Get active document
        doc = Krita.instance().activeDocument()
        if not doc:
            print("No active document found")
            return

        # Get current dimensions
        current_width = doc.width()
        current_height = doc.height()
        current_xres = doc.xRes()
        current_yres = doc.yRes()

        print(f"Original size: {current_width} x {current_height} pixels")
        print(f"Original resolution: {current_xres} x {current_yres} DPI")

        # Calculate new dimensions (50% of original)
        new_width = int(current_width * 0.5)
        new_height = int(current_height * 0.5)

        print(f"Scaling to: {new_width} x {new_height} pixels (50% of original)")

        # Scale the image using Krita's scaleImage API
        doc.scaleImage(
            new_width,  # new width in pixels
            new_height,  # new height in pixels
            int(current_xres),  # convert float to int for horizontal DPI
            int(current_yres),  # convert float to int for vertical DPI
            "Bicubic",  # high-quality scaling algorithm
        )

        # Refresh the document to show changes
        doc.refreshProjection()

        print(f"Successfully scaled image to 50% size: {new_width} x {new_height}")
        print("All layers have been scaled proportionally")

    except Exception as e:
        print(f"Error scaling image: {e}")
        import traceback

        traceback.print_exc()


# Execute the function
if __name__ == "__main__":
    scale_image_to_half()

from krita import *

APPLICATION = Krita.instance()


def get_active_document():
    """Helper function to get the active document"""
    return APPLICATION.activeDocument()


def create_check_group():
    """Create _Check group with desaturate and posterize filter layers"""
    activeDoc = get_active_document()

    # Create the group layer
    checkGroup = activeDoc.createGroupLayer("_Check")

    # Set blend mode to "pass through"
    checkGroup.setPassThroughMode(True)

    # Add group to document
    rootNode = activeDoc.rootNode()
    rootNode.addChildNode(checkGroup, None)

    # Create desaturate filter layer
    desaturateFilter = APPLICATION.filter("desaturate")
    if desaturateFilter:
        desaturateConfig = InfoObject()
        desaturateConfig.setProperty("type", 0)
        desaturateFilter.setConfiguration(desaturateConfig)

        # Create selection for entire document
        selection = Selection()
        selection.select(0, 0, activeDoc.width(), activeDoc.height(), 255)

        # Create filter layer
        desaturateLayer = activeDoc.createFilterLayer(
            "desaturate", desaturateFilter, selection
        )
        if desaturateLayer:
            checkGroup.addChildNode(desaturateLayer, None)
            print("Desaturate filter layer added")
    else:
        print("Desaturate filter not found!")

    # Create posterize filter layer
    posterizeFilter = APPLICATION.filter("posterize")
    if posterizeFilter:
        posterizeConfig = InfoObject()
        posterizeConfig.setProperty("steps", 8)
        posterizeFilter.setConfiguration(posterizeConfig)

        # Create selection for entire document
        selection = Selection()
        selection.select(0, 0, activeDoc.width(), activeDoc.height(), 255)

        # Create filter layer
        posterizeLayer = activeDoc.createFilterLayer(
            "posterize", posterizeFilter, selection
        )
        if posterizeLayer:
            checkGroup.addChildNode(posterizeLayer, None)
            print("Posterize filter layer added")
    else:
        print("Posterize filter not found!")

    # Refresh the document
    activeDoc.refreshProjection()

    print("_Check group created successfully!")


# Run the script
create_check_group()

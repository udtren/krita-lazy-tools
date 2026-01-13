from krita import Krita

application = Krita.instance()
activeDoc = application.activeDocument()
currentLayer = activeDoc.activeNode()

# First, get the Filter object by name (not a string!)
filterObj = application.filter("gaussian blur")

if filterObj:
    # Create filter configuration
    filterConfig = InfoObject()
    filterConfig.setProperty("horizRadius", 15.78)
    filterConfig.setProperty("vertRadius", 15.78)
    filterConfig.setProperty("lockAspect", True)

    # Create selection (required parameter)
    s = Selection()
    s.select(0, 0, activeDoc.width(), activeDoc.height(), 255)

    # Create the filter mask using Filter object (NOT string)
    filterMask = activeDoc.createFilterMask("Gaussian Blur Mask", filterObj, s)

    # Add the filter mask to the current layer as a child node
    if filterMask:
        currentLayer.addChildNode(filterMask, None)
        activeDoc.refreshProjection()
        print("Filter mask created successfully!")
else:
    print("Filter not found!")


def gaussian_blur_filter_mask(
    horizRadius: float = 15.78,
    vertRadius: float = 15.78,
    name: str = "Gaussian Blur Mask",
) -> "FilterMask":
    """Create a Gaussian blur filter mask"""
    activeDoc = get_active_document()
    filterObj = APPLICATION.filter("gaussian blur")

    if not filterObj:
        print("Gaussian blur filter not found!")
        return None

    # Get configuration from the filter object
    filterConfig = filterObj.configuration()

    # Set properties
    filterConfig.setProperty("horizRadius", horizRadius)
    filterConfig.setProperty("vertRadius", vertRadius)
    filterConfig.setProperty("lockAspect", True)

    # Set configuration back to filter
    filterObj.setConfiguration(filterConfig)

    # Create selection for entire document
    s = Selection()
    s.select(0, 0, activeDoc.width(), activeDoc.height(), 255)

    # Create the filter mask
    filterMask = activeDoc.createFilterMask(name, filterObj, s)
    return filterMask


def levels_filter_mask(
    mode: str = "lightness",
    blackvalue: int = 0,
    whitevalue: int = 255,
    gammavalue: float = 1.0,
    outblackvalue: int = 0,
    outwhitevalue: int = 255,
    redchannel: str = "0;1;1;0;1",
    greenchannel: str = "0;1;1;0;1",
    bluechannel: str = "0;1;1;0;1",
) -> FilterMask:
    activeDoc = ActiveDocument
    filterObj = APPLICATION.filter("levels")
    if not filterObj:
        print("Levels filter not found!")
        return None

    # Get the configuration FROM the filter object
    filterConfig = filterObj.configuration()

    # Set properties on the existing configuration
    filterConfig.setProperty("blackvalue", blackvalue)
    filterConfig.setProperty("whitevalue", whitevalue)
    filterConfig.setProperty("gammavalue", gammavalue)
    filterConfig.setProperty("outblackvalue", outblackvalue)
    filterConfig.setProperty("outwhitevalue", outwhitevalue)
    filterConfig.setProperty("mode", mode)
    filterConfig.setProperty("histogram_mode", "linear")
    filterConfig.setProperty("number_of_channels", 8)

    lightness_value = f"{(blackvalue/255)};1;1;0;1"
    filterConfig.setProperty("lightness", lightness_value)

    filterConfig.setProperty("channel_0", "0;1;1;0;1")
    filterConfig.setProperty("channel_1", redchannel)
    filterConfig.setProperty("channel_2", greenchannel)
    filterConfig.setProperty("channel_3", bluechannel)
    filterConfig.setProperty("channel_4", "0;1;1;0;1")
    filterConfig.setProperty("channel_5", "0;1;1;0;1")
    filterConfig.setProperty("channel_6", "0;1;1;0;1")
    filterConfig.setProperty("channel_7", "0;1;1;0;1")

    # Set the configuration back on the filter
    filterObj.setConfiguration(filterConfig)

    selection = Selection()
    selection.select(0, 0, activeDoc.width(), activeDoc.height(), 255)

    filterMask = activeDoc.createFilterMask("Levels Mask", filterObj, selection)

    return filterMask

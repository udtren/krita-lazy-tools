import platform
from krita import Krita, Extension  # type: ignore
from .lazy_color import LazyColorLabel
from .lazy_color_filter import LazyColorFilter
from .lazy_tools_docker import LazyToolsDockerFactory
from .e_scripts.duplicate import DuplicateLayerExtension
from .e_scripts.new_layer import AddNewLayerExtension
from .e_scripts.color_pick import ScreenColorPicker
from .e_scripts.group_expand import ExpandAllGroups
from .e_scripts.group_fold import FolderAllGroups
from .e_scripts.deselect_alt import DeselectAlternative
from .e_scripts.selection_mask import CreateSelectionMaskAlternative
from .e_scripts.selection_mask_popup import CreateSelectionMaskPopup
from .e_scripts.rename import RenameAlternative
from .e_scripts.set_color import (
    SetForegroundColor1,
    SetForegroundColor2,
    SetForegroundColor3,
    SetForegroundColor4,
    SetForegroundColor5,
    SetForegroundColor6,
    SetForegroundColor7,
    SetForegroundColor8,
    SetForegroundColor9,
)
from .config.config_loader import get_script_enabled, ensure_config_exists


# Ensure config file exists with default settings
ensure_config_exists()


class LazyToolsExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.lazy_color_filter_docker_factory = None

    def setup(self):
        """Setup the extension and register docker factories"""
        self.lazy_color_filter_docker_factory = LazyToolsDockerFactory()
        Krita.instance().addDockWidgetFactory(self.lazy_color_filter_docker_factory)

    def createActions(self, window):
        """Called after Krita window is initialized"""
        # This method can be used for additional initialization if needed
        pass


# Register all extensions with Krita
app = Krita.instance()
extensions = [
    LazyColorLabel,
    LazyColorFilter,
    LazyToolsExtension,
    ExpandAllGroups,
    FolderAllGroups,
    AddNewLayerExtension,
    RenameAlternative,
    DuplicateLayerExtension,
    DeselectAlternative,
    CreateSelectionMaskAlternative,
    CreateSelectionMaskPopup,
    SetForegroundColor1,
    SetForegroundColor2,
    SetForegroundColor3,
    SetForegroundColor4,
    SetForegroundColor5,
    SetForegroundColor6,
    SetForegroundColor7,
    SetForegroundColor8,
    SetForegroundColor9,
]

# Conditionally add ScreenColorPicker based on config (Windows only)
if platform.system() == "Windows" and get_script_enabled("screen_color_picker"):
    extensions.append(ScreenColorPicker)

for extension_class in extensions:
    app.addExtension(extension_class(app))

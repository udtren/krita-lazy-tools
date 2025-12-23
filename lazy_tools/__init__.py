from krita import Krita, Extension  # type: ignore
from .lazy_color import LazyColorLabel
from .lazy_color_filter import LazyColorFilter
from .lazy_scripts import LazyScripts
from .lazy_tools_docker import LazyToolsDockerFactory
from .e_scripts.duplicate import DuplicateLayerExtension
from .e_scripts.new_layer import AddNewLayerExtension
from .e_scripts.color_pick import ScreenColorPicker
from .e_scripts.group_expand import ExpandAllGroups
from .e_scripts.group_fold import FolderAllGroups
from .e_scripts.deselect_alt import DeselectAlternative
from .e_scripts.selection_mask import CreateSelectionMaskAlternative
from .e_scripts.selection_mask_popup import CreateSelectionMaskPopup


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
    DuplicateLayerExtension,
    ScreenColorPicker,
    DeselectAlternative,
    CreateSelectionMaskAlternative,
    CreateSelectionMaskPopup,
]

for extension_class in extensions:
    app.addExtension(extension_class(app))

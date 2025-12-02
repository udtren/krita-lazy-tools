from krita import Krita, Extension  # type: ignore
from .lazy_color import LazyColorLabel
from .lazy_color_filter import LazyColorFilter
from .lazy_scripts import LazyScripts
from .lazy_tools_docker import LazyToolsDockerFactory
from .e_scripts.duplicate import *
from .e_scripts.new_layer import *
from .e_scripts.color_pick import *
from .e_scripts.group_expand import *
from .e_scripts.group_fold import *
from .e_scripts.deselect_alt import *


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
Krita.instance().addExtension(LazyColorLabel(Krita.instance()))
Krita.instance().addExtension(LazyColorFilter(Krita.instance()))
Krita.instance().addExtension(LazyToolsExtension(Krita.instance()))
Krita.instance().addExtension(ExpandAllGroups(Krita.instance()))
Krita.instance().addExtension(FolderAllGroups(Krita.instance()))
Krita.instance().addExtension(AddNewLayerExtension(Krita.instance()))
Krita.instance().addExtension(DuplicateLayerExtension(Krita.instance()))
Krita.instance().addExtension(ScreenColorPicker(Krita.instance()))
Krita.instance().addExtension(DeselectAlternative(Krita.instance()))

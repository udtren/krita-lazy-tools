# Krita Custom Export Plugin Analysis
> Based on the [Direct Export](https://github.com/cesarsampedro/DirectExport) plugin (v1.03)

## Overview

This document analyzes how the Direct Export pykrita plugin implements a custom image export workflow in Krita. It covers every layer of the plugin — from file structure to Krita API calls — so it can serve as a reference for writing a similar export plugin.

---

## File Structure

```
Direct_Export/
├── actions/
│   └── direct_export.action          # Action collection XML (shortcut metadata)
└── pykrita/
    ├── direct_export.desktop         # Plugin registration descriptor
    └── direct_export/
        ├── __init__.py               # Package entry: from .direct_export import *
        ├── direct_export.py          # All plugin logic (539 lines)
        └── Manual.html               # User-facing documentation
```

---

## 1. Plugin Registration

### `.desktop` file (`pykrita/direct_export.desktop`)

This is the minimum required file for Krita to discover a Python plugin.

```ini
[Desktop Entry]
Type=Service
ServiceTypes=Krita/PythonPlugin
X-KDE-Library=direct_export       # Must match the folder name under pykrita/
X-Python-2-Compatible=false
X-Krita-Manual=Manual.html        # Optional: links to help doc
Name=Direct Export
Comment=...
```

**Key rule:** `X-KDE-Library` must exactly match the subfolder name inside `pykrita/`. Krita loads `pykrita/<name>/__init__.py` as the plugin entry point.

---

## 2. Plugin Entry Point

### `__init__.py`

```python
from .direct_export import *
```

The simplest possible entry — re-exports everything from the main module. Registration code (calling `Krita.instance().addExtension()` and `addDockWidgetFactory()`) runs at module import time inside `direct_export.py`.

---

## 3. Action Definition

### `actions/direct_export.action`

An XML file placed in `actions/` next to `pykrita/`. Krita reads it to populate the keyboard shortcut editor.

```xml
<ActionCollection version="2" name="Scripts">
  <Actions category="Scripts">
    <Action name="direct_export">
      <text>Direct Export</text>
      <toolTip>Auto-export image to the correct directory.</toolTip>
      <shortcut></shortcut>          <!-- empty = user assigns their own -->
      <isCheckable>false</isCheckable>
    </Action>
  </Actions>
</ActionCollection>
```

**Key rule:** The `name` attribute in the XML must match the first argument passed to `window.createAction()` in the `Extension.createActions()` method.

---

## 4. Krita Extension (Actions & Shortcuts)

### Class: `DEExtension(Extension)`

Subclassing `Extension` is how a plugin registers keyboard actions.

```python
class DEExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass  # required override, can be empty

    def createActions(self, window):
        action = window.createAction(
            "direct_export",   # must match .action XML name
            "Direct Export"    # display name
        )
        action.triggered.connect(self.triggerExport)

    def triggerExport(self):
        # Find the docker by objectName and call its method
        mainWindow = Krita.instance().activeWindow()
        for docker in mainWindow.dockers():
            if docker.objectName() == "direct_export":
                docker.export()
                break

# Registration at module level:
Krita.instance().addExtension(DEExtension(Krita.instance()))
```

**Key points:**
- `setup()` is called once at startup; `createActions(window)` is called per window.
- The extension finds its docker by `objectName`, which is set by `DockWidgetFactoryBase.__init__()` (first argument).
- Both registration calls (`addExtension`, `addDockWidgetFactory`) must happen at module import time, not deferred.

---

## 5. Docker (Persistent UI Panel)

### Classes: `DEEDocker(DockWidget)` + `DEEDockerFactory(DockWidgetFactoryBase)`

```python
class DEEDockerFactory(DockWidgetFactoryBase):
    def __init__(self):
        # "direct_export" becomes the docker's objectName()
        super().__init__("direct_export", DockWidgetFactory.DockRight)

    def createDockWidget(self):
        return DEEDocker()


def registerDocker():
    Krita.instance().addDockWidgetFactory(DEEDockerFactory())

registerDocker()
```

```python
class DEEDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Direct Export")
        # Build UI with PyQt5 widgets here
        ...
        self.setWidget(self.mainWidget)

    def canvasChanged(self, canvas):
        # Called by Krita whenever the active document/canvas changes.
        # Use this to reload per-document settings.
        self.loadSettingsFromFile()
```

**Key points:**
- `DockWidgetFactory.DockRight` sets the default docking side.
- `canvasChanged(canvas)` is the main hook for reacting to document switches. `canvas` may be `None` when no document is open.
- The docker's `objectName()` is the first arg to `DockWidgetFactoryBase.__init__()`. The extension uses this to locate the docker at runtime.

---

## 6. Performing the Export

### `document.exportImage(path, infoObject)`

This is the core Krita API call for exporting.

```python
def directExport(self):
    app = Krita.instance()
    activeDoc = app.activeDocument()

    activeDoc.setBatchmode(True)   # suppress any export dialog Krita might show

    info_object = InfoObject()

    # Apply format-specific settings (e.g. quality, compression)
    for key, value in self.deeSettings['exportSettings'].items():
        info_object.setProperty(key, value)

    success = activeDoc.exportImage(export_path, info_object)

    activeDoc.setBatchmode(False)
    return success
```

**Key points:**
- `InfoObject` holds format-specific export parameters as key-value pairs (e.g. `quality=95` for JPEG).
- `setBatchmode(True)` prevents Krita from opening its own export dialog during the call.
- `exportImage()` returns `True` on success, `False` on failure.
- The path must be a fully expanded absolute path — resolve `~` with `os.path.expanduser()` before calling.

### Getting export settings from a user file dialog

After calling `document.exportImage()`, read back the actual settings Krita used:

```python
success = document.exportImage(output_path, info_object)
if success:
    # Krita populates info_object with the settings it actually applied
    applied_settings = info_object.properties()
    self.deeSettings['exportSettings'] = applied_settings
```

This is how the plugin captures format-specific settings (chosen interactively by the user through Krita's own export dialog which appears after the file dialog).

---

## 7. File Selection Dialog

The plugin uses a standard `QFileDialog` to let the user choose the export destination:

```python
fileDialog = QFileDialog()
fileDialog.setWindowTitle("Export Image As")
fileDialog.setFileMode(QFileDialog.AnyFile)
fileDialog.setAcceptMode(QFileDialog.AcceptSave)
fileDialog.setNameFilters([
    "PNG image (*.png)",
    "JPEG image (*.jpg *.jpeg *.jpe)",
    "WebP image (*.webp)",
    # ... 30+ formats
])

if fileDialog.exec_() == QFileDialog.Accepted:
    output_path = fileDialog.selectedFiles()[0]
    selected_filter = fileDialog.selectedNameFilter()

    # Auto-append extension if user didn't type one
    if '.' not in output_path.split('/')[-1]:
        match = re.search(r'\*\.(\w+)[\s\)]', selected_filter)
        if match:
            output_path = f"{output_path}.{match.group(1)}"
```

---

## 8. Persisting Settings in the `.kra` File

The plugin stores per-document export configuration inside the `.kra` file's own metadata, so it survives across Krita sessions without a separate config file.

### Reading: `document.documentInfo()`

Returns the document's internal XML metadata as a string. The plugin extracts the `<abstract>` CDATA section using regex:

```python
doc_info = activeDoc.documentInfo()
match = re.search(
    r'<abstract[^>]*>\s*<!\[CDATA\[(.*?)\]\]>\s*</abstract>',
    doc_info, re.DOTALL
)
if match:
    xml_content = match.group(1)  # The raw text inside CDATA
```

### Stored XML format (inside CDATA)

```xml
<DirectExport>
    <DirectExport_Version>1.03</DirectExport_Version>
    <deeExportPath>~/Pictures/output.png</deeExportPath>
    <exportSettings>
        <quality>95</quality>
        <transparencyFillcolor>&lt;color ...&gt;</transparencyFillcolor>
    </exportSettings>
</DirectExport>
```

Note: XML special characters in values (like `<color>` strings) must be HTML-escaped (`&lt;`, `&gt;`) before writing and unescaped when reading.

### Writing: `document.setDocumentInfo(xml_string)` + `document.save()`

```python
# Replace the abstract CDATA block with new content
new_info = re.sub(
    r'<abstract><!\[CDATA\[([^]]*)\]\]></abstract>',
    f'<abstract><![CDATA[{xml_content}]]></abstract>',
    doc_info
)
activeDoc.setDocumentInfo(new_info)

if activeDoc.fileName():   # only save if file exists on disk
    activeDoc.save()
```

---

## 9. Cross-Platform Path Handling

Absolute paths are stored relative to the home directory (`~`) for portability:

```python
sistem = platform.system()  # "Windows", "Linux", or "Darwin"

# Linux/Mac: /home/user/... → ~/...
if sistem in ("Linux", "Darwin"):
    patron = r"^/home/[^/]+"
    if re.match(patron, absolute_path):
        relative_path = re.sub(patron, "~", absolute_path)

# Windows: C:\Users\user\... → ~\...
elif sistem == "Windows":
    user_profile = os.path.expanduser("~").replace('/', '\\')
    path_normalized = absolute_path.replace('/', '\\')
    if path_normalized.lower().startswith(user_profile.lower()):
        relative_path = path_normalized.replace(user_profile, "~", 1)

# Stored in XML always with forward slashes
xml_safe_path = relative_path.replace('\\', '/')

# Expanded back before export:
if image_path.startswith('~'):
    image_path = os.path.expanduser(image_path)
if sistem == "Windows":
    image_path = image_path.replace('/', '\\')
```

---

## 10. UI State Machine

`setPathDisplay()` drives three distinct UI states based on the path value:

| State | Trigger | Color | Buttons visible |
|-------|---------|-------|-----------------|
| Invalid format | non-.kra file open | Red (`#954a4a`) | Neither |
| Not exported yet | `.kra` open, no saved path | Gray | Folder only |
| Path set | valid path loaded | White | Both folder + export |

```python
def setPathDisplay(self, path=None):
    if path == "Wrong":
        # non-.kra file
        self.pathDisplay.setStyleSheet("color: #954a4a;")
        self.pathDisplay.setText("  -- Not a Krita file --")
        self.selectExportPath.setVisible(False)
        self.selectExport.setVisible(False)
    elif path is None:
        # .kra file but no export configured yet
        self.pathDisplay.setStyleSheet("color: gray;")
        self.pathDisplay.setText("  -- Image not exported yet --")
        self.selectExportPath.setVisible(True)
        self.selectExport.setVisible(False)
    else:
        self.pathDisplay.setStyleSheet("color: white;")
        self.pathDisplay.setText(path)
        self.selectExportPath.setVisible(True)
        self.selectExport.setVisible(True)
```

---

## 11. Temporary Notification (Auto-closing QMessageBox)

```python
def showExportMessage(self):
    self.msg = QMessageBox()
    self.msg.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    self.msg.setStandardButtons(QMessageBox.NoButton)
    self.msg.setText("  IMAGE EXPORTED   \n\n" + self.deeSettings['deeExportPath'])
    self.msg.setStyleSheet("QLabel { color: orange; font-size: 14px; font-weight: bold; }")

    # Center on Krita's main window
    window = Krita.instance().activeWindow().qwindow()
    self.msg.move(window.frameGeometry().center() - self.msg.rect().center())

    self.timer = QTimer()
    self.timer.setSingleShot(True)
    self.timer.timeout.connect(self.closeMessage)
    self.msg.show()
    self.timer.start(1000)  # auto-close after 1 second

    # Also update Krita's status bar
    Krita.instance().activeWindow().qwindow().statusBar().showMessage("  IMAGE EXPORTED   ")
```

---

## 12. Complete Export Flow

```
User clicks "Export" button
        │
        ▼
export() [DEEDocker]
        │
        ├─ No path yet? ──────────────► updateExportingPath()
        │                                       │
        │                               export_advanced(doc)
        │                                       │
        │                               QFileDialog (pick path + format)
        │                                       │
        │                               document.exportImage(path, InfoObject)
        │                                       │
        │                               Krita opens its format dialog
        │                                       │
        │                               info_object.properties() ← get settings
        │                                       │
        │                               Save XML into .kra documentInfo
        │                                       │
        │                               document.save()
        │
        └─ Path set? ─────────────────► directExport()
                                                │
                                        InfoObject with saved settings
                                                │
                                        os.path.expanduser(path)
                                                │
                                        activeDoc.setBatchmode(True)
                                                │
                                        activeDoc.exportImage(path, info)
                                                │
                                        activeDoc.setBatchmode(False)
                                                │
                                        showExportMessage() [1-second popup]
```

---

## 13. Krita API Reference Summary

| API | Description |
|-----|-------------|
| `Krita.instance()` | Singleton app object |
| `app.activeDocument()` | Currently focused `.kra` document |
| `app.activeWindow()` | Currently focused Krita window |
| `window.dockers()` | List of all visible docker widgets |
| `window.createAction(name, label)` | Register a named action for shortcut binding |
| `window.qwindow()` | Underlying `QMainWindow` |
| `document.exportImage(path, InfoObject)` | Export to file; returns bool |
| `document.documentInfo()` | Get document XML metadata string |
| `document.setDocumentInfo(xml)` | Write back XML metadata |
| `document.save()` | Save the `.kra` file |
| `document.setBatchmode(bool)` | Suppress/restore Krita UI during export |
| `document.fileName()` | Absolute path of `.kra` file on disk |
| `document.name()` | Document title (no path) |
| `InfoObject()` | Key-value container for export format settings |
| `infoObject.setProperty(key, value)` | Set a format option |
| `infoObject.properties()` | Get all options as a dict |
| `DockWidget` | Base class for a persistent docker panel |
| `DockWidget.canvasChanged(canvas)` | Called on document/canvas switch |
| `DockWidgetFactoryBase` | Factory that Krita calls to create docker instances |
| `Extension` | Base class for registering actions |
| `Extension.setup()` | Called once at startup (can be empty) |
| `Extension.createActions(window)` | Called per window to register actions |
| `Krita.instance().addExtension(ext)` | Register an Extension |
| `Krita.instance().addDockWidgetFactory(fac)` | Register a docker factory |

---

## 14. Minimal Plugin Template

The smallest working custom export plugin needs these pieces:

```
myplugin/
├── actions/
│   └── myplugin.action
└── pykrita/
    ├── myplugin.desktop
    └── myplugin/
        ├── __init__.py
        └── myplugin.py
```

**`myplugin.desktop`**
```ini
[Desktop Entry]
Type=Service
ServiceTypes=Krita/PythonPlugin
X-KDE-Library=myplugin
X-Python-2-Compatible=false
Name=My Plugin
Comment=Description here
```

**`myplugin/__init__.py`**
```python
from .myplugin import *
```

**`myplugin/myplugin.py`**
```python
from krita import Krita, Extension, DockWidget, DockWidgetFactoryBase, DockWidgetFactory, InfoObject
from PyQt5.Qt import QWidget, QVBoxLayout, QPushButton, QFileDialog

class MyDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Export")
        btn = QPushButton("Export")
        btn.clicked.connect(self.do_export)
        w = QWidget()
        QVBoxLayout(w).addWidget(btn)
        self.setWidget(w)

    def canvasChanged(self, canvas):
        pass

    def do_export(self):
        doc = Krita.instance().activeDocument()
        if doc is None:
            return
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setNameFilters(["PNG image (*.png)", "JPEG image (*.jpg)"])
        if dlg.exec_() == QFileDialog.Accepted:
            path = dlg.selectedFiles()[0]
            info = InfoObject()
            doc.setBatchmode(True)
            doc.exportImage(path, info)
            doc.setBatchmode(False)


class MyDockerFactory(DockWidgetFactoryBase):
    def __init__(self):
        super().__init__("myplugin", DockWidgetFactory.DockRight)
    def createDockWidget(self):
        return MyDocker()


class MyExtension(Extension):
    def setup(self): pass
    def createActions(self, window):
        action = window.createAction("myplugin", "My Export")
        action.triggered.connect(self.trigger)
    def trigger(self):
        for d in Krita.instance().activeWindow().dockers():
            if d.objectName() == "myplugin":
                d.do_export()
                break

Krita.instance().addExtension(MyExtension(Krita.instance()))
Krita.instance().addDockWidgetFactory(MyDockerFactory())
```

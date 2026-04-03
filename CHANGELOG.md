# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 2026-03-30
### Changed
- PyQt5 / PyQt6 dual compatibility (`compat.py`)
  - Added `compat.py` shim — all Qt imports now routed through this module; detects PyQt5 or PyQt6 at runtime
  - PyQt6 path patches all flat enum aliases (`Qt.AlignLeft`, `QEvent.KeyPress`, `QPalette.Window`, etc.) so existing code requires no changes
  - `QShortcut` and `QAction` imports moved from `QtWidgets` to `QtGui` for PyQt6
  - All `exec_()` calls replaced with `exec()` (works on both PyQt5 ≥ 5.12 and PyQt6)
  - `QTextEdit.NoWrap` patched to `QTextEdit.LineWrapMode.NoWrap` for PyQt6
  - `QRadioButton` and `QButtonGroup` added to compat shim
  - `DockWidgetFactoryBase.DockRight` wrapped with try/except fallback to `DockPosition.DockRight` for Krita 6
  - Standalone scripts in `scripts/` updated with inline try/except Qt5/6 imports
- Config and icon files moved out of `pykrita/lazy_tools/config/` to `krita/lazy_tools/config/`
  - Config files (`common.json`, `name_color_list.txt`) now survive plugin updates/reinstalls
  - System icon directory remains in `pykrita/lazy_tools/config/icon/` (bundled with the plugin)
  - Centralized path utilities in `config/config_loader.py` (`get_config_path()`, `get_icon_dir()`, `get_name_color_list_path()`)

## 2026-01-31
### Added
- Add New SetForegroundColor Actions

## 2026-01-23
### Changed
- Screen Color Picker is now only loaded on Windows OS

## 2025-12-30
### Added
- Configuration system for Lazy Tools plugin
  - Settings dialog with Common and Name List tabs
  - Common settings for enabling/disabling screen color picker and top menu shortcuts
  - Name List editor for managing layer names with optional color labels
  - Config files stored in `lazy_tools/config/` directory
- Rename Alternative script
  - Dialog displays layer names from `name_color_list.txt` with color icons
  - Click to rename active layer and set color label
  - Supports case-insensitive color names (Blue, Green, Yellow, Orange, Brown, Red, Purple, Grey)
  - Dialog positioned at mouse cursor for quick access
  - Sets color to None/Transparent when no color specified

### Changed
- Add New Layer dialog now uses editable combo box for layer names
  - Populated with layer names from `name_color_list.txt`
  - Allows typing custom names or selecting from predefined list
  - Displays placeholder text "auto-generate if empty" when empty

## 2025-12-24
### Added
- Add Selection Mask Alternative Action
- Add Create Selection Mask Popup Window Action

## 2025-12-02
### Added
- Two new layer group actions
  - Fold All Layer Groups - Collapse all layer groups in the document
  - Expand All Layer Groups - Expand all layer groups in the document
- Deselect Alternative - Deselect and Switch to Freehand Brush Tool in one action


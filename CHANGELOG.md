# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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


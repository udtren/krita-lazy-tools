# Lazy Tools for Krita

A Krita plugin suite that adds layer management and automation tools directly to the Layer Docker.
![Setting](./lazy_tools/images/1.png)
## Features

### Color Labeling (LazyColorLabel)
- Adds a color label dropdown to Krita's Layer Docker
- Quick assignment of color labels to layers and groups
- Works with selected layers or current active layer

### Color Filtering (LazyColorFilter)
- Toggle visibility of layers/groups by color label
- Click a color to show/hide all layers with that specific color label

### Script Execution (LazyScripts)
- Execute custom Python scripts directly from the Layer Docker
- Auto-discovery of `.py` files in the `scripts` folder
- "Reload Scripts" option for dynamic script development

## Usage
### Script Execution
1. Add custom `.py` scripts to the `lazy_tools/scripts/` folder
2. Click "Reload Scripts" (green icon) to refresh the script list
3. Select a script name from the third dropdown to execute it
4. Check the console for execution results

## Sample Scripts Included
- **duplicate_layer.py** - Duplicates the currently active layer
- **create_paint_layer.py** - Creates a new paint layer above the current layer
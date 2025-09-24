# Krita Lazy Tools

A Krita plugin that adds layer management and automation tools.

For "Florence-2 + SAM2.1 AI Segmentation" function, use "sam2" branch.
![Setting](./lazy_tools/images/1.png)

## Features
### Color Labeling
- Adds a color label dropdown to Krita's Layer Docker
- Quick assignment of color labels to layers and groups
- Updating a group will not change its children's color labels

### Color Filtering
- Toggle visibility of layers/groups by color label
- Click a color to show/hide all layers with that specific color label

### Script Execution
- Execute custom Python scripts
- Auto-discovery of `.py` files in the `lazy_tools/scripts/` folder
- "Reload Scripts" option for dynamic script development

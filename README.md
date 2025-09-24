# Krita Lazy Tools

A Krita plugin that adds layer management and automation tools.
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

## Florence + Sam2.1
install the necessary package

python -m venv .venv

you python version should be "3.12.10" because I didnt test other version

install packages in venv
pip install -r .\requirements.txt

download "sam2.1_hiera_large.pt" and "sam2.1_hiera_base_plus.pt" and put them in models folder
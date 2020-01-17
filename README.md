# BabelBrushVolumeManager
A simple tool for creating and managing the user saves folder (volume hub) for BabelBrush and indexing nii files ready to use.

To setup the python environment:-
```
pip install -r requirements.txt
```

### Modules

The class  `BabelBrushVolumeHub` in BabelBrushVolumeHub.py has the following methods:-

* open_hub(folder)
* index_nii_file(file_name)
* delete_volume(index)
    
The method `create_directory_structure` creates an empty hub (folder structure).

The module VolumeHubGUI is just a wxPython GUI wrapped around BabelBrushVolumeHub. It can be run with:-
```
python VolumeHubGUI.py
```

### Example Usage
```
from BabelBrushVolumeHunb import BabelBrushVolumeHub,create_directory_structure
folder  ="/path/to/base_folder"
create_directory_structure(folder)
hub = BabelBrushVolumeHub(folder)
hub.index_nii_file("/path/to/file.nii")
```

### Building
To get a single clickable executable:-
```
pyinstaller -w -F VolumeHubGUI.py
```

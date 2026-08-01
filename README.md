# Osmapy — Python Editor for OpenStreetMap Data

Osmapy is a Python‑based editor for OpenStreetMap (OSM) data.  
It provides functionality for viewing map tiles, loading GPX tracks, inspecting OSM elements, and modifying nodes.  
The graphical interface is implemented using Qt via PySide6.

OpenStreetMap® and the OpenStreetMap logo are trademarks of the OpenStreetMap Foundation.  
The Python logo is a trademark of the Python Software Foundation.  
Osmapy is not endorsed by or affiliated with either organization.

## Features

### Tile handling
- Slippy‑tile interface  
- LIFO tile‑loading queue  
- Concurrent tile downloads  
- Local tile caching  
- Configurable tile servers

### Layers
- Multiple layers  
- Adjustable layer order (drag and drop)  
- Adjustable layer opacity

### GPX
- GPX loading via drag and drop

### OSM element editing
- Create, modify, and delete OSM nodes  
- Add, change, and remove tags  
- Move nodes using arrow keys  
- Upload changes to an OSM API endpoint

### Interface
- Movable tool windows  
- Single YAML configuration file

## Installation

Install the project in editable mode:

```bash
pip install -e .
```

Install with test dependencies:

```bash
pip install -e .[test]
```

Run the application:

```bash
osmapy
```

Or:

```bash
python -m osmapy
```

### Windows notes

Python must be available in the PATH.  
If not, modify the PATH manually or re‑run the Python installer and enable *Add Python to environment variables*.  
Some Python packages may require Microsoft Build Tools.

## Development and Testing

Use the OSM sandbox API for development:

```
https://master.apis.dev.openstreetmap.org
```

Set the API URL in `config.yaml`:

```yaml
osm_api_url: https://master.apis.dev.openstreetmap.org
```

Run tests:

```bash
pytest
```

## Usage Notes

- Move the map: right mouse button + drag  
- Zoom: mouse wheel  
- Load OSM elements for the visible area: *Load Elements*  
- Select a node: right click  
- Move a selected node: arrow keys  
- Remove a tag: click the tag key  
- Load GPX: drag and drop a GPX file into the window

## License

Osmapy is licensed under the GNU General Public License v3.0.

## Origin

Osmapy was originally created by Philipp Rigoll.  
The original repository is available at: https://github.com/PhilippRigoll/osmapy

# spritep

A command-line tool to generate placeholder sprites from a YAML configuration file.

## Installation

```bash
uv pip install git+https://github.com/johnbradley/spritep.git
```

## Usage

```bash
spritep [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-c, --config PATH` | Path to YAML configuration file (default: `placeholders.yaml`) |
| `-o, --output PATH` | Output directory for generated sprites (default: `.`) |
| `-v, --verbose` | Enable verbose output |

## Configuration Syntax

The configuration file uses YAML format with two main sections: `defaults` and `sprites`.

### Basic Structure

```yaml
defaults:
  # Default values applied to all sprites
  width: 64
  height: 64

sprites:
  - name: my_sprite
    width: 32
    height: 32
```

### Defaults Section

Optional section that sets default values for all sprites. Any property set here applies to sprites that don't override it.

```yaml
defaults:
  width: 64
  height: 64
  background: "#CCCCCC"
  text_color: "#333333"
  border:
    color: "#999999"
    width: 1
```

### Sprites Section

A list of sprites to generate. Each sprite supports the following properties:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | string | required | Output filename (without extension) |
| `folder` | string | none | Subfolder to organize sprite into |
| `width` | integer | `100` | Width in pixels |
| `height` | integer | `100` | Height in pixels |
| `background` | color | transparent | Background color |
| `text` | string | none | Label text (no text if unset) |
| `text_color` | color | `#666666` | Text color |
| `corner_radius` | integer | none | Rounded corner radius in pixels |
| `border` | object | none | Border configuration |

### Border Configuration

```yaml
border:
  color: "#999999"  # Border color
  width: 1          # Border thickness in pixels
```

### Color Formats

Colors can be specified in several formats:

| Format | Example | Description |
|--------|---------|-------------|
| Named | `"red"`, `"forestgreen"` | CSS color names |
| Hex RGB | `"#FF0000"` | Red, green, blue |
| Hex RGBA | `"#FF000080"` | RGB with alpha (80 = 50% opacity) |
| RGB list | `[255, 0, 0]` | Red, green, blue as integers |
| RGBA list | `[255, 0, 0, 128]` | RGB with alpha channel |

Named colors include all [CSS color names](https://www.w3.org/TR/css-color-3/#svg-color) such as `red`, `blue`, `green`, `coral`, `dodgerblue`, `forestgreen`, etc.

### Example Configuration

```yaml
defaults:
  width: 64
  height: 64
  text_color: white

sprites:
  - name: player
    folder: characters
    width: 32
    height: 32
    background: dodgerblue
    text: "P"

  - name: enemy
    folder: characters
    width: 32
    height: 32
    background: crimson
    text: "E"

  - name: coin
    folder: items
    width: 16
    height: 16
    background: gold
    text: "$"
    text_color: black

  - name: grass
    folder: tiles
    width: 64
    height: 64
    background: limegreen
```

This generates:
```
output/
├── characters/
│   ├── player.png
│   └── enemy.png
├── items/
│   └── coin.png
└── tiles/
    └── grass.png
```

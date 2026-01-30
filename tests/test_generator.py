"""Tests for sprite generator."""

import pytest
from pathlib import Path
from PIL import Image

from spritep.generator import (
    parse_color,
    generate_sprite,
    generate_sprites,
    load_config,
)


class TestParseColor:
    def test_hex_rgb(self):
        assert parse_color("#FF0000") == (255, 0, 0)
        assert parse_color("#00FF00") == (0, 255, 0)
        assert parse_color("#0000FF") == (0, 0, 255)

    def test_hex_rgba(self):
        assert parse_color("#FF000080") == (255, 0, 0, 128)
        assert parse_color("#00FF00FF") == (0, 255, 0, 255)

    def test_hex_lowercase(self):
        assert parse_color("#ff0000") == (255, 0, 0)
        assert parse_color("#aabbcc") == (170, 187, 204)

    def test_rgb_list(self):
        assert parse_color([255, 0, 0]) == (255, 0, 0)
        assert parse_color([100, 150, 200]) == (100, 150, 200)

    def test_rgba_list(self):
        assert parse_color([255, 0, 0, 128]) == (255, 0, 0, 128)

    def test_none_returns_default(self):
        assert parse_color(None) == (0, 0, 0, 0)
        assert parse_color(None, (255, 255, 255)) == (255, 255, 255)
        assert parse_color(None, "#FF0000") == (255, 0, 0)

    def test_without_hash(self):
        assert parse_color("FF0000") == (255, 0, 0)

    def test_named_colors(self):
        assert parse_color("red") == (255, 0, 0)
        assert parse_color("green") == (0, 128, 0)
        assert parse_color("blue") == (0, 0, 255)
        assert parse_color("white") == (255, 255, 255)
        assert parse_color("black") == (0, 0, 0)

    def test_named_colors_extended(self):
        assert parse_color("forestgreen") == (34, 139, 34)
        assert parse_color("coral") == (255, 127, 80)
        assert parse_color("dodgerblue") == (30, 144, 255)

    def test_invalid_color_returns_transparent(self):
        assert parse_color("notacolor") == (0, 0, 0, 0)


class TestGenerateSprite:
    def test_creates_file(self, tmp_path):
        output = generate_sprite(
            name="test",
            width=32,
            height=32,
            output_dir=tmp_path,
        )
        assert output.exists()
        assert output.name == "test.png"

    def test_correct_dimensions(self, tmp_path):
        generate_sprite(
            name="test",
            width=64,
            height=48,
            output_dir=tmp_path,
        )
        img = Image.open(tmp_path / "test.png")
        assert img.size == (64, 48)

    def test_transparent_background(self, tmp_path):
        generate_sprite(
            name="test",
            width=32,
            height=32,
            output_dir=tmp_path,
        )
        img = Image.open(tmp_path / "test.png")
        assert img.mode == "RGBA"
        # Check center pixel is transparent
        pixel = img.getpixel((16, 16))
        assert pixel[3] == 0

    def test_colored_background(self, tmp_path):
        generate_sprite(
            name="test",
            width=32,
            height=32,
            background="#FF0000",
            output_dir=tmp_path,
        )
        img = Image.open(tmp_path / "test.png")
        # Check center pixel is red
        pixel = img.getpixel((16, 16))
        assert pixel[0] == 255
        assert pixel[1] == 0
        assert pixel[2] == 0

    def test_with_text(self, tmp_path):
        generate_sprite(
            name="test",
            width=64,
            height=64,
            background="#FFFFFF",
            text="X",
            text_color="#000000",
            output_dir=tmp_path,
        )
        img = Image.open(tmp_path / "test.png")
        # Image should exist and have correct size
        assert img.size == (64, 64)

    def test_with_border(self, tmp_path):
        generate_sprite(
            name="test",
            width=32,
            height=32,
            border={"color": "#FF0000", "width": 2},
            output_dir=tmp_path,
        )
        img = Image.open(tmp_path / "test.png")
        # Check corner pixel has border color
        pixel = img.getpixel((0, 0))
        assert pixel[0] == 255
        assert pixel[1] == 0
        assert pixel[2] == 0

    def test_with_folder(self, tmp_path):
        output = generate_sprite(
            name="test",
            width=32,
            height=32,
            folder="characters",
            output_dir=tmp_path,
        )
        assert output.exists()
        assert output == tmp_path / "characters" / "test.png"

    def test_with_nested_folder(self, tmp_path):
        output = generate_sprite(
            name="test",
            width=32,
            height=32,
            folder="sprites/characters/players",
            output_dir=tmp_path,
        )
        assert output.exists()
        assert output == tmp_path / "sprites" / "characters" / "players" / "test.png"

    def test_with_corner_radius(self, tmp_path):
        generate_sprite(
            name="test",
            width=32,
            height=32,
            background="#FF0000",
            corner_radius=8,
            output_dir=tmp_path,
        )
        img = Image.open(tmp_path / "test.png")
        # Corner pixel should be transparent due to rounding
        corner_pixel = img.getpixel((0, 0))
        assert corner_pixel[3] == 0  # Alpha should be 0
        # Center pixel should be red
        center_pixel = img.getpixel((16, 16))
        assert center_pixel[0] == 255

    def test_corner_radius_with_border(self, tmp_path):
        generate_sprite(
            name="test",
            width=32,
            height=32,
            background="#0000FF",
            corner_radius=8,
            border={"color": "#FF0000", "width": 2},
            output_dir=tmp_path,
        )
        img = Image.open(tmp_path / "test.png")
        assert img.size == (32, 32)
        # Corner should be transparent
        assert img.getpixel((0, 0))[3] == 0


class TestLoadConfig:
    def test_loads_yaml(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
sprites:
  - name: test
    width: 32
    height: 32
""")
        config = load_config(config_file)
        assert "sprites" in config
        assert len(config["sprites"]) == 1
        assert config["sprites"][0]["name"] == "test"

    def test_loads_defaults(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
defaults:
  width: 64
  height: 64

sprites:
  - name: test
""")
        config = load_config(config_file)
        assert config["defaults"]["width"] == 64


class TestGenerateSprites:
    def test_generates_multiple(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
sprites:
  - name: sprite1
    width: 32
    height: 32
  - name: sprite2
    width: 64
    height: 64
""")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        results = generate_sprites(config_file, output_dir)

        assert len(results) == 2
        assert (output_dir / "sprite1.png").exists()
        assert (output_dir / "sprite2.png").exists()

    def test_applies_defaults(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
defaults:
  width: 48
  height: 48
  background: "#0000FF"

sprites:
  - name: test
""")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        generate_sprites(config_file, output_dir)

        img = Image.open(output_dir / "test.png")
        assert img.size == (48, 48)
        pixel = img.getpixel((24, 24))
        assert pixel[2] == 255  # Blue

    def test_sprite_overrides_defaults(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
defaults:
  width: 64
  height: 64

sprites:
  - name: test
    width: 32
    height: 32
""")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        generate_sprites(config_file, output_dir)

        img = Image.open(output_dir / "test.png")
        assert img.size == (32, 32)

    def test_empty_sprites_returns_empty(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
sprites: []
""")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        results = generate_sprites(config_file, output_dir)
        assert results == []

    def test_no_sprites_key_returns_empty(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
defaults:
  width: 64
""")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        results = generate_sprites(config_file, output_dir)
        assert results == []

    def test_sprites_with_folders(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
sprites:
  - name: player
    folder: characters
    width: 32
    height: 32
  - name: coin
    folder: items
    width: 16
    height: 16
  - name: logo
    width: 64
    height: 64
""")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        results = generate_sprites(config_file, output_dir)

        assert len(results) == 3
        assert (output_dir / "characters" / "player.png").exists()
        assert (output_dir / "items" / "coin.png").exists()
        assert (output_dir / "logo.png").exists()

    def test_default_folder(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
defaults:
  folder: sprites

sprites:
  - name: player
    width: 32
    height: 32
  - name: enemy
    width: 32
    height: 32
""")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        generate_sprites(config_file, output_dir)

        assert (output_dir / "sprites" / "player.png").exists()
        assert (output_dir / "sprites" / "enemy.png").exists()

    def test_folder_override(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
defaults:
  folder: default

sprites:
  - name: special
    folder: custom
    width: 32
    height: 32
""")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        generate_sprites(config_file, output_dir)

        assert (output_dir / "custom" / "special.png").exists()
        assert not (output_dir / "default" / "special.png").exists()

"""Command-line interface for sprite placeholder generator."""

import click
from pathlib import Path

from .generator import generate_sprites


@click.command()
@click.option(
    "-c", "--config",
    type=click.Path(exists=True, path_type=Path),
    default="placeholders.yaml",
    help="Path to YAML configuration file.",
)
@click.option(
    "-o", "--output",
    type=click.Path(path_type=Path),
    default=".",
    help="Output directory for generated sprites.",
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output.",
)
def main(config: Path, output: Path, verbose: bool) -> None:
    """Generate placeholder sprites from a YAML configuration file."""
    if verbose:
        click.echo(f"Reading configuration from: {config}")

    output.mkdir(parents=True, exist_ok=True)

    sprites = generate_sprites(config, output, verbose=verbose)

    output_display = "current directory" if str(output) == "." else f"{output}/"
    click.echo(f"Generated {len(sprites)} sprite(s) in {output_display}")


if __name__ == "__main__":
    main()

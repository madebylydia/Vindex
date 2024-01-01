from logging import root
import pathlib
from re import sub
import subprocess

import click
import rich

from vindex import __file__ as _vindex_path

VINDEX_PATH = pathlib.Path(_vindex_path, "..").resolve()
PATHS_TO_TRANSLATE = [
    VINDEX_PATH / "cogs",
    VINDEX_PATH / "core",
]


@click.command()
def localegenerate():
    """Generate locales files."""
    console = rich.get_console()

    console.print("[yellow]This command is a work in progress.[/]")

    for main_path in PATHS_TO_TRANSLATE:
        for root_path, _, files in main_path.walk():
            if "__pycache__" in root_path.parts:
                continue

            if any(file.endswith(".py") for file in files):
                console.print(f"[green]Generating at [cyan]{root_path}[/cyan]...")

                subprocess.Popen(
                    [
                        "pygettext3",
                        "--docstrings",
                        "--output-dir",
                        root_path / "locales",
                        "--style",
                        "GNU",
                        "--verbose"
                    ]
                )

import pathlib
import subprocess

import rich

from vindex import __file__ as _vindex_path

VINDEX_PATH = pathlib.Path(_vindex_path, "..").resolve()
PATHS_TO_TRANSLATE = [
    VINDEX_PATH / "cogs",
    VINDEX_PATH / "core",
]


def translate_project():
    """Generate locales files."""
    console = rich.get_console()

    for main_path in PATHS_TO_TRANSLATE:
        for root_path, _, files in main_path.walk():
            if "__pycache__" in root_path.parts:
                continue

            if any(file.endswith(".py") for file in files):
                locale_path = root_path / "locales"

                if not locale_path.exists():
                    locale_path.mkdir()

                console.print(f"[green]Generating at [cyan]{root_path}[/cyan]...")
                with subprocess.Popen(
                    [
                        "pygettext3",
                        "--docstrings",
                        "--output-dir",
                        str(locale_path),
                        "--style",
                        "GNU",
                        f"{root_path}/*.py",
                    ],
                ) as process:
                    process.wait()

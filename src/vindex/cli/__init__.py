import pathlib

import ccl
import click

ROOT_FOLDER = pathlib.Path(__file__).parent.resolve()
COMMANDS_FOLDER = ROOT_FOLDER / "commands"

cli = click.Group("Vindex")

ccl.register_commands(cli, COMMANDS_FOLDER.resolve())

# "cli" will be called by Poetry.

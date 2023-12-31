import os
import pathlib

import click
import rich

from vindex.core.creator import fetch_creator
from vindex.core.exceptions.invalid_creator import CreatorException


@click.command()
def updateenv():
    """Update your .env file with the database URL."""
    console = rich.get_console()

    try:
        creator = fetch_creator()
    except CreatorException:
        console.print(
            "[red]It appears that you have not setup Vindex. Please run "
            "[blue]vindex setup[/blue] to setup Vindex first."
        )
        return

    env_file = pathlib.Path(os.getcwd()) / ".env"
    with env_file as file:
        env_content = file.read_text()

    env_lines_separated = [line.split("=") for line in env_content.split("\n")]

    edited = False
    for line in env_lines_separated:
        if line[0] == "DATABASE_URL":
            line[1] = creator.build_db_url()
            edited = True
            break
        if line[0] == "":
            env_lines_separated.remove(line)
            break

    if not edited:
        env_lines_separated.append(["DATABASE_URL", creator.build_db_url()])

    env_content = "\n".join(["=".join(line) for line in env_lines_separated])

    with env_file as file:
        file.write_text(env_content)

    console.print(
        "[green]Successfully exported the database URL to your [yellow].env[/yellow] file."
    )

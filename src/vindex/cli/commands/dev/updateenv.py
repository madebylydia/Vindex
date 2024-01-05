import os
import pathlib

import click
import rich

from vindex.core.creator import fetch_creator
from vindex.core.exceptions.invalid_creator import CreatorException


@click.command()
@click.argument("instance_name", type=str)
def updateenv(instance_name: str):
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

    instance = creator.instances.get(instance_name)
    if not instance:
        console.print(
            f"[red]No instance with the name [blue]{instance_name}[/blue] exists."
        )
        return

    env_file = pathlib.Path(os.getcwd()) / ".env"
    with env_file as file:
        if not file.exists():
            file.touch()
        env_content = file.read_text()

    env_lines_separated = [line.split("=") for line in env_content.split("\n")]

    edited = False
    for line in env_lines_separated:
        if line[0] == "DATABASE_URL":
            line[1] = instance.build_db_url()
            edited = True
            break
        if line[0] == "":
            env_lines_separated.remove(line)
            break

    if not edited:
        # ... then create the line
        env_lines_separated.append(["DATABASE_URL", instance.build_db_url()])

    env_content = "\n".join(["=".join(line) for line in env_lines_separated])

    with env_file as file:
        file.write_text(env_content)

    console.print(
        "[green]Successfully exported the database URL to your [yellow].env[/yellow] file."
    )

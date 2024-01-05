import click
import rich

from vindex.core.creator.reader import fetch_creator

@click.command()
def list():
    """List all of your Vindex instances."""
    console = rich.get_console()

    creator = fetch_creator()

    total = 0
    for index, instance in enumerate(creator.instances, 1):
        console.print(f"[red]{index}. [blue]{instance}[/]")
        total += 1

    if total == 0:
        console.print(f"[yellow]There is no instances in here. How about starting with [green]vindex setup[/]?")

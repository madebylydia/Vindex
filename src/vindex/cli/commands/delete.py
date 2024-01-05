import click
import rich
from rich.prompt import Confirm

from vindex.core.creator import Creator, fetch_creator
from vindex.core.exceptions.invalid_creator import CreatorException


def build_list(creator: Creator) -> dict[int, str]:
    """Create a dictionnary for a list of editable values inside the Creator."""
    return dict(enumerate(creator.model_dump().keys()))


@click.command()
@click.argument("instance_name", required=True)
def delete(instance_name: str):
    """Edit your Vindex Creator."""
    console = rich.get_console()

    try:
        creator = fetch_creator()
    except CreatorException as e:
        click.echo(e)
        return

    instance = creator.instances.get(instance_name)
    if not instance:
        console.print(
            f"[red]No instance with the name [blue]{instance_name}[/blue] exists."
        )
        return

    if not Confirm.ask(f"[yellow]:warning-emoji: Are you sure to delete [blue]{instance_name}[/blue]?[/] (DB data will remain as-is)"):
        return
    creator.instances.pop(instance_name)
    creator.commit()
    console.print(f"[green]:white_check_mark-emoji: Deleted [blue]{instance_name}[/blue].")

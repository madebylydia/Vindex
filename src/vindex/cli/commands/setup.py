import click
import rich
from rich.prompt import Confirm

from vindex.cli.commands.dev.updateenv import updateenv
from vindex.cli.utils import Prompt
from vindex.core.creator.model import Creator, CreatorData
from vindex.core.creator.reader import fetch_creator

SETUP_INTRO = f"""
[bold blue]:star-emoji: Welcome to Vindex setup![/]
This setup will help you setup your instance of Vindex.
This will store a new file in your config directory, located at [cyan]{Creator.PATH}[/cyan].\n
This will contain your bot's token, prefix, and anyother information needed for the bot correct's setup.
To abort this setup, press [magenta]Ctrl + C[/magenta] at any moment.
"""


@click.command()
@click.argument("name", required=True)
def setup(name: str):
    """Setup your Vindex instance."""
    name = "".join(char.lower() for char in name if char.isalnum())

    console = rich.get_console()

    console.clear()
    console.print(SETUP_INTRO)
    console.print(
        f'[italic blue]:information-emoji: We will now create an instance called "{name}"'
    )

    console.print("[yellow]:key-emoji: What is your bot's token?")
    token = Prompt.ask()

    console.print("[yellow]:speech_balloon-emoji: What is your bot's prefix?")
    prefix = Prompt.ask()

    console.print("[yellow]:floppy_disk-emoji: What is your database name?")
    database_name = Prompt.ask()

    console.print("[yellow]:floppy_disk-emoji: Who is your database user?")
    database_user = Prompt.ask()

    console.print("[yellow]:floppy_disk-emoji: What is your database user's password?")
    database_password = Prompt.ask()

    console.print("[yellow]:floppy_disk-emoji: What is your database host?")
    database_host = Prompt.ask()

    creator = fetch_creator()
    data = CreatorData(
        name=name,
        token=token,
        prefix=prefix,
        database_name=database_name,
        database_user=database_user,
        database_password=database_password,
        database_host=database_host,
    )
    creator.instances[name] = data

    console.print(data)

    if Confirm.ask("Do you confirm committing this Creator?"):
        creator.commit()
        console.print(
            "[bold green]:white_check_mark-emoji: The Creator has been succesfully committed!"
        )
        updateenv()

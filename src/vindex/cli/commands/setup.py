import click
import rich

from rich.prompt import Prompt as Confirm

from vindex.cli.utils import Prompt
from vindex.core.creator.model import Creator
from vindex.core.creator.reader import get_creator


SETUP_INTRO = f"""
[bold blue]:star-emoji: Welcome to Vindex setup![/]
This setup will help you setup your instance of Vindex.
This will store a new file in your config directory, located at [cyan]{Creator.PATH}[/cyan].\n
This will contain your bot's token, prefix, and anyother information needed for the bot correct's setup.
To abort this setup, press [magenta]Ctrl + C[/magenta] at any moment.
"""


@click.command()
def setup():
    """
    Setup your Vindex instance.
    """
    console = rich.get_console()

    console.clear()
    console.print(SETUP_INTRO)

    if get_creator():
        console.print(
            "[bold red]:warning-emoji: A CREATOR ALREDY EXISTS, IT WILL BE OVERWRITTEN[/]\n"
            "[red]If you prefer to edit each settings, use the [cyan]vindex edit[/cyan] command.[/red]"
        )
        if not Confirm.ask("[red]Do you still want to proceed?"):
            return

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

    config = Creator(
        token=token,
        prefix=prefix,
        database_name=database_name,
        database_user=database_user,
        database_password=database_password,
        database_host=database_host,
    )

    console.print(config)

    if Confirm.ask("Do you confirm committing this Creator?"):
        config.commit()
        console.print("[bold green]:white_check_mark-emoji: The Creator has been succesfully committed!")

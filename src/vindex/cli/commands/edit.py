import click
import rich

from rich.prompt import IntPrompt, Confirm
from vindex.cli.utils import Prompt

from vindex.core.creator import fetch_creator, Creator
from vindex.core.exceptions.invalid_creator import CreatorException

def build_list(creator: Creator) -> dict[int, str]:
    return {
        index: value
        for index, value in enumerate(creator.model_dump().keys())
    }
    

@click.command()
def edit():
    """
    Edit your Vindex Creator.
    """
    console = rich.get_console()

    try:
        creator = fetch_creator()
    except CreatorException as e:
        click.echo(e)
        return

    console.clear()
    console.print("[green]What would you like to edit?")

    while True:
        choices = build_list(creator)

        console.print("\n".join(f"[cyan]{index}[/cyan] [yellow]{value}" for index, value in choices.items()))

        choice = None
        while choice is None:
            choice = IntPrompt.ask("Enter your choice")
            
            if choice not in choices.keys():
                choice = None
                console.print("[red]Invalid choice.")

        console.print(f"Current value: [blue]{getattr(creator, choices[choice])}[/blue]")
        new_value = None
        while not new_value:
            console.print(f"[yellow]:writing_hand-emoji: What is the new value of [blue]{choices[choice]}[/blue]?")
            new_value = Prompt.ask()
            
            if not Confirm.ask(f"[yellow]Update to [blue]{new_value}[/blue]?"):
                new_value = None
                
        setattr(creator, choices[choice], new_value)
        creator.commit()
        console.print(f"[green]Updated [yellow]{choices[choice]}[/yellow] to [blue]{new_value}[/blue].")

        if not Confirm.ask("Would you like to edit another value?"):
            break

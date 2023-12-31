from rich.prompt import Prompt as _RichPrompt


class Prompt(_RichPrompt):
    """A simple Prompt class from Rich, but editing the suffix to ">"."""

    prompt_suffix = "> "

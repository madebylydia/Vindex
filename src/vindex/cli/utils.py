from rich.prompt import Prompt as _RichPrompt


class Prompt(_RichPrompt):
    prompt_suffix = "> "

from discord.utils import escape_markdown as _escape_markdown
from discord.utils import escape_mentions as _escape_mentions


def bold(text: str) -> str:
    """Make a text bold.

    Parameters
    ----------
    text : str
        The text to add bold markdown to.

    Returns
    -------
    str
        The bold text.
    """
    return f"**{text}**"


def italic(text: str) -> str:
    """Make a text italic.

    Parameters
    ----------
    text : str
        The text to add italic markdown to.

    Returns
    -------
    str
        The italic text.
    """
    return f"*{escape(text, markdown=True)}*"


def underline(text: str) -> str:
    """Make a text underlined.

    Parameters
    ----------
    text : str
        The text to add underline markdown to.

    Returns
    -------
    str
        The underlined text.
    """
    return f"__{escape(text, markdown=True)}__"


def strikethrough(text: str) -> str:
    """Make a text strikethrough.

    Parameters
    ----------
    text : str
        The text to add strikethrough markdown to.

    Returns
    -------
    str
        The strikethrough text.
    """
    return f"~~{text}~~"


def quote(text: str) -> str:
    """Mark a text as quoted.

    Parameters
    ----------
    text : str
        The text to add quote markdown to.

    Returns
    -------
    str
        The quoted text.
    """
    return f"> {text}"


def bold_and_italic(text: str) -> str:
    """Make a text bold and italic.

    Parameters
    ----------
    text : str
        The text to add bold and italic markdown to.

    Returns
    -------
    str
        The bold 'n italic text.
    """
    return f"***{escape(text, markdown=True)}***"


def inline(text: str) -> str:
    """Make a text inlined.

    Parameters
    ----------
    text : str
        The text to add inline markdown to.

    Returns
    -------
    str
        The inlined text.
    """
    if "`" in text:
        return f"``{text}``"
    return f"`{text}`"


def block(text: str, language: str | None = None) -> str:
    """Make a text contained inside a code block.

    Parameters
    ----------
    text : str
        The text to wrap inside a code block.
    language : Optional, str
        The language to use for the code block.
        If none, no language markup will be used.

    Returns
    -------
    str
        The code block.
    """
    if language is None:
        language = ""
    return f"```{language}\n{text}\n```"


def spoiler(text: str) -> str:
    """Put a text inside a spoiler.

    Parameters
    ----------
    text : str
        The text to put inside a spoiler.

    Returns
    -------
    str
        The spoiler.
    """
    return f"||{text}||"


def h1(text: str) -> str:
    """Turn a text into a heading of level 1.

    Parameters
    ----------
    text : str
        The text to turn into a heading of level 1.

    Returns
    -------
    str
        The text with heading level 1.
    """
    return f"# {text}"


def h2(text: str) -> str:
    """Turn a text into a heading of level 2.

    Parameters
    ----------
    text : str
        The text to turn into a heading of level 2.

    Returns
    -------
    str
        The text with heading level 2.
    """
    return f"## {text}"


def h3(text: str) -> str:
    """Turn a text into a heading of level 3.

    Parameters
    ----------
    text : str
        The text to turn into a heading of level 3.

    Returns
    -------
    str
        The text with heading level 3.
    """
    return f"### {text}"


def escape(text: str, *, mentions: bool = False, markdown: bool = True) -> str:
    """Utilitarian function used to escape mentions and markdown from a string.

    Parameters
    ----------
    text : str
        The text to escape.
    mentions : bool
        Whether to escape mentions or not.
        Defaults to ``False``
    markdown : bool
        Whether to escape markdown or not.
        Defaults to ``True``

    Returns
    -------
    str
        The escaped text.
    """
    final = text
    if mentions:
        final = _escape_mentions(final)
    if markdown:
        final = _escape_markdown(final)
    return final

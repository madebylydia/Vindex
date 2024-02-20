import typing
from datetime import datetime, timedelta

from babel.dates import format_datetime as _format_datetime
from babel.dates import format_timedelta as _format_timedelta
from babel.lists import format_list as _format_list
from babel.numbers import format_number as _format_number
from discord.utils import escape_markdown as _escape_markdown
from discord.utils import escape_mentions as _escape_mentions
from discord.utils import utcnow as _utcnow

from vindex.core.i18n import get_babel_current_language

if typing.TYPE_CHECKING:
    from decimal import Decimal


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


def reduce_to(text: str, max_length: int, *, placeholder: str = "...") -> str:
    """Reduce a text to a maximum length.

    Parameters
    ----------
    text : str
        The text to reduce.
    max_length : int
        The maximum length of the text.
    placeholder : str
        The placeholder to use when the text is reduced.
        Defaults to ``"..."``

    Returns
    -------
    str
        The reduced text.
    """
    return text[: max_length - len(placeholder)] + placeholder if len(text) > max_length else text


class Humanize:
    """An utilitarian/factory class used for the "humanization" of strings.

    This class is used to format numbers, dates, etc. in a human-readable way, with formatted
    locale.
    """

    @staticmethod
    def list(
        items: list[str],
        style: typing.Literal[
            "standard", "standard-short", "or", "or-short", "unit", "unit-short", "unit-narrow"
        ] = "standard",
    ) -> str:
        """Humanize a list of items.

        Parameters
        ----------
        items : list[str]
            The list of items to humanize.
        style : str
            The style to use for the humanization.
            Defaults to ``"standard"``.
            See https://babel.pocoo.org/en/latest/api/lists.html

        Returns
        -------
        str
            The humanized list.
        """
        return _format_list(items, style=style, locale=get_babel_current_language())

    @staticmethod
    def number(number: "float | Decimal | str") -> str:
        """Humanize a number.

        Parameters
        ----------
        number : int
            The number to humanize.

        Returns
        -------
        str
            The humanized number.
        """
        return _format_number(number, locale=get_babel_current_language())

    @staticmethod
    def date(
        date: "datetime", date_format: typing.Literal["full", "long", "medium", "short"] = "medium"
    ) -> str:
        """Humanize a date.

        Parameters
        ----------
        date : datetime | date
            The date to humanize.
        date_format : str
            Defaults to ``"medium"``.
            See https://babel.pocoo.org/en/latest/api/dates.html

        Returns
        -------
        str
            The humanized date.
        """
        return _format_datetime(date, locale=get_babel_current_language(), format=date_format)

    @staticmethod
    @typing.overload
    def timedelta(delta: "timedelta") -> str:
        """Humanize a timedelta.

        Parameters
        ----------
        delta : timedelta
            The timedelta to humanize.

        Returns
        -------
        str
            The humanized timedelta.
        """

    @staticmethod
    @typing.overload
    def timedelta(delta: "datetime") -> str:
        """Humanize a datetime, and return it as a timedelta from now.

        Parameters
        ----------
        delta : datetime
            The datetime-as-timedelta to humanize.

        Returns
        -------
        str
            The humanized timedelta.
        """

    @staticmethod
    def timedelta(delta: "timedelta | datetime") -> str:
        """Humanize a timedelta.

        Parameters
        ----------
        delta : timedelta or datetime
            The timedelta to humanize.
            In the case you pass a datetime, it will be converted to a timedelta from now.

        Returns
        -------
        str
            The humanized timedelta.
        """
        if isinstance(delta, datetime):
            delta = _utcnow() - delta
        return _format_timedelta(delta, locale=get_babel_current_language())

from vindex.core.creator.model import Creator

from vindex.core.exceptions.invalid_creator import CreatorException

def get_raw_creator() -> str | None:
    """
    Get the raw content from the creator file.
    May return None if the creator file does not exist.

    Returns
    -------
    str or None :
        The raw content from the creator file.
        None if the file does not exist.
    """
    if not Creator.PATH.exists():
        return None
    return fetch_raw_creator()


def fetch_raw_creator() -> str:
    """
    Fetch the raw content from the creator file.

    Returns
    -------
    str :
        The raw content from the creator file.
    """
    if not Creator.PATH.exists():
        raise CreatorException(Creator.PATH, "Creator file does not exist.")
    with Creator.PATH as file:
        return file.read_text()


def get_creator() -> Creator | None:
    """
    Get a Creator model.
    May return None if the creator file does not exist.

    Raises
    ------
    :py:exc:`pydantic.ValidationError` :
        If the creator file cannot be validated against the model.

    Returns
    -------
    :py:class:`vindex.core.creator.model.Creator` or None :
        The creator from the creator file.
        None if the file does not exist.
    """
    if not Creator.PATH.exists():
        return None
    return fetch_creator()


def fetch_creator() -> Creator:
    """
    Create a Creator model.

    Raises
    ------
    :py:exc:`vindex.core.exceptions.invalid_creator.CreatorException` :
        If the creator file does not exist.
    :py:exc:`pydantic.ValidationError` :
        If the creator file cannot be validated against the model.

    Returns
    -------
    :py:class:`vindex.core.creator.model.Creator` :
        The creator from the creator file.
    """
    return Creator.model_validate_json(fetch_raw_creator())

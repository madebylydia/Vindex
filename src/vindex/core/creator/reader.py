from vindex.core.creator.model import Creator
from vindex.core.exceptions.invalid_creator import CreatorException


def fetch_raw_creator() -> str:
    """Fetch the raw content from the creator file.

    Returns
    -------
    str :
        The raw content from the creator file.
    """
    if not Creator.PATH.exists():
        raise CreatorException(Creator.PATH, "Creator file does not exist.")
    with Creator.PATH as file:
        return file.read_text()


def fetch_creator() -> Creator:
    """Create a Creator model.

    Raises
    ------
    :py:exc:`pydantic.ValidationError` :
        If the creator file cannot be validated against the model.

    Returns
    -------
    :py:class:`vindex.core.creator.model.Creator` :
        The creator from the creator file.
    """
    if not Creator.PATH.exists():
        return Creator(instances={})
    return Creator.model_validate_json(fetch_raw_creator())

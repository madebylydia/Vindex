import pathlib

from .base import VindexException


class CreatorException(VindexException):
    creator_location: pathlib.Path

    def __init__(self, creator_location: pathlib.Path, reason: str) -> None:
        super().__init__(
            "Error with Creator object.\n"
            f"Location: {creator_location.resolve()}\n"
            f"Reason: {reason}"
        )

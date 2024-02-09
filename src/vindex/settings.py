import dataclasses
import os


@dataclasses.dataclass
class Settings:
    """A settings manager taking information from environment variables."""

    token: str
    database_url: str


def read_settings() -> Settings:
    """Read settings from environment variables."""
    return Settings(
        token=os.environ["VINDEX_TOKEN"],
        database_url=os.environ["VINDEX_DB_URL"],
    )

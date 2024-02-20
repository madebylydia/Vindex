import dataclasses
import logging
import os

_log = logging.getLogger(__name__)


@dataclasses.dataclass
class Settings:
    """A settings manager taking information from environment variables."""

    token: str
    database_url: str


def read_settings() -> Settings:
    """Read settings from environment variables."""
    db_url = os.environ.get("VINDEX_DB_URL")

    if not db_url:
        _log.warning(
            "VINDEX_DB_URL is not set, trying to create one from other environment variables"
        )
        # VINDEX_DB_URL is not set, so we might as well try to create one if possible
        pg_user = os.environ.get("POSTGRES_USER")
        if not pg_user:
            raise ValueError("VINDEX_DB_URL or POSTGRES_USER must be set")

        pg_password = os.environ.get("POSTGRES_PASSWORD")
        if not pg_password:
            raise ValueError("VINDEX_DB_URL or POSTGRES_PASSWORD must be set")

        pg_db = os.environ.get("POSTGRES_DB")
        if not pg_db:
            raise ValueError("VINDEX_DB_URL or POSTGRES_DB must be set")

        pg_port = os.environ.get("POSTGRES_PORT", "5432")

        # Host shouldn't change, unless you're using a different service name...
        # *sigh* anyone that doesn't uses Docker should not bother me... hopefullyyyyyy?
        db_url = f"postgresql://{pg_user}:{pg_password}@db:{pg_port}/{pg_db}"

    return Settings(
        token=os.environ["VINDEX_TOKEN"],
        database_url=db_url,
    )

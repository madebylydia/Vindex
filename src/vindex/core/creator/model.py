import typing

import pydantic
from platformdirs import user_config_path


class Creator(pydantic.BaseModel):
    """The Creator model is a Object Oriented Model for the Creator file.
    It is used by Pydantic to succesfully parse the file.
    """

    PATH: typing.ClassVar = (
        user_config_path("vindex", ensure_exists=True) / "creator.json"
    ).resolve()

    model_config = pydantic.ConfigDict(strict=True)

    token: str
    prefix: str

    database_name: str
    database_user: str
    database_password: str
    database_host: str

    def build_db_url(self) -> str:
        """Build the database URL from the given informations.

        Returns
        -------
        str
            The database URL.
        """
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}/{self.database_name}"
        )

    def commit(self):
        """Commit the Creator to the file system.

        Raises
        ------
        :py:exc:`pydantic.ValidationError` :
            If the Creator cannot be validated.
        """
        self.model_rebuild()
        with self.PATH as file:
            file.write_text(self.model_dump_json())

import typing

import pydantic
from platformdirs import user_config_path


class Creator(pydantic.BaseModel):
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

    def build_db_url(self):
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

    def commit(self):
        with self.PATH as file:
            file.write_text(self.model_dump_json())

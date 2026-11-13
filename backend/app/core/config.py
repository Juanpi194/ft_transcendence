from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: PostgresDsn
    """
    Looks for an environment variable that is named the same way the
    variable is (does not care about uppercase or lowercase).
    When using it, cast it to str.
    """


settings = Settings()

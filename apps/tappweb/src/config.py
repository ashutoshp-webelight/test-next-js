import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn, validator


load_dotenv(override=True)


class Settings(BaseSettings):
    """
    A settings class for the project defining all the necessary parameters within the
    app through an object.
    """

    APP_NAME: str = os.getenv("APP_NAME")
    APP_VERSION: str = os.getenv("APP_VERSION")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")

    DATABASE_USER: Optional[str] = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD: Optional[str] = os.getenv("DATABASE_PASSWORD")
    DATABASE_HOST: Optional[str] = os.getenv("DATABASE_HOST")
    DATABASE_PORT: Optional[str] = os.getenv("DATABASE_PORT")
    DATABASE_NAME: Optional[str] = os.getenv("DATABASE_NAME")

    DATABASE_URL: Optional[PostgresDsn] = os.getenv("DATABASE_URL")

    @validator("DATABASE_URL", pre=True)
    def assemble_db_url(cls, v, values) -> str:
        """
        Create a Database URL from the settings provided in the .env file.
        """
        if isinstance(v, str):
            return v
        try:
            return PostgresDsn.build(
                scheme="postgresql+asyncpg",
                user=values.get("DATABASE_USER"),
                password=values.get("DATABASE_PASSWORD"),
                host=values.get("DATABASE_HOST"),
                port=values.get("DATABASE_PORT"),
                path=f"/{values.get('DATABASE_NAME')}",
            )
        except Exception:
            raise ValueError("Neither DATABASE_URL nor DATABASE_* environment variables set!")


settings = Settings()

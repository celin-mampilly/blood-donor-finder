from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    db_host: str
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str
    db_password: str
    secret_key: str
    access_token_minutes: int = 1440

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )


settings = Settings()
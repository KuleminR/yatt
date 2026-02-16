from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironmentType(Enum):
    DEV = "development"
    PROD = "production"
    TEST = "test"


class AppConfig(BaseSettings):
    environment: AppEnvironmentType = AppEnvironmentType.PROD


class DBConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="database_")

    hostname: str
    port: str
    name: str
    user: str
    password: str


app_config = AppConfig()
db_config = DBConfig()

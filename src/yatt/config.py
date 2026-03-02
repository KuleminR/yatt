from enum import Enum
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironmentType(Enum):
    DEV = "development"
    PROD = "production"
    TEST = "test"


class LogLevels(Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="app_")

    environment: AppEnvironmentType = AppEnvironmentType.PROD
    log_level: LogLevels = LogLevels.INFO


class DBConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="database_")

    hostname: str
    port: str
    name: str
    user: str
    password: SecretStr


app_config = AppConfig()
db_config = DBConfig()

config = {"application_config": app_config, "database_config": db_config}

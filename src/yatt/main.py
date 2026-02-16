from typing import Any
from fastapi import FastAPI

from yatt.config import app_config, AppEnvironmentType


fastapi_config: dict[str, Any] = {
    "title": "Yet Another Task Tracker",
    "description": "Simple task tracking web application",
}


if app_config.environment in [AppEnvironmentType.PROD, AppEnvironmentType.TEST]:
    fastapi_config["openapi_url"] = None

app = FastAPI(**fastapi_config)

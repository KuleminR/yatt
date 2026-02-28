from typing import Any
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from yatt.config import app_config, AppEnvironmentType
from yatt.api import api_router


fastapi_config: dict[str, Any] = {
    "title": "Yet Another Task Tracker",
    "description": "Simple task tracking web application",
}


if app_config.environment in [AppEnvironmentType.PROD, AppEnvironmentType.TEST]:
    fastapi_config["openapi_url"] = None

app = FastAPI(**fastapi_config)

app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_error(request, exc: RequestValidationError):
    """Custom handler to produce formatted error in json"""
    output = {"errors": []}
    for error in exc.errors():
        error = {
            "type": "validation_error",
            "msg": error["msg"],
            "details": {"loc": ".".join(error["loc"])},
        }

        output["errors"].append(error)

    return JSONResponse(
        content=output, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )

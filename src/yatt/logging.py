import logging

from yatt.config import app_config

logging.basicConfig(level=app_config.log_level.value)

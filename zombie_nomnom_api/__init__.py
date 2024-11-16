"""
.. include:: ../README.md
   :start-line: 2
   :end-before: Contribution
"""

from pydantic_settings import BaseSettings
import logging


class Configs(BaseSettings):
    cors_methods: set[str] = ["*"]
    cors_headers: set[str] = ["*"]
    cors_origins: set[str] = ["*"]
    cors_allow_credentials: bool = True
    log_level: str = "DEBUG"


configs = Configs()


logging.basicConfig(level=configs.log_level)

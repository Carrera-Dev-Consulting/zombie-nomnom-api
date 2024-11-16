"""
.. include:: ../README.md
   :start-line: 2
   :end-before: Contribution
"""

import logging
from enum import Enum
from pydantic_settings import BaseSettings
from zombie_nomnom_api.db.client import get_client, MongoClient


class PersistenceModes(Enum):
    IN_MEM = 1
    MONGO = 2



class Configs(BaseSettings):
    cors_methods: set[str] = ["*"]
    cors_headers: set[str] = ["*"]
    cors_origins: set[str] = ["*"]
    cors_allow_credentials: bool = True
    log_level: str = "DEBUG"
    persistence_mode_config: int = 1
    mongo_connection: str
    game_collection_name: str = "games"
    
    
    @property
    def mongo_client(self) -> MongoClient:
        return get_client(self.mongo_connection)

    @property
    def game_collection(self):
        client = get_client(self.mongo_connection)
        return client[self.game_collection_name]
    
    @property
    def persistence_mode(self):
        return PersistenceModes(self.persistence_mode_config)


configs = Configs()


logging.basicConfig(level=configs.log_level)

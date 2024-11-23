from pymongo import MongoClient


def get_client_mongo(connection_string: str) -> MongoClient:
    if not connection_string:
        return None

    return MongoClient(connection_string)

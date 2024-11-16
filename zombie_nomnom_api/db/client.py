from pymongo import MongoClient


def get_client(connection_string: str) -> MongoClient:
    if not connection_string:
        return None
    
    return MongoClient(connection_string)
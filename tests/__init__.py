import os

os.environ["MONGO_CONNECTION"] = "mongodb://test_user:admin@mongo:27017/zombie_nomnom"
os.environ["OAUTH_DOMAIN"] = "required"
os.environ["OAUTH_ISSUER"] = "is"
os.environ["OAUTH_AUDIENCE"] = "that"
os.environ["OAUTH_ALGORITHMS"] = "stuff"

from fastapi import FastAPI
from importlib.metadata import version
from .graphql_app import graphql_app

try:
    _version = version("zombie-nomnom-api")
except:
    _version = "dev"

fastapi_app = FastAPI(
    title="Zombie Nom Nom API",
    version=_version,
)


@fastapi_app.get("/healthz")
def healthz():
    return {"o": "k"}


fastapi_app.mount("/", graphql_app)

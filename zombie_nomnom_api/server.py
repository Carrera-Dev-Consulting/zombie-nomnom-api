from fastapi import FastAPI
from importlib.metadata import version

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

from fastapi import FastAPI
from importlib.metadata import version
from .graphql_app import graphql_app
from fastapi.middleware.cors import CORSMiddleware
from zombie_nomnom_api import configs

try:
    _version = version("zombie-nomnom-api")
except:
    _version = "dev"

fastapi_app = FastAPI(
    title="Zombie Nom Nom API",
    version=_version,
)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=configs.cors_origins,
    allow_credentials=configs.cors_allow_credentials,
    allow_methods=configs.cors_methods,
    allow_headers=configs.cors_headers,
)


@fastapi_app.get("/healthz")
def healthz():
    return {"o": "k"}


@fastapi_app.get("/version")
def version():
    return {"version": _version}


fastapi_app.mount("/", graphql_app)

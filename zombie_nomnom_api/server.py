"""
FastAPI Server Configuration for Zombie Nom Nom API

This module sets up the main FastAPI application with middleware, authentication,
and routing for the Zombie Dice game API. It includes CORS configuration,
JWT token verification middleware, and basic health/version endpoints.

The server combines GraphQL functionality (mounted at root) with REST endpoints
for health checks, version information, and user authentication.
"""

from fastapi import FastAPI, HTTPException, Request
from importlib.metadata import version

from fastapi.responses import JSONResponse

from .graphql_app import graphql_app
from fastapi.middleware.cors import CORSMiddleware
from zombie_nomnom_api import configs
from zombie_nomnom_api.rest_app.authentication import (
    get_verifier,
    token_auth_scheme,
)


try:
    _version = version("zombie-nomnom-api")
except:  # pragma: no cover
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


@fastapi_app.middleware("http")
async def hydrate_user(
    request: Request,
    call_next,
):
    """
    HTTP middleware to authenticate and hydrate user information from JWT tokens.
    
    This middleware extracts JWT tokens from requests, verifies them using OAuth,
    and adds user information to the request state. If authentication fails,
    appropriate error responses are returned.
    
    Args:
        request (Request): The incoming HTTP request
        call_next: The next middleware/handler in the chain
        
    Returns:
        Response: Either the next handler's response or an authentication error
    """
    try:
        token = await token_auth_scheme(request)
    except HTTPException as e:
        if e.detail == "Not authenticated":
            return await call_next(request)
        return JSONResponse(
            {"status": "error", "message": "Not Authenticated"}, status_code=401
        )

    result = get_verifier().verify(token.credentials)

    if result.get("status"):
        return JSONResponse(result, status_code=403)
    request.state.user = result
    return await call_next(request)


@fastapi_app.get("/healthz")
def healthz():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: Simple status object indicating the service is operational
    """
    return {"o": "k"}


@fastapi_app.get("/version")
def version():
    """
    Version information endpoint.
    
    Returns:
        dict: Object containing the current API version
    """
    return {"version": _version}


@fastapi_app.get("/me")
def get_me(request: Request):
    """
    User information endpoint that returns authenticated user details.
    
    This endpoint returns the user information that was populated by the
    authentication middleware, or None if no user is authenticated.
    
    Args:
        request (Request): The HTTP request containing user state
        
    Returns:
        dict | None: User information or None if not authenticated
    """
    return getattr(request.state, "user", None)


fastapi_app.mount("/", graphql_app)

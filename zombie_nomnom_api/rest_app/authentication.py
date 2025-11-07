"""
JWT Authentication Module for REST API

This module provides JWT token verification functionality for the Zombie Nom Nom API.
It integrates with OAuth providers to validate tokens and extract user information
for authentication and authorization purposes.

Key Components:
    - VerifyToken: Main class for JWT verification
    - HTTPBearer: FastAPI security scheme for extracting Bearer tokens
    - Cached verifier instance for performance optimization

The module supports verification of:
    - Token signatures using JWKS
    - Token expiration and standard claims
    - Custom scopes and permissions
"""

from functools import cache
from fastapi.security import HTTPBearer
import jwt
from jwt.exceptions import PyJWKClientError, DecodeError
from zombie_nomnom_api import configs


token_auth_scheme = HTTPBearer()
"""FastAPI security scheme for extracting Bearer tokens from Authorization headers."""


def create_error_json(message: str) -> dict[str, str]:
    """
    Create a standardized error response dictionary.

    Args:
        message (str): The error message to include

    Returns:
        dict[str, str]: Standardized error response with status and message
    """
    return {"status": "error", "message": message}


class VerifyToken:
    """
    JWT token verification class for OAuth-based authentication.

    This class handles verification of JWT tokens issued by an OAuth provider.
    It validates token signatures, expiration, audience, and issuer claims,
    and can also verify custom scopes and permissions.

    Attributes:
        config (zombie_nomnom_api.Configs): Configuration containing OAuth settings
        jwks_client (jwt.PyJWKClient): Client for retrieving JWT signing keys
    """

    def __init__(self, configs=configs):
        """
        Initialize the token verifier with OAuth configuration.

        Args:
            configs (zombie_nomnom_api.Configs): Configuration object containing
                OAuth domain, algorithms, audience, and issuer settings
        """
        self.config = configs

        jwks_url = f"https://{self.config.oauth_domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self, token: str, permissions: list = None, scopes: list | str = None):
        """
        Verify a JWT token and optionally check scopes and permissions.

        This method validates the token signature, expiration, audience, and issuer.
        It can also verify that the token contains required scopes and permissions.

        Args:
            token (str): The JWT token to verify
            permissions (list, optional): List of required permissions
            scopes (list | str, optional): Required scopes as list or space-separated string

        Returns:
            dict: Either the decoded token payload or an error response
                 Error response format: {"status": "error", "message": "..."}
                 Success response: The full JWT payload as a dictionary
        """
        # This gets the 'kid' from the passed token
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token).key
        except PyJWKClientError as error:
            return create_error_json(str(error))
        except DecodeError as error:
            return create_error_json(str(error))

        try:
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=self.config.oauth_algorithms,
                audience=self.config.oauth_audience,
                issuer=self.config.oauth_issuer,
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        if scopes:
            result = self._check_claims(
                payload,
                "scope",
                str,
                scopes if isinstance(scopes, list) else scopes.split(" "),
            )
            if result.get("status") == "error":
                return result

        if permissions:
            result = self._check_claims(payload, "permissions", list, permissions)
            if result.get("status") == "error":
                return result

        return payload

    def _check_claims(
        self, payload: dict, claim_name: str, claim_type: type, expected_value: list
    ):
        """
        Verify that the JWT payload contains required claims with expected values.

        This internal method checks that a specific claim exists in the JWT payload,
        has the correct type, and contains all required values.

        Args:
            payload (dict): The decoded JWT payload
            claim_name (str): Name of the claim to check (e.g., "scope", "permissions")
            claim_type (type): Expected type of the claim value
            expected_value (list): List of values that must be present in the claim

        Returns:
            dict: Success response or error response
                 Success: {"status": "success", "status_code": 200}
                 Error: {"status": "error", "message": "..."}
        """
        payload_claim = payload.get(claim_name)
        if payload_claim is None or not isinstance(payload[claim_name], claim_type):
            return create_error_json(
                f"User does not have the required '{claim_name}' claim."
            )
        result = {"status": "success", "status_code": 200}

        if claim_name == "scope":
            payload_claim = payload_claim.split(" ")

        for value in expected_value:
            if value not in payload_claim:
                return create_error_json(
                    f"User does not have the required '{claim_name}' claim."
                )
        return result


@cache
def get_verifier() -> VerifyToken:
    """
    Get a cached instance of the token verifier.

    This function provides a singleton instance of VerifyToken that is
    cached for the lifetime of the application to avoid recreating
    the JWKS client repeatedly.

    Returns:
        VerifyToken: Cached token verifier instance
    """
    return VerifyToken()

from functools import cache
from fastapi.security import HTTPBearer
import jwt
from zombie_nomnom_api import configs
from zombie_nomnom_api.rest_app.custom_exceptions import (
    UnauthenticatedException,
    UnauthorizedException,
)

token_auth_scheme = HTTPBearer()


class VerifyToken:
    def __init__(self, configs=configs):
        """
        Args:
            configs (zombie_nomnom_api.Configs): The Configs that hold the domain for the oauth server.

        Attributes:
            config (zombie_nomnom_api.Configs): The Configs that hold the domain for the oauth server.
            jwks_client (jwt.PyJWKClient): A jwt client that is used to verify the tokens.
        """
        self.config = configs

        jwks_url = f"https://{self.config.oauth_domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self, token: str, permissions=None, scopes=None):
        # This gets the 'kid' from the passed token
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}

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
            result = self._check_claims(payload, "scope", str, scopes.split(" "))
            if result.get("error"):
                return result

        if permissions:
            result = self._check_claims(payload, "permissions", list, permissions)
            if result.get("error"):
                return result

        return payload

    def _check_claims(self, payload, claim_name, claim_type, expected_value):

        instance_check = isinstance(payload[claim_name], claim_type)
        result = {"status": "success", "status_code": 200}

        payload_claim = payload[claim_name]

        if claim_name not in payload or not instance_check:
            raise UnauthenticatedException

        if claim_name == "scope":
            payload_claim = payload[claim_name].split(" ")

        for value in expected_value:
            if value not in payload_claim:
                raise UnauthorizedException(
                    f"User does not have the required '{claim_name}' claim."
                )
        return result


@cache
def get_verifier() -> VerifyToken:
    return VerifyToken()

import jwt
import re
from pydantic import EmailStr
from datetime import timedelta, datetime

from auth.schemas import Decoded_Token, Encoded_Token
from core.config import settings


class TokenHandler():

    def encode_token(user_id: int, token_type: str) -> Encoded_Token:
        """
        Encode a token to be used in requests. This is a helper
        method to encode an auth token that can be used in requests.

        Args:
            uuid: The UUID of the user
            username: The username of the user ( if any )
            token_type: specifies which token to create: 'Refresh' or 'Access'

        Returns:
            The encoded token as a base64 - encoded string. Note that you must
            add the token yourself.
        """
        if token_type.lower() != "access" and token_type.lower() != "refresh":
            raise ValueError(
                "Error, token type passed must be either an 'Access' or 'Refresh' token")

        payload = {
            "iss": "https://www.Final-Labz.com",
            "exp": datetime.utcnow() + timedelta(days=0, hours=0, minutes=15),
            "iat": datetime.utcnow(),
            "user_id": user_id,
            "token_type": token_type
        }

        if token_type.lower() == "refresh":
            payload["exp"] = datetime.utcnow() + timedelta(
                days=14, hours=0, minutes=0)

        payload = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        return Encoded_Token(token=payload)

    def decode_token(token: str) -> Decoded_Token:
        """
        Decodes a JWT token. This is a wrapper around jwt.decode
        to handle exceptions that are raised in the process.

        Args:
            token: The JWT token to decode

        Returns:
            The payload of the JWT token as a TokenSchema or
            returns a Falsey value if the token is invalid.
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms="HS256")
        except jwt.ExpiredSignatureError as exc:
            raise exc
        except jwt.InvalidTokenError as exc:
            raise exc
        return Decoded_Token(**payload)

    def grant_access(self, email: EmailStr, token: str):
        """
        Check if token is valid. This is used to verify that
        a user has access to the resource identified by token.

        Args:
            token: Token obtained from token_generator
            uuid: UUID of the resource being accessed

        Returns:
            True if access is granted False if access is not
            granted and exception is raised if token is not valid.
        """
        decoded: Decoded_Token = self.decode_token(token)
        # Returns true if uuid is not equal to decoded. uuid.
        if email != decoded.email:
            return False
        return True


def check_password_strength(password) -> bool:
    # Check if the password contains at least one letter
    if not re.search('[a-zA-Z]', password):
        raise ValueError("Password must contain at least one letter")

    # Check if the password contains at least one number
    if not re.search('[0-9]', password):
        raise ValueError("Password must contain at least one number")

    # Check if the password contains at least one special character
    if not re.search('[!@#$%^&*()_+{}|:"<>?]', password):
        raise ValueError(
            "Password must contain at least one special character (!@#$%^&*()_+{}|:\"<>?)")

    # Check if the password is at least 8 characters long
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    # If all conditions are met, return True indicating the password is strong
    return True

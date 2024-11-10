import binascii
import datetime
import hashlib

import bcrypt
import jwt

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(subject: str, /, *, expires_delta: datetime.timedelta) -> str:
    """
    Create an access token using JWT (JSON Web Token).

    This function generates a JWT that encodes a subject and an expiration time.
    The token is signed with a secret key using a specified algorithm.

    Args:
        subject (str): The subject (typically a user identifier) that the token represents.
        expires_delta (datetime.timedelta): The duration for which the token is valid.

    Returns:
        str: The encoded JWT as a string.

    Raises:
        Exception: Raises an exception if token encoding fails.
    """
    expire = datetime.datetime.now(datetime.UTC) + expires_delta
    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str) -> str:
    """
    Generate a hashed password using bcrypt.

    This function takes a plaintext password, generates a SHA-256 hash of it,
    and then hashes that hash using bcrypt with a randomly generated salt.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        str: The hashed password encoded as an ASCII string.
    """
    salt = bcrypt.gensalt(rounds=12)
    sha256_hash = hashlib.sha256(password.encode()).digest()
    hex_password = binascii.hexlify(sha256_hash)
    hashed_password = bcrypt.hashpw(hex_password, salt)
    return hashed_password.decode("ascii")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    This function checks whether the SHA-256 hash of the given plaintext password
    matches the provided hashed password.

    Args:
        password (str): The plaintext password to verify.
        hashed_password (str): The previously hashed password to check against.

    Returns:
        bool: True if the plaintext password matches the hashed password, False otherwise.
    """
    sha256_hash = hashlib.sha256(password.encode()).digest()
    hex_password = binascii.hexlify(sha256_hash)
    return bcrypt.checkpw(hex_password, hashed_password.encode("ascii"))

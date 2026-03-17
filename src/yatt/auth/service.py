import jwt
from datetime import datetime, timedelta, timezone
from uuid import UUID
from pwdlib import PasswordHash

from yatt.auth.models import AccessToken
from yatt.config import app_config

password_hash = PasswordHash.recommended()


DUMMY_HASH = password_hash.hash("dummy_pass")
ALGORITHM = "HS256"
ACCESS_TOKEN_SECRET = app_config.access_token_secret.get_secret_value()


def hash_password(password) -> str:
    return password_hash.hash(password)


def verify_password(password, stored_hash) -> bool:
    return password_hash.verify(password, stored_hash)


def create_access_token(
    user_identity: UUID,
    expires_in: timedelta,
    permissions: list[str],
) -> str:
    token = AccessToken(
        sub=str(user_identity),
        exp=datetime.now(timezone.utc) + expires_in,
        scopes=permissions,
    )

    data = token.model_dump()
    data["scopes"] = ",".join(data["scopes"])

    encoded_jwt = jwt.encode(data, ACCESS_TOKEN_SECRET, algorithm=ALGORITHM)

    return encoded_jwt

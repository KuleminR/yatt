from datetime import datetime, timezone
import logging
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from yatt.auth.models import AccessToken
from yatt.auth.service import ACCESS_TOKEN_SECRET, ALGORITHM


logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_verified_access_token(
    raw_token: Annotated[str, Depends(oauth2_scheme)],
) -> AccessToken:
    try:
        payload = jwt.decode(
            raw_token,
            ACCESS_TOKEN_SECRET,
            algorithms=[ALGORITHM],
        )
    except InvalidTokenError as e:
        logger.debug(e)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    exp = datetime.fromtimestamp(payload["exp"], timezone.utc)
    scopes = payload["scopes"].split(",")

    return AccessToken(sub=payload["sub"], exp=exp, scopes=scopes)

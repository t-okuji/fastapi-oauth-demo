from datetime import datetime, timedelta, timezone

import jwt
import requests
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import APIKeyCookie
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from settings import Settings


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    sub: str
    email: str | None = None


settings = Settings()
cookie_scheme = APIKeyCookie(name="access_token")
app = FastAPI()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(access_token: str = Depends(cookie_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str = payload.get("sub")
        email: str = payload.get("email")
        if sub is None and email is None:
            raise credentials_exception
        token_data = User(sub=sub, email=email)
    except InvalidTokenError:
        raise credentials_exception

    return token_data


async def verify_google_id_token(id_token: str) -> User:
    # Get configuration
    openid_configuration = requests.get(
        "https://accounts.google.com/.well-known/openid-configuration"
    ).json()
    key_url = openid_configuration["jwks_uri"]
    issuer = openid_configuration["issuer"]

    keys = requests.get(key_url).json()["keys"]
    header = jwt.get_unverified_header(id_token)
    for key in keys:
        if key["kid"] == header["kid"]:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            break
    claims = jwt.decode(
        id_token,
        public_key,
        issuer=issuer,
        audience=settings.GOOGLE_CLIENT_ID,
        algorithms=["RS256"],
    )

    user_info = User(sub=claims["sub"], email=claims["email"])

    return user_info


async def verify_apple_id_token(id_token: str) -> User:
    # Get configuration
    openid_configuration = requests.get(
        "https://appleid.apple.com/.well-known/openid-configuration"
    ).json()
    key_url = openid_configuration["jwks_uri"]
    issuer = openid_configuration["issuer"]

    keys = requests.get(key_url).json()["keys"]
    header = jwt.get_unverified_header(id_token)
    for key in keys:
        if key["kid"] == header["kid"]:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            break
    claims = jwt.decode(
        id_token,
        public_key,
        issuer=issuer,
        audience=settings.APPLE_CLIENT_ID,
        algorithms=["RS256"],
    )

    user_info = User(sub=claims["sub"], email=claims["email"])

    return user_info

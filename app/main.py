import secrets
from typing import Annotated

import requests
from fastapi import Cookie, FastAPI, Form, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from settings import Settings

app = FastAPI()

# load .env
settings = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONT_URL,
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/auth/google_auth")
async def google_auth(response: Response):
    """Generate Google Auth URL

    Returns:
        str: URL
    """

    # Generate state for prevent CSRF attack
    state = secrets.token_urlsafe()

    google_auth_url = (
        f"{settings.GOOGLE_AUTH_URI}?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"prompt=select_account consent&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_mode=form_post&"
        f"response_type=code&"
        f"scope=email&"
        f"state={state}"
    )
    response = RedirectResponse(google_auth_url, status_code=302)

    response.set_cookie(
        key="authstate",
        value=state,
        httponly=True,
        secure=True,
        samesite="None",  # When developing (Lax for production)
    )
    return response


@app.post("/auth/google_auth/callback")
async def google_auth_callback2(
    response: Response,
    code: str = Form(),
    state: str = Form(),
    authstate: Annotated[str | None, Cookie()] = None,
):
    """Verify authorization code

    Args:
        response (Response): fastapi Response
        code (str, optional): Authorization code

    Raises:
        HTTPException: 401 500

    Returns:
        RedirectResponse: 302 response
    """

    # Check state for prevent CSRF attack
    if state != authstate:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    body_data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    }

    auth_response = requests.post(url=f"{settings.GOOGLE_TOKEN_URI}", json=body_data)
    try:
        auth_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response = RedirectResponse(f"{settings.FRONT_URL}/me", status_code=302)

    response.set_cookie(
        key="token",
        value="dummy_token",
        httponly=True,
        secure=True,
        samesite="Lax",
    )
    return response

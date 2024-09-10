import secrets
from typing import Annotated

import requests
from fastapi import APIRouter, Cookie, Form, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from settings import Settings

router = APIRouter()
settings = Settings()


@router.get("/auth/apple_auth")
async def apple_auth(response: Response):
    """Generate Apple Auth URL

    Returns:
        str: URL
    """

    # Generate state for prevent CSRF attack
    state = secrets.token_urlsafe()

    apple_auth_url = (
        f"{settings.APPLE_AUTH_URI}?"
        f"client_id={settings.APPLE_CLIENT_ID}&"
        f"redirect_uri={settings.APPLE_REDIRECT_URI}&"
        f"response_mode=form_post&"
        f"response_type=code&"
        f"scope=email&"
        f"state={state}"
    )
    response = RedirectResponse(apple_auth_url, status_code=302)

    response.set_cookie(
        key="authstate",
        value=state,
        httponly=True,
        secure=True,
        samesite="None",  # When developing (Lax for production)
    )
    return response


@router.post("/auth/apple_auth/callback")
async def apple_auth_callback(
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
        "client_id": settings.APPLE_CLIENT_ID,
        "client_secret": settings.APPLE_CLIENT_SECRET,
        "redirect_uri": settings.APPLE_REDIRECT_URI,
    }

    auth_response = requests.post(url=f"{settings.APPLE_TOKEN_URI}", data=body_data)
    try:
        auth_response.raise_for_status()
    except requests.exceptions.HTTPError:
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

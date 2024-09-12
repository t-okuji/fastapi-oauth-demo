import secrets
from datetime import timedelta
from typing import Annotated, Optional

import requests
from core.auth import create_access_token, verify_google_id_token
from fastapi import APIRouter, Cookie, Form, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from settings import Settings

router = APIRouter()
settings = Settings()


@router.get("/auth/google_auth")
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


@router.post("/auth/google_auth/callback")
async def google_auth_callback(
    response: Response,
    code: Optional[str] = Form(None),
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

    if code is None:
        response = RedirectResponse(f"{settings.FRONT_URL}/", status_code=302)
        return response

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

    auth_response = requests.post(url=f"{settings.GOOGLE_TOKEN_URI}", data=body_data)

    try:
        auth_response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Get claim
    id_token = auth_response.json()["id_token"]
    user_info = await verify_google_id_token(id_token=id_token)

    # Generate access_token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_info.sub, "email": user_info.email},
        expires_delta=access_token_expires,
    )

    response = RedirectResponse(f"{settings.FRONT_URL}/me", status_code=302)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="None",  # When developing (Lax for production)
    )
    return response

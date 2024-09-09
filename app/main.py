import requests
from fastapi import FastAPI, Form, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from settings import Settings

app = FastAPI()

# load .env
settings = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/auth/google_auth")
async def google_auth(response: Response):
    """Create Google Auth URL

    Returns:
        str: URL
    """
    google_auth_url = (
        f"{settings.GOOGLE_AUTH_URI}?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"prompt=select_account consent&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_mode=form_post&"
        f"response_type=code&"
        f"scope=email"
    )
    response = PlainTextResponse(google_auth_url)

    return response


@app.post("/auth/google_auth/callback")
async def google_auth_callback2(response: Response, code: str = Form()):
    """Verify authorization code

    Args:
        response (Response): fastapi Response
        code (str, optional): Authorization code

    Raises:
        HTTPException: Error

    Returns:
        RedirectResponse: 302 response
    """
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

    response = RedirectResponse("http://localhost:5173/me", status_code=302)

    response.set_cookie(
        key="token",
        value="dummy_token",
        httponly=True,
        secure=True,
        samesite="Lax",
    )
    return response

from typing import Annotated

from core.auth import User, get_current_user
from fastapi import APIRouter, Depends, Response
from settings import Settings

router = APIRouter()
settings = Settings()


@router.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.post("/logout")
async def logout(
    response: Response,
) -> dict[str, str]:
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="None",  # When developing (Lax for production)
    )

    # クッキーの削除
    return {"message": "Logout Success"}

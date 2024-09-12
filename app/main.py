from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import apple, auth, google
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


app.include_router(google.router, tags=["Google Auth"])
app.include_router(apple.router, tags=["Apple Auth"])
app.include_router(auth.router, tags=["JWT token"])

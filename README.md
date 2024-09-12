# OAuth2 Demo (Backend FastAPI)
This project is OAuth2 Demo created with FastAPI.

Frontend is [here (React)](https://github.com/t-okuji/react-oauth-demo).

## Implemented

- Google
- Apple

## Getting started

### dev

```
docker compose up --build
http://localhost:8080
```

### debug

```
TARGET=debug docker compose up --build
http://localhost:8080
```

F5 to launch the debugger. 

### Build image

```
docker build --target prod -t fastapi-oauth-demo . --platform linux/amd64
```

`--platform linux/amd64` option is for Mac with Apple sillicon.


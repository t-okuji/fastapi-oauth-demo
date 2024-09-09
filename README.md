# Python + FastAPI + aws-lambda-web-adapter
This project is lambda function in Python.

## Libraries
- `fastapi` Web framework
- `poetry` Package manager
- `ruff` Linter and Formatter
  - `poetry run ruff <commands>`
- `pre-commit` Git hook
  - `poetry run pre-commit run --all-files` Run hook

## Getting started local
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

## Build image
```
docker build --target prod -t python-lambda . --platform linux/amd64
```

`--platform linux/amd64` option is for Mac with Apple sillicon.


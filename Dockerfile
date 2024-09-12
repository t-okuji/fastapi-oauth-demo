FROM public.ecr.aws/docker/library/python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.8.3
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN apt update && apt install curl -y

# Development
FROM base AS dev
COPY ./pyproject.toml ./poetry.lock ./
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry install
WORKDIR /app
ENTRYPOINT [ "fastapi" ]
CMD [ "dev", "main.py", "--host", "0.0.0.0", "--port", "8080" ]

# Builder for prod
FROM base AS builder
COPY ./pyproject.toml ./poetry.lock ./
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.8.3
# Install only dependencies
RUN poetry install --only main

# Production for lambda
FROM public.ecr.aws/docker/library/python:3.12-slim AS prod
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/fastapi /usr/local/bin/fastapi
# change lambda-web-adapter listen port (default port 8080)
ENV PORT 8000
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter
COPY ./app/. /app/
WORKDIR /app
ENTRYPOINT [ "fastapi" ]
CMD [ "run", "main.py" ]

# Debug
FROM base AS debug
COPY ./pyproject.toml ./poetry.lock ./
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry install
WORKDIR /app
CMD [ "python3", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload" ]
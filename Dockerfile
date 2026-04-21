FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app

WORKDIR /app
RUN uv sync --locked --no-cache

CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "8088",  "--host", "0.0.0.0"]

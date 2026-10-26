FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.8 /uv /bin/

# install directory
WORKDIR /app

# install app
COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY app ./app

# final configuration
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

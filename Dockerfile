# Etapa 1: constrói o front. Desta etapa só o dist/ segue adiante.
FROM node:24-slim AS front
WORKDIR /front
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Etapa 2: a imagem que roda.
FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.8 /uv /bin/

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --no-dev

COPY backend/app ./app
COPY backend/migrations ./migrations
COPY backend/alembic.ini ./
COPY --from=front /front/dist ./dist
ENV PASTA_DO_FRONT=/app/dist
ENV PATH="/app/.venv/bin:$PATH"
# O psycopg-binary traz OpenSSL próprio, que não acha as raízes do Debian sozinho:
# sem esta linha, o sslrootcert=system da DATABASE_URL dá "certificate verify failed".
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && python -m app.comandos.semear_demonstracao && exec uvicorn app.main:app --host 0.0.0.0 --port 8000" ]

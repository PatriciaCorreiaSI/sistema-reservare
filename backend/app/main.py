from fastapi import FastAPI

from app.routers import health, recurso

app = FastAPI()
app.include_router(health.router)
app.include_router(recurso.router)

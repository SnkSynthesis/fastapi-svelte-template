from typing import Any
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from . import api_v1
from .auth.api import router as auth_router

app = FastAPI(
    title="{{cookiecutter.project_name}}", version="{{cookiecutter.project_version}}"
)

app.include_router(api_v1.router, prefix="/api/v1")
app.include_router(auth_router)

templates = Jinja2Templates(directory="frontend/public")
app.mount("/static", StaticFiles(directory="frontend/public"))


@app.get("/")
async def root(request: Request) -> Any:
    return templates.TemplateResponse("index.html", {"request": request})

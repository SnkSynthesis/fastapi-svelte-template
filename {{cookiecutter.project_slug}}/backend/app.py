from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from . import api_v1

app = FastAPI(
    title="{{cookiecutter.project_name}}", version="{{cookiecutter.project_version}}"
)

app.include_router(api_v1.router, prefix="/api/v1")

templates = Jinja2Templates(directory="frontend/public")
app.mount("/static", StaticFiles(directory="frontend/public"))


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

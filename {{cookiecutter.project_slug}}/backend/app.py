from fastapi import FastAPI

from . import api_v1


app = FastAPI(
    title="{{cookiecutter.project_name}}", version="{{cookiecutter.project_version}}"
)
app.include_router(api_v1.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"title": "{{cookiecutter.project_name}}", "version": app.version}

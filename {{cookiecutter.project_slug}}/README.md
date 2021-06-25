# {{cookiecutter.project_name}}

## Run Project

* With reload: `uvicorn --app-dir '.\{{cookiecutter.project_slug}}\' backend.app:app --reload`
* Without reload: `uvicorn --app-dir '.\{{cookiecutter.project_slug}}\' backend.app:app`
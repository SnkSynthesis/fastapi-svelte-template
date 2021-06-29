# {{cookiecutter.project_name}}

## Install dependencies

**NOTE**: *This creates a virtualenv folder (`.venv/`) inside of the root folder of the project*

* With development dependencies: `poetry install`
* Without development dependencies `poetry install --no-dev`

## Run Project

* With reload: `poetry run uvicorn backend.app:app --reload`
* Without reload: `uvicorn backend.app:app`

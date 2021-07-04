# {{cookiecutter.project_name}}

## Install Dependencies
**NOTE**: *This creates a [virtualenv](https://virtualenv.pypa.io/en/latest/) folder (`.venv/`) inside of the root folder of the project*

* With development dependencies: `poetry install`
* Without development dependencies `poetry install --no-dev`

## Linting, Formatting, and Testing

### Linting
Run `poetry run mypy backend`

### Formatting
Run `poetry run black backend`

### Testing
Run `poetry run pytest`


## Run the Project
* With reload: `poetry run uvicorn backend.main:app --reload`
* Without reload: `uvicorn backend.main:app`

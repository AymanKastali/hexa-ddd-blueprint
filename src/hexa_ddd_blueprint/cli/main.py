"""Typer CLI entry point for hexa-ddd-blueprint."""

import keyword
import re
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from hexa_ddd_blueprint import __version__
from hexa_ddd_blueprint.defaults import (
    DEFAULT_AUTHOR,
    DEFAULT_DB,
    DEFAULT_DESCRIPTION,
    DEFAULT_PROJECT_NAME,
    DEFAULT_PYTHON_VERSION,
)
from hexa_ddd_blueprint.generators.project import generate_project
from hexa_ddd_blueprint.logging import logger
from hexa_ddd_blueprint.prompts.interactive import prompt_for_config

app = typer.Typer(
    name="hexa-ddd-blueprint",
    help="Scaffold opinionated Python projects following DDD + Hexagonal Architecture.",
    no_args_is_help=True,
)


class DbChoice(StrEnum):
    postgres = "postgres"
    none = "none"


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"hexa-ddd-blueprint {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """hexa-ddd-blueprint — scaffold DDD + Hexagonal Architecture Python projects."""


@app.command()
def new(
    name: Annotated[str | None, typer.Argument(help="Project name")] = None,
    description: Annotated[
        str | None, typer.Option("--description", "-d", help="Project description")
    ] = None,
    author: Annotated[
        str | None, typer.Option("--author", "-a", help="Author name")
    ] = None,
    db: Annotated[
        DbChoice | None, typer.Option("--db", help="Database: postgres, none")
    ] = None,
    python: Annotated[
        str, typer.Option("--python", help="Python version")
    ] = DEFAULT_PYTHON_VERSION,
    docker: Annotated[
        bool | None,
        typer.Option("--docker/--no-docker", help="Include Docker/Compose generation"),
    ] = None,
    ci: Annotated[
        bool | None, typer.Option("--ci/--no-ci", help="Include GitHub Actions CI")
    ] = None,
    devcontainer: Annotated[
        bool | None,
        typer.Option(
            "--devcontainer/--no-devcontainer", help="Include devcontainer setup"
        ),
    ] = None,
    no_interactive: Annotated[
        bool,
        typer.Option("--no-interactive", "-y", help="Use defaults, skip all prompts"),
    ] = False,
) -> None:
    """Create a new DDD + Hexagonal Architecture Python project."""
    config = {
        "name": name,
        "description": description,
        "author": author,
        "db": db.value if db else None,
        "python": python,
        "docker": docker,
        "ci": ci,
        "devcontainer": devcontainer,
    }

    # Handle "." — scaffold into the current directory
    if config["name"] == ".":
        cwd = Path.cwd()
        config["name"] = re.sub(r"[^a-zA-Z0-9_]", "_", cwd.name)
        config["_use_cwd"] = True
    else:
        config["_use_cwd"] = False

    if no_interactive:
        # Fill in defaults for any missing values
        config["name"] = config["name"] or DEFAULT_PROJECT_NAME
        config["description"] = config["description"] or DEFAULT_DESCRIPTION
        config["author"] = config["author"] or DEFAULT_AUTHOR
        config["db"] = config["db"] or DEFAULT_DB
        if config["docker"] is None:
            config["docker"] = True
        if config["ci"] is None:
            config["ci"] = True
        if config["devcontainer"] is None:
            config["devcontainer"] = True
    else:
        # Prompt for any missing values
        config = prompt_for_config(config)

    _validate_project_name(config["name"])
    logger.info(f"Creating project: {config['name']}")
    try:
        generate_project(config)
    except FileExistsError as e:
        logger.error(str(e))
        raise typer.Exit(code=1) from e
    logger.info(f"Project '{config['name']}' created successfully!")


def _validate_project_name(name: str) -> None:
    """Validate that the project name is a valid Python identifier."""
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
        logger.error(
            f"Invalid project name '{name}'. Only letters, digits, and underscores "
            "are allowed (cannot start with a digit). "
            f"Hint: try '{re.sub(r'[^a-zA-Z0-9_]', '_', name)}' instead."
        )
        raise typer.Exit(code=1)
    if keyword.iskeyword(name):
        logger.error(f"Invalid project name '{name}'. Python keywords are not allowed.")
        raise typer.Exit(code=1)

"""Rich-based interactive prompts for project configuration."""

from typing import Any

from rich.console import Console
from rich.prompt import Confirm, Prompt

from blueprint.defaults import (
    DB_CHOICES,
    DEFAULT_AUTHOR,
    DEFAULT_DB,
    DEFAULT_DESCRIPTION,
    DEFAULT_PROJECT_NAME,
    DEFAULT_PYTHON_VERSION,
)

console = Console()


def prompt_for_config(config: dict[str, Any]) -> dict[str, Any]:
    """Prompt for any missing configuration values using Rich prompts.

    Only prompts for values not already provided via CLI flags.
    """
    console.print("\n[bold blue]Blueprint[/bold blue] — Project Setup\n")

    if not config.get("name"):
        config["name"] = Prompt.ask(
            "[bold]Project name[/bold]",
            default=DEFAULT_PROJECT_NAME,
        )

    if not config.get("description"):
        config["description"] = Prompt.ask(
            "[bold]Project description[/bold]",
            default=DEFAULT_DESCRIPTION,
        )

    if not config.get("author"):
        config["author"] = Prompt.ask(
            "[bold]Author name[/bold]",
            default=DEFAULT_AUTHOR,
        )

    if not config.get("db"):
        config["db"] = Prompt.ask(
            "[bold]Database[/bold]",
            choices=DB_CHOICES,
            default=DEFAULT_DB,
        )

    if not config.get("python"):
        config["python"] = Prompt.ask(
            "[bold]Python version[/bold]",
            default=DEFAULT_PYTHON_VERSION,
        )

    if config.get("docker") is None:
        config["docker"] = Confirm.ask("[bold]Include Docker/Compose?[/bold]", default=True)

    if config.get("ci") is None:
        config["ci"] = Confirm.ask("[bold]Include GitHub Actions CI?[/bold]", default=True)

    if config.get("devcontainer") is None:
        config["devcontainer"] = Confirm.ask(
            "[bold]Include devcontainer setup?[/bold]", default=True
        )

    return config

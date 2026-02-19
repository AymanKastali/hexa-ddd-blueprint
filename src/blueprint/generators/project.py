"""Project generator — orchestrates DDD + Hexagonal Architecture project scaffolding."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

from blueprint.logging import logger

TEMPLATE_ENV = Environment(
    loader=PackageLoader("blueprint", "templates"),
    autoescape=select_autoescape(),
    keep_trailing_newline=True,
)


def _render(template_path: str, context: dict[str, Any]) -> str:
    """Render a Jinja2 template with the given context."""
    template = TEMPLATE_ENV.get_template(template_path)
    return template.render(**context)


def _write_file(path: Path, content: str) -> None:
    """Write content to a file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    logger.debug(f"  Created {path}")


def _write_init(path: Path) -> None:
    """Write an empty __init__.py file."""
    _write_file(path / "__init__.py", "")


def generate_project(config: dict[str, Any]) -> None:
    """Generate a complete DDD + Hexagonal Architecture project.

    Args:
        config: Project configuration dict with keys:
            name, description, author, db, python, docker, ci, devcontainer
    """
    name = config["name"]
    root = Path.cwd() / name

    if root.exists():
        raise FileExistsError(
            f"Directory '{name}' already exists. Remove it or choose a different name."
        )

    src = root / "src" / name

    context = {
        "project_name": name,
        "description": config["description"],
        "author": config["author"],
        "db": config["db"],
        "python_version": config["python"],
        "docker": config["docker"],
        "ci": config["ci"],
        "devcontainer": config["devcontainer"],
    }

    _generate_source_tree(src, context)
    _generate_tests(root, context)
    _generate_docs(root, context)
    _generate_root_files(root, context)

    if config["docker"]:
        _generate_docker(root, context)

    if config["ci"]:
        _generate_ci(root, context)

    if config["devcontainer"]:
        _generate_devcontainer(root, context)


def _generate_source_tree(src: Path, context: dict[str, Any]) -> None:
    """Generate the src/<project>/ directory tree."""
    # Top-level package init
    _write_file(src / "__init__.py", _render("base/init.py.j2", context))
    _write_file(src / "__main__.py", _render("base/__main__.py.j2", context))

    # Domain layer
    _write_init(src / "domain")
    _write_init(src / "domain" / "models")
    _write_init(src / "domain" / "services")
    _write_init(src / "domain" / "events")
    _write_file(
        src / "domain" / "events" / "base.py",
        _render("base/domain_event.py.j2", context),
    )
    _write_file(
        src / "domain" / "events" / "events.py",
        _render("base/events.py.j2", context),
    )
    _write_file(
        src / "domain" / "exceptions" / "__init__.py",
        _render("base/exceptions/__init__.py.j2", context),
    )
    _write_file(
        src / "domain" / "exceptions" / "base.py",
        _render("base/exceptions/base.py.j2", context),
    )
    _write_file(
        src / "domain" / "exceptions" / "validation.py",
        _render("base/exceptions/validation.py.j2", context),
    )

    # Application layer
    _write_init(src / "application")
    _write_init(src / "application" / "ports")
    _write_init(src / "application" / "ports" / "inbound")
    _write_init(src / "application" / "ports" / "outbound")
    if context["db"] != "none":
        _write_file(
            src / "application" / "ports" / "outbound" / "database.py",
            _render("base/database_port.py.j2", context),
        )
    _write_init(src / "application" / "services")
    _write_init(src / "application" / "dto")

    # Adapters layer — inbound
    _write_init(src / "adapters")
    _write_init(src / "adapters" / "inbound")
    _write_init(src / "adapters" / "inbound" / "api")
    _write_init(src / "adapters" / "inbound" / "api" / "rest")
    _write_file(
        src / "adapters" / "inbound" / "api" / "rest" / "app.py",
        _render("base/app.py.j2", context),
    )
    _write_file(
        src / "adapters" / "inbound" / "api" / "rest" / "dependencies.py",
        _render("base/dependencies.py.j2", context),
    )
    _write_init(src / "adapters" / "inbound" / "api" / "rest" / "routes")

    # Adapters layer — outbound
    _write_init(src / "adapters" / "outbound")

    # DB adapter (conditional)
    if context["db"] != "none":
        _generate_db_adapter(src, context)

    # Config (inside adapters layer)
    _write_init(src / "adapters" / "config")
    _write_file(
        src / "adapters" / "config" / "settings.py",
        _render("base/settings.py.j2", context),
    )

    # Shared kernel (inside domain layer)
    _write_init(src / "domain" / "shared")
    _write_file(
        src / "domain" / "shared" / "building_blocks.py",
        _render("base/building_blocks.py.j2", context),
    )


def _generate_db_adapter(src: Path, context: dict[str, Any]) -> None:
    """Generate the persistence adapter for the selected database."""
    db = context["db"]
    persistence = src / "adapters" / "outbound" / "persistence"
    _write_init(persistence)

    db_dir = persistence / db
    _write_init(db_dir)

    template_dir = f"db/{db}"

    _write_file(
        db_dir / "database.py",
        _render(f"{template_dir}/database.py.j2", context),
    )
    _write_file(
        db_dir / "models.py",
        _render(f"{template_dir}/models.py.j2", context),
    )
    _write_file(
        db_dir / "repositories.py",
        _render(f"{template_dir}/repositories.py.j2", context),
    )
    _write_file(
        db_dir / "config.py",
        _render(f"{template_dir}/config.py.j2", context),
    )


def _generate_tests(root: Path, context: dict[str, Any]) -> None:
    """Generate the test directory structure."""
    tests = root / "tests"

    _write_file(tests / "conftest.py", _render("base/conftest.py.j2", context))
    _write_init(tests / "unit" / "domain")
    _write_init(tests / "unit" / "application")
    _write_init(tests / "integration" / "adapters")


def _generate_docs(root: Path, context: dict[str, Any]) -> None:
    """Generate documentation files including PlantUML architecture diagram."""
    docs = root / "docs" / "architecture"
    _write_file(
        docs / "hexagonal.puml",
        _render("docs/hexagonal.puml.j2", context),
    )


def _generate_root_files(root: Path, context: dict[str, Any]) -> None:
    """Generate root-level project files."""
    _write_file(root / "pyproject.toml", _render("base/pyproject.toml.j2", context))
    _write_file(root / "README.md", _render("base/README.md.j2", context))
    _write_file(root / ".gitignore", _render("base/gitignore.j2", context))
    _write_file(
        root / ".pre-commit-config.yaml",
        _render("base/pre-commit-config.yaml.j2", context),
    )
    _write_file(root / ".env", _render("base/env.j2", context))
    _write_file(root / ".env.dev", _render("base/env.dev.j2", context))


def _generate_docker(root: Path, context: dict[str, Any]) -> None:
    """Generate Docker and Docker Compose files."""
    docker = root / "docker"
    _write_file(docker / "Dockerfile", _render("docker/Dockerfile.j2", context))
    _write_file(
        docker / "docker-compose.yml",
        _render("docker/docker-compose.yml.j2", context),
    )
    _write_file(root / ".dockerignore", _render("docker/dockerignore.j2", context))


def _generate_ci(root: Path, context: dict[str, Any]) -> None:
    """Generate GitHub Actions CI workflow."""
    ci = root / ".github" / "workflows"
    _write_file(ci / "ci.yml", _render("ci/ci.yml.j2", context))


def _generate_devcontainer(root: Path, context: dict[str, Any]) -> None:
    """Generate devcontainer configuration."""
    devcontainer = root / ".devcontainer"
    _write_file(
        devcontainer / "devcontainer.json",
        _render("devcontainer/devcontainer.json.j2", context),
    )
    if context["db"] != "none":
        _write_file(
            devcontainer / "docker-compose.yml",
            _render("devcontainer/docker-compose.yml.j2", context),
        )
    _write_file(
        root / ".vscode" / "launch.json",
        _render("devcontainer/launch.json.j2", context),
    )

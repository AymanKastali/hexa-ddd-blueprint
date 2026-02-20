"""Tests for the project generator."""

import pytest

from hexa_ddd_blueprint.generators.project import generate_project

BASE_CONFIG = {
    "name": "testgen",
    "description": "A test project",
    "author": "Tester",
    "db": "none",
    "python": "3.12",
    "docker": True,
    "ci": True,
    "devcontainer": True,
}


@pytest.fixture
def project_dir(tmp_path, monkeypatch):
    """Generate a project and return its root path."""
    monkeypatch.chdir(tmp_path)
    generate_project(BASE_CONFIG)
    return tmp_path / "testgen"


def test_core_structure(project_dir):
    """Verify the DDD + Hexagonal directory structure."""
    src = project_dir / "src" / "testgen"

    # Domain layer
    assert (src / "domain" / "__init__.py").exists()
    assert (src / "domain" / "models" / "__init__.py").exists()
    assert (src / "domain" / "services" / "__init__.py").exists()
    assert (src / "domain" / "events" / "__init__.py").exists()
    assert (src / "domain" / "events" / "base.py").exists()
    assert (src / "domain" / "events" / "events.py").exists()
    assert (src / "domain" / "exceptions" / "__init__.py").exists()
    assert (src / "domain" / "exceptions" / "base.py").exists()
    assert (src / "domain" / "exceptions" / "validation.py").exists()

    # Application layer
    assert (src / "application" / "__init__.py").exists()
    assert (src / "application" / "ports" / "inbound" / "__init__.py").exists()
    assert (src / "application" / "ports" / "outbound" / "__init__.py").exists()
    assert (src / "application" / "use_cases" / "__init__.py").exists()
    assert (src / "application" / "dto" / "__init__.py").exists()

    # Adapters layer
    assert (src / "adapters" / "inbound" / "api" / "rest" / "app.py").exists()
    assert (src / "adapters" / "inbound" / "api" / "rest" / "dependencies.py").exists()
    assert (
        src / "adapters" / "inbound" / "api" / "rest" / "routes" / "__init__.py"
    ).exists()
    assert (src / "adapters" / "outbound" / "__init__.py").exists()

    # Package entry point and logging (hexagonal)
    assert (src / "__main__.py").exists()
    assert (src / "application" / "ports" / "outbound" / "logger.py").exists()
    assert (src / "adapters" / "outbound" / "logging" / "logger.py").exists()

    # Config (inside adapters) & shared kernel (inside domain)
    assert (src / "adapters" / "config" / "settings.py").exists()
    assert (src / "domain" / "shared" / "building_blocks.py").exists()


def test_domain_building_blocks(project_dir):
    """Verify domain building blocks contain the expected classes."""
    src = project_dir / "src" / "testgen"

    # base_entity.py has Id, Entity, AggregateRoot — not old BaseEntity
    base_entity = (src / "domain" / "shared" / "building_blocks.py").read_text()
    assert "class Id[T]:" in base_entity
    assert "class Entity[IdT]:" in base_entity
    assert "class AggregateRoot[IdT]" in base_entity
    assert "BaseEntity" not in base_entity

    # events/base.py has DomainEvent
    domain_event = (src / "domain" / "events" / "base.py").read_text()
    assert "class DomainEvent:" in domain_event

    # exceptions package has DomainError, ValidationError, RequiredFieldError
    validation = (src / "domain" / "exceptions" / "validation.py").read_text()
    assert "class RequiredFieldError" in validation
    assert "class ValidationError" in validation
    base_exc = (src / "domain" / "exceptions" / "base.py").read_text()
    assert "class DomainError" in base_exc


def test_root_files(project_dir):
    """Verify root-level files are generated."""
    assert (project_dir / "pyproject.toml").exists()
    assert (project_dir / "README.md").exists()
    assert (project_dir / ".gitignore").exists()
    assert (project_dir / ".pre-commit-config.yaml").exists()
    assert (project_dir / ".env").exists()
    assert (project_dir / ".env.dev").exists()


def test_tests_structure(project_dir):
    """Verify test directory structure."""
    tests = project_dir / "tests"
    assert (tests / "conftest.py").exists()
    assert (tests / "unit" / "domain" / "__init__.py").exists()
    assert (tests / "unit" / "application" / "__init__.py").exists()
    assert (tests / "integration" / "adapters" / "__init__.py").exists()


def test_docs_always_generated(project_dir):
    """Verify PlantUML architecture diagram is always generated."""
    puml = project_dir / "docs" / "architecture" / "hexagonal.puml"
    assert puml.exists()
    content = puml.read_text()
    assert "@startuml" in content
    assert "testgen" in content
    assert "@enduml" in content


def test_docker_generated(project_dir):
    """Verify Docker files are generated when enabled."""
    assert (project_dir / "docker" / "Dockerfile").exists()
    assert (project_dir / "docker" / "docker-compose.yml").exists()
    assert (project_dir / ".dockerignore").exists()


def test_ci_generated(project_dir):
    """Verify CI files are generated when enabled."""
    assert (project_dir / ".github" / "workflows" / "ci.yml").exists()


def test_devcontainer_generated(project_dir):
    """Verify devcontainer config is generated when enabled (standalone, db=none)."""
    assert (project_dir / ".devcontainer" / "devcontainer.json").exists()
    assert not (project_dir / ".devcontainer" / "docker-compose.yml").exists()
    assert not (project_dir / ".devcontainer" / ".env").exists()
    assert (project_dir / ".vscode" / "launch.json").exists()
    launch = (project_dir / ".vscode" / "launch.json").read_text()
    assert "Debug FastAPI" in launch
    assert "--reload" not in launch
    assert '"launch"' in launch


def test_no_docker(tmp_path, monkeypatch):
    """Verify Docker files are skipped when disabled."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "nodocker", "docker": False}
    generate_project(config)
    assert not (tmp_path / "nodocker" / "docker").exists()
    assert not (tmp_path / "nodocker" / ".dockerignore").exists()


def test_no_ci(tmp_path, monkeypatch):
    """Verify CI files are skipped when disabled."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "noci", "ci": False}
    generate_project(config)
    assert not (tmp_path / "noci" / ".github").exists()


def test_no_devcontainer(tmp_path, monkeypatch):
    """Verify devcontainer files are skipped when disabled."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "nodev", "devcontainer": False}
    generate_project(config)
    assert not (tmp_path / "nodev" / ".devcontainer").exists()
    assert not (tmp_path / "nodev" / ".devcontainer" / "docker-compose.yml").exists()
    assert not (tmp_path / "nodev" / ".vscode" / "launch.json").exists()


def test_postgres_db(tmp_path, monkeypatch):
    """Verify postgres persistence adapter is generated."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "sqlproj", "db": "postgres"}
    generate_project(config)
    src = tmp_path / "sqlproj" / "src" / "sqlproj"
    persistence = src / "adapters" / "outbound" / "persistence" / "postgres"
    assert (persistence / "database.py").exists()
    assert (persistence / "models.py").exists()
    assert (persistence / "repositories.py").exists()
    assert (persistence / "config.py").exists()
    # DatabasePort interface in application layer
    db_port = src / "application" / "ports" / "outbound" / "database.py"
    assert db_port.exists()
    assert "DatabasePort" in db_port.read_text()


def test_no_db_no_persistence(project_dir):
    """Verify no persistence adapter when db=none."""
    persistence = (
        project_dir / "src" / "testgen" / "adapters" / "outbound" / "persistence"
    )
    assert not persistence.exists()


def test_pyproject_contains_db_deps(tmp_path, monkeypatch):
    """Verify generated pyproject.toml includes DB dependencies."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "sqldeps", "db": "postgres"}
    generate_project(config)
    pyproject = (tmp_path / "sqldeps" / "pyproject.toml").read_text()
    assert "sqlalchemy" in pyproject
    assert "alembic" in pyproject


def test_pyproject_no_db_deps(project_dir):
    """Verify generated pyproject.toml excludes DB deps when db=none."""
    pyproject = (project_dir / "pyproject.toml").read_text()
    assert "sqlalchemy" not in pyproject


def test_settings_includes_db_config(tmp_path, monkeypatch):
    """Verify settings template includes DB-specific config."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "sqlsettings", "db": "postgres"}
    generate_project(config)
    settings_path = (
        tmp_path
        / "sqlsettings"
        / "src"
        / "sqlsettings"
        / "adapters"
        / "config"
        / "settings.py"
    )
    settings = settings_path.read_text()
    assert "database_url" in settings


def test_docker_compose_includes_db_service(tmp_path, monkeypatch):
    """Verify docker-compose includes DB service for postgres."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "sqldocker", "db": "postgres"}
    generate_project(config)
    compose = (tmp_path / "sqldocker" / "docker" / "docker-compose.yml").read_text()
    assert "postgres" in compose


def test_devcontainer_with_postgres(tmp_path, monkeypatch):
    """Verify devcontainer uses docker-compose mode with postgres."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "pgdev", "db": "postgres", "devcontainer": True}
    generate_project(config)
    root = tmp_path / "pgdev"

    # docker-compose.yml exists and contains postgres
    compose_path = root / ".devcontainer" / "docker-compose.yml"
    assert compose_path.exists()
    compose = compose_path.read_text()
    assert "postgres" in compose

    # devcontainer.json uses compose mode, not standalone image
    devcontainer = (root / ".devcontainer" / "devcontainer.json").read_text()
    assert "dockerComposeFile" in devcontainer
    assert '"image"' not in devcontainer

    # forwardPorts includes 5432
    assert "5432" in devcontainer

    # .env.dev exists at root and contains service-name URL
    env_dev_path = root / ".env.dev"
    assert env_dev_path.exists()
    env_dev_content = env_dev_path.read_text()
    assert "db:5432" in env_dev_content
    assert not (root / ".devcontainer" / ".env").exists()


def test_root_env_postgres(tmp_path, monkeypatch):
    """Verify root .env contains localhost DB URL for postgres."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "pgenv", "db": "postgres"}
    generate_project(config)
    env_content = (tmp_path / "pgenv" / ".env").read_text()
    assert "localhost:5432" in env_content


def test_root_env_no_db(project_dir):
    """Verify root .env exists but has no DATABASE_URL when db=none."""
    env_path = project_dir / ".env"
    assert env_path.exists()
    env_content = env_path.read_text()
    assert "DATABASE_URL" not in env_content


def test_no_repository_port(tmp_path, monkeypatch):
    """Verify RepositoryPort is not generated (replaced by DatabasePort)."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "norepo", "db": "postgres"}
    generate_project(config)
    src = tmp_path / "norepo" / "src" / "norepo"
    assert not (src / "application" / "ports" / "outbound" / "repository.py").exists()
    repos_path = (
        src / "adapters" / "outbound" / "persistence" / "postgres" / "repositories.py"
    )
    repos = repos_path.read_text()
    assert "RepositoryPort" not in repos


def test_no_db_no_database_port(project_dir):
    """Verify no DatabasePort when db=none."""
    src = project_dir / "src" / "testgen"
    assert not (src / "application" / "ports" / "outbound" / "database.py").exists()


def test_settings_includes_pool_config(tmp_path, monkeypatch):
    """Verify settings includes connection pool settings."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "poolproj", "db": "postgres"}
    generate_project(config)
    settings_path = (
        tmp_path
        / "poolproj"
        / "src"
        / "poolproj"
        / "adapters"
        / "config"
        / "settings.py"
    )
    content = settings_path.read_text()
    assert "db_pool_size" in content
    assert "db_pool_timeout" in content
    assert "db_command_timeout" in content


def test_app_lifespan_uses_database(tmp_path, monkeypatch):
    """Verify app.py uses database.connect()/disconnect() in lifespan."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "lifeproj", "db": "postgres"}
    generate_project(config)
    app_content = (
        tmp_path
        / "lifeproj"
        / "src"
        / "lifeproj"
        / "adapters"
        / "inbound"
        / "api"
        / "rest"
        / "app.py"
    ).read_text()
    assert "database.connect()" in app_content
    assert "database.disconnect()" in app_content
    assert "engine.dispose()" not in app_content


def test_app_lifespan_no_db(project_dir):
    """Verify app.py has no database lifecycle calls when db=none."""
    app_content = (
        project_dir
        / "src"
        / "testgen"
        / "adapters"
        / "inbound"
        / "api"
        / "rest"
        / "app.py"
    ).read_text()
    assert "database.connect()" not in app_content
    assert "database.disconnect()" not in app_content


def test_logging_adapter_uses_rich(project_dir):
    """Verify logging adapter uses Rich and settings-based configuration."""
    content = (
        project_dir
        / "src"
        / "testgen"
        / "adapters"
        / "outbound"
        / "logging"
        / "logger.py"
    ).read_text()
    assert "RichHandler" in content
    assert "settings.debug" in content
    assert "setup_logging" in content


def test_logger_port_exists(project_dir):
    """Verify LoggerPort protocol is generated in ports layer."""
    content = (
        project_dir
        / "src"
        / "testgen"
        / "application"
        / "ports"
        / "outbound"
        / "logger.py"
    ).read_text()
    assert "LoggerPort" in content
    assert "Protocol" in content


def test_pyproject_has_rich_not_loggerizer(project_dir):
    """Verify generated pyproject.toml includes rich but not loggerizer."""
    pyproject = (project_dir / "pyproject.toml").read_text()
    assert "rich" in pyproject
    assert "loggerizer" not in pyproject


def test_generate_use_cwd(tmp_path, monkeypatch):
    """Verify generate_project scaffolds into cwd when _use_cwd is True."""
    monkeypatch.chdir(tmp_path)
    config = {**BASE_CONFIG, "name": "testgen", "_use_cwd": True}
    generate_project(config)
    # Files should be in tmp_path directly, not in a subdirectory
    assert (tmp_path / "src" / "testgen" / "__init__.py").exists()
    assert (tmp_path / "pyproject.toml").exists()
    assert not (tmp_path / "testgen").exists()


def test_generate_use_cwd_non_empty(tmp_path, monkeypatch):
    """Verify generate_project raises FileExistsError for non-empty cwd."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "existing.txt").write_text("content")
    config = {**BASE_CONFIG, "name": "testgen", "_use_cwd": True}
    with pytest.raises(FileExistsError, match="not empty"):
        generate_project(config)

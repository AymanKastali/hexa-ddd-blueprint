"""Tests for the blueprint CLI."""

from typer.testing import CliRunner

from blueprint import __version__
from blueprint.cli.main import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Scaffold" in result.output


def test_new_help(monkeypatch):
    monkeypatch.setenv("COLUMNS", "200")
    result = runner.invoke(app, ["new", "--help"])
    assert result.exit_code == 0
    assert "--description" in result.output
    assert "--author" in result.output
    assert "--db" in result.output
    assert "--python" in result.output
    assert "--no-docker" in result.output
    assert "--no-ci" in result.output
    assert "--no-devcontainer" in result.output
    assert "--no-interactive" in result.output


def test_new_with_all_flags(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, [
        "new", "testcli",
        "--description", "Test project",
        "--author", "Tester",
        "--db", "none",
        "--python", "3.12",
        "--no-docker",
        "--no-ci",
        "--no-devcontainer",
        "-y",
    ])
    assert result.exit_code == 0
    assert (tmp_path / "testcli" / "pyproject.toml").exists()
    assert (tmp_path / "testcli" / "src" / "testcli" / "__init__.py").exists()
    assert not (tmp_path / "testcli" / "docker").exists()
    assert not (tmp_path / "testcli" / ".github").exists()
    assert not (tmp_path / "testcli" / ".devcontainer").exists()


def test_new_non_interactive_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "defaultproj", "-y"])
    assert result.exit_code == 0
    project = tmp_path / "defaultproj"
    assert project.exists()
    # Should have docker, ci, devcontainer by default
    assert (project / "docker" / "Dockerfile").exists()
    assert (project / ".github" / "workflows" / "ci.yml").exists()
    assert (project / ".devcontainer" / "devcontainer.json").exists()


def test_new_invalid_name(tmp_path, monkeypatch):
    """Verify non-identifier name exits non-zero."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "123-bad-name", "-y"])
    assert result.exit_code != 0


def test_new_directory_exists(tmp_path, monkeypatch):
    """Verify existing directory exits non-zero."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "existing").mkdir()
    result = runner.invoke(app, ["new", "existing", "-y"])
    assert result.exit_code != 0

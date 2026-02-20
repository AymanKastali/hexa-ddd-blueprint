"""Tests for the hexa-ddd-blueprint CLI."""

import re

from typer.testing import CliRunner

from hexa_ddd_blueprint import __version__
from hexa_ddd_blueprint.cli.main import app

runner = CliRunner()

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


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
    output = _strip_ansi(result.output)
    assert "--description" in output
    assert "--author" in output
    assert "--db" in output
    assert "--python" in output
    assert "--no-docker" in output
    assert "--no-ci" in output
    assert "--no-devcontainer" in output
    assert "--no-interactive" in output


def test_new_with_all_flags(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app,
        [
            "new",
            "testcli",
            "--description",
            "Test project",
            "--author",
            "Tester",
            "--db",
            "none",
            "--python",
            "3.12",
            "--no-docker",
            "--no-ci",
            "--no-devcontainer",
            "-y",
        ],
    )
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


def test_new_keyword_name(tmp_path, monkeypatch):
    """Verify Python keyword as project name exits non-zero."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "class", "-y"])
    assert result.exit_code != 0


def test_new_directory_exists(tmp_path, monkeypatch):
    """Verify existing directory exits non-zero."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "existing").mkdir()
    result = runner.invoke(app, ["new", "existing", "-y"])
    assert result.exit_code != 0


def test_new_dot_scaffolds_in_cwd(tmp_path, monkeypatch):
    """Verify 'new .' scaffolds into the current directory."""
    project_dir = tmp_path / "my_cool_app"
    project_dir.mkdir()
    monkeypatch.chdir(project_dir)
    result = runner.invoke(
        app,
        [
            "new",
            ".",
            "--db",
            "none",
            "-d",
            "Test",
            "-a",
            "Dev",
            "--no-docker",
            "--no-ci",
            "--no-devcontainer",
            "-y",
        ],
    )
    assert result.exit_code == 0
    assert (project_dir / "src" / "my_cool_app" / "__init__.py").exists()
    assert (project_dir / "pyproject.toml").exists()
    # No subdirectory should be created
    assert not (project_dir / "my_cool_app").exists()


def test_new_dot_derives_name_from_hyphenated_dir(tmp_path, monkeypatch):
    """Verify hyphens in directory name are converted to underscores."""
    project_dir = tmp_path / "my-cool-app"
    project_dir.mkdir()
    monkeypatch.chdir(project_dir)
    result = runner.invoke(
        app,
        [
            "new",
            ".",
            "--db",
            "none",
            "-d",
            "Test",
            "-a",
            "Dev",
            "--no-docker",
            "--no-ci",
            "--no-devcontainer",
            "-y",
        ],
    )
    assert result.exit_code == 0
    assert (project_dir / "src" / "my_cool_app" / "__init__.py").exists()


def test_new_dot_non_empty_directory(tmp_path, monkeypatch):
    """Verify 'new .' in a non-empty directory exits non-zero."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "existing_file.txt").write_text("content")
    result = runner.invoke(app, ["new", ".", "-y"])
    assert result.exit_code != 0

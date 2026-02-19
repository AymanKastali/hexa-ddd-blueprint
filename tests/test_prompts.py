"""Tests for the interactive prompts module."""

from blueprint.prompts.interactive import prompt_for_config


def test_prompt_skips_provided_values(monkeypatch):
    """Verify prompts are skipped for values already provided."""
    # Simulate input for missing values (won't be reached since all provided)
    config = {
        "name": "existing",
        "description": "Already set",
        "author": "Already Author",
        "db": "none",
        "python": "3.12",
        "docker": True,
        "ci": True,
        "devcontainer": True,
    }
    result = prompt_for_config(config)
    assert result["name"] == "existing"
    assert result["description"] == "Already set"
    assert result["author"] == "Already Author"
    assert result["db"] == "none"
    assert result["python"] == "3.12"
    assert result["docker"] is True
    assert result["ci"] is True
    assert result["devcontainer"] is True


def test_prompt_fills_missing_name(monkeypatch):
    """Verify prompt asks for missing name."""
    inputs = iter(["prompted_name", "A description", "Author Name", "postgres"])
    monkeypatch.setattr("rich.prompt.Prompt.ask", lambda *a, **kw: next(inputs))
    monkeypatch.setattr("rich.prompt.Confirm.ask", lambda *a, **kw: True)

    config = {
        "name": None,
        "description": None,
        "author": None,
        "db": None,
        "python": "3.12",
    }
    result = prompt_for_config(config)
    assert result["name"] == "prompted_name"
    assert result["description"] == "A description"
    assert result["author"] == "Author Name"
    assert result["db"] == "postgres"
    assert result["docker"] is True
    assert result["ci"] is True
    assert result["devcontainer"] is True

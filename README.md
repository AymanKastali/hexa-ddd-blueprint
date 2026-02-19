# Blueprint

CLI tool that scaffolds opinionated Python projects following **DDD + Hexagonal (Ports & Adapters) Architecture**.

## Installation

```bash
uv tool install blueprint
```

## Usage

### Interactive mode (default)

```bash
blueprint new
```

Launches prompts for project name, description, author, DB choice, and Python version.

### Flag-driven mode

```bash
blueprint new myproject \
  --description "My awesome service" \
  --author "John Doe" \
  --db postgres \
  --python 3.12 \
  --no-docker \
  --no-ci
```

### All flags

| Flag | Default | Description |
|---|---|---|
| `[NAME]` | (prompted) | Project name |
| `--description` / `-d` | (prompted) | Project description |
| `--author` / `-a` | (prompted) | Author name |
| `--db` | (prompted) | Database: `postgres`, `none` |
| `--python` | `3.12` | Python version |
| `--no-docker` | false | Skip Docker/Compose |
| `--no-ci` | false | Skip GitHub Actions CI |
| `--no-devcontainer` | false | Skip devcontainer |
| `--no-interactive` / `-y` | false | Use defaults, skip prompts |

## Generated Project Structure

```
myproject/
├── src/myproject/
│   ├── domain/           # Pure business logic
│   │   └── shared/       # Shared kernel (base entity)
│   ├── application/      # Use cases, ports, DTOs
│   └── adapters/
│       ├── config/           # Pydantic Settings
│       ├── inbound/
│       │   └── api/
│       │       └── rest/     # FastAPI REST adapter
│       └── outbound/
│           └── persistence/
│               └── postgres/ # DB-specific adapter
├── tests/
├── docs/architecture/    # PlantUML diagrams
├── docker/
├── .github/workflows/
└── .devcontainer/
```

## Development

```bash
uv sync
uv run pytest
```

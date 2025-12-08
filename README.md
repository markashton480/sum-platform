# Tradesite

Monorepo for trade website platform.

## Getting Started (Tooling)

### Prerequisites

* Python 3.12+
* A working virtual environment

### Installation

1. Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install development dependencies:

```bash
make install-dev
```

This will install the project dependencies and development tools (Black, isort, ruff, pytest, mypy, pre-commit) and set up pre-commit hooks.

### Development Commands

#### Linting

Run linting checks (ruff + mypy):

```bash
make lint
```

#### Testing

Run the test suite:

```bash
make test
```

#### Formatting

Format code with Black and isort:

```bash
make format
```

#### Pre-commit Hooks

Pre-commit hooks are automatically installed when you run `make install-dev`. They will run automatically on git commit. You can also run them manually:

```bash
pre-commit run --all-files
```

### Project Structure

```
.
├── core/           # Core package (sum_core)
├── boilerplate/     # Boilerplate templates
├── clients/         # Client projects
├── cli/             # CLI tools
├── docs/            # Documentation
├── scripts/         # Utility scripts
├── infrastructure/  # Infrastructure as code
└── tests/           # Test suite
```

## License

TBD

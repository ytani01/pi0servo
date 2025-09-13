# Tech Stack

**Programming Language:** Python

**Core Libraries:**
- `pigpio`: For low-level GPIO control and servo pulse generation.

**Package Management & Build System:**
- `uv`: Used for dependency management, command execution, and project configuration.
- `pyproject.toml`: Project configuration file.

**Web Framework (for API):**
- `FastAPI`: Modern, fast (high-performance) web framework for building APIs.
- `Uvicorn`: ASGI server for FastAPI.

**Testing Framework:**
- `pytest`: For writing and running tests.

**Linting & Type Checking Tools:**
- `ruff`: A very fast Python linter and formatter.
- `mypy`: Static type checker for Python.
- `pyright`: Another static type checker for Python (often used with VS Code).

**Other Utilities:**
- `click`: For building command-line interfaces (used in `click_utils.py`).
- Custom logging module (`my_logger.py`).
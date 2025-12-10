# Tech Stack: pi0servo

The `pi0servo` project utilizes the following technologies and libraries:

**Core Language:**
*   Python (>=3.11)

**Key Libraries/Frameworks:**
*   **pigpio:** Low-level GPIO access and servo control on Raspberry Pi.
*   **click:** Python package for creating beautiful command line interfaces.
*   **blessed:** A thin, practical wrapper around curses-like functionality, for Python. Used for interactive CLI elements (e.g., calibration tool).
*   **requests:** HTTP library for making web requests (likely used by API client).
*   **fastapi:** Modern, fast (high-performance) web framework for building APIs.
*   **uvicorn:** ASGI web server, used to run FastAPI applications.
*   **json-rpc:** Library for implementing JSON-RPC communication.

**Build System & Project Management:**
*   **hatchling:** Modern, extensible Python build backend.
*   **hatch-vcs:** Hatch plugin for versioning based on VCS (e.g., Git).
*   **uv:** Fast Python package installer and resolver, used for dependency management and running scripts.

**Development Tools:**
*   **ruff:** Extremely fast Python linter and formatter, used for enforcing code style and catching errors.
*   **mypy:** Static type checker for Python.
*   **pytest:** Popular Python testing framework.
*   **pytest-mock:** Pytest plugin for mocking.
*   **flake8:** Another Python code linter (used in dev dependencies, might be superseded by ruff).
*   **twine:** Utility for publishing Python packages.
*   **ruff-lsp:** Language Server Protocol for Ruff.
*   **jsonschema:** For validating JSON data (used in samples).
*   **types-jsonschema:** Type stubs for `jsonschema`.
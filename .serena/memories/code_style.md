# Code Style and Conventions: pi0servo

The `pi0servo` project adheres to the following code style and conventions, primarily enforced through `ruff` and `mypy` configurations:

**General Guidelines:**
*   **Language:** Python 3.11 or newer.
*   **Line Length:** All lines of code are limited to a maximum of 78 characters. This also applies to docstring code examples.

**Linting and Formatting (Ruff):**
*   **Tool:** `ruff` is used for both linting and formatting.
*   **Selected Rules:** A comprehensive set of linting rules is enabled, including:
    *   `E` (pycodestyle Error)
    *   `F` (Pyflakes)
    *   `I` (isort - import sorting)
    *   `W` (pycodestyle Warning)
    *   `C90` (mccabe complexity)
    *   `B` (flake8-bugbear)
    *   `A` (flake8-builtins)
    *   `UP` (pyupgrade)
    *   `PT` (flake8-pytest-style)
    *   `SIM` (flake8-simplify)
    *   `S` (flake8-bandit - security issues)
*   **Ignored Rules (Global):**
    *   `SIM108`: Ternary operator can be used (often makes code less readable).
    *   `S104`: Hardcoded bind address (security consideration, often necessary for servers).
    *   `C901`: Too complex (mccabe complexity, sometimes complex functions are unavoidable).
    *   `B008`: Do not perform function calls in argument defaults (can lead to unexpected behavior).
*   **Per-File Ignores:**
    *   `conftest.py`: `F401` (unused imports), `F811` (redefinition of unused name).
    *   `tests/*`: `S101` (assert statement used), `S603` (subprocess call with shell=True), `S307` (unsafe yaml load). These are often acceptable in test contexts.
    *   `docs/conf.py`: `A001` (variable name shadows a built-in).
    *   `samples/*`, `src/pi0servo/command/*`: `S108` (hardcoded password string). This indicates that sample code and command definitions might contain placeholder sensitive information that should not be present in production.

**Type Hinting (Mypy):**
*   **Tool:** `mypy` is used for static type checking.
*   **Ignored Missing Imports:** Type checking is less strict for external libraries where type stubs might be missing or incomplete. Specifically, `pigpio`, `fastapi`, `requests`, `jsonrpc`, `click`, and `blessed` are ignored for missing imports.

**Naming Conventions:**
*   (Inferred from general Python practices and ruff rules): snake_case for variables and functions, PascalCase for classes.

**Docstrings:**
*   (Inferred from ruff configuration): Docstring code line length is also limited to 78 characters, suggesting docstrings are used and expected to be well-formatted.

**Testing:**
*   `pytest` is the chosen framework.
*   `pythonpath = "tests"` in `pytest.ini_options` indicates that the `tests` directory is added to the Python path for test discovery.
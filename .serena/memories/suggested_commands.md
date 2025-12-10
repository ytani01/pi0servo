# Suggested Commands for pi0servo Development

This document outlines essential commands for developing, testing, and maintaining the `pi0servo` project. It assumes `uv` is installed and configured as the project environment manager.

## General Project Commands

*   **Activate `uv` Environment:**
    ```bash
    uv shell
    ```
    (This should automatically activate the environment if `uv` is configured correctly for the project directory, or you can run it manually.)

*   **Install/Update Dependencies:**
    ```bash
    uv pip install -e ".[dev,samples]"
    ```
    This command installs the project in editable mode (`-e`) and includes development and samples dependencies.

## Running the Application

*   **Run CLI Subcommands:**
    To execute any `pi0servo` CLI subcommand (e.g., `calib`, `api-server`, `servo`):
    ```bash
    uv run pi0servo <subcommand> [options]
    ```
    **Examples:**
    *   Interactive calibration for GPIO 17:
        ```bash
        uv run pi0servo calib 17
        ```
    *   Start the API server:
        ```bash
        uv run pi0servo api-server
        ```
    *   Get help for a subcommand:
        ```bash
        uv run pi0servo <subcommand> -h
        ```

## Testing

*   **Run All Tests:**
    ```bash
    uv run pytest
    ```

*   **Run Specific Test File:**
    ```bash
    uv run pytest tests/test_01_piservo.py
    ```

*   **Run Specific Test (by name):**
    ```bash
    uv run pytest -k "test_servo_move"
    ```

## Code Quality

*   **Linting (Check for errors and style violations):**
    ```bash
    uv run ruff check .
    ```

*   **Formatting (Automatically fix style violations):**
    ```bash
    uv run ruff format .
    ```

*   **Type Checking:**
    ```bash
    uv run mypy src/
    ```

## Building and Publishing

*   **Build the package:**
    ```bash
    uv run hatch build
    ```

*   **Publish to PyPI (or TestPyPI):**
    (Requires `twine` and proper credentials)
    ```bash
    uv run hatch build
    uv run twine upload --repository testpypi dist/*
    # Or for official PyPI:
    # uv run twine upload dist/*
    ```

## Git Commands

*   **Check Status:**
    ```bash
    git status
    ```

*   **View Differences:**
    ```bash
    git diff
    ```

*   **Stage Changes:**
    ```bash
    git add .
    ```

*   **Commit Changes:**
    ```bash
    git commit -m "Your commit message"
    ```

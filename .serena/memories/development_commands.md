# Development Commands

- **Command Execution**: `uv run <command>`
- **Library Installation**: `uv add <package_name>` (do not use `pip` directly)
- **Linting**:
    - `uv run ruff format src samples tests`
    - `uv run ruff check --fix --extend-select I src samples tests`
    - `uv run mypy src samples tests`
- **Testing**: `uv run python -m pytest -v <test_file_or_directory>`
- **CLI Entrypoints**:
    - Calibration: `uv run pi0servo calib <gpio_pin>`
    - API Server: `uv run pi0servo api-server <gpio_pin1> <gpio_pin2> ...`
    - API Client (JSON): `uv run pi0servo api-client`
    - String Command API Client: `uv run pi0servo str-client` (or `uv run pi0servo` for default)
    - Servo Control: `uv run pi0servo servo` (details to be confirmed)
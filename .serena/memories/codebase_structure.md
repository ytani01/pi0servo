# Codebase Structure: pi0servo

The `pi0servo` project is organized into the following main directories and subdirectories:

*   **`/` (Project Root):**
    *   `pyproject.toml`: Project metadata, dependencies, build configuration, and development tool settings (ruff, mypy, pytest).
    *   `README.md`: Project overview, features, installation instructions, and basic usage.
    *   `LICENSE`: Project licensing information (MIT License).
    *   `mise.toml`: (Inferred) Configuration for `uv` or similar environment manager.
    *   `.gitignore`: Specifies intentionally untracked files to ignore.
    *   `ToDo.md`: Project's main ToDo list.
    *   `archives/`: Directory for old ToDo lists or task archives.

*   **`docs/`:**
    *   Contains project documentation, including setup guides (`setup-pigpiod.md`), architecture diagrams (`SoftwareArchitecture-20251207a.png`), and specifications (`STR_CMD.md`, `JSONCMD_SAMPLES.md`, `JSONRPC-Errors.md`).
    *   `archives/`: Archived documentation.

*   **`samples/`:**
    *   Provides example Python scripts (`sample-01-threadworker.py`, `fastapi-test.py`, etc.) demonstrating various functionalities and API usages.
    *   Example script files (`sample-api.script`, `sample-str.script`, `sample-strcmd.txt`).

*   **`src/pi0servo/`:**
    *   The core source code of the `pi0servo` library.
    *   `__init__.py`: Package initialization.
    *   `__main__.py`: The main entry point for the command-line interface (`cli` function).
    *   `py.typed`: Indicates the package supports type hinting.
    *   **`command/`:** Contains modules for different CLI subcommands.
        *   `cmd_apicli.py`: API CLI command.
        *   `cmd_apiclient.py`: API client command.
        *   `cmd_apiserver.py`: API server command.
        *   `cmd_calib.py`: Calibration tool command.
        *   `cmd_jsonrpccli.py`: JSON-RPC CLI command.
        *   `cmd_servo.py`: Servo control command.
        *   `cmd_strcli.py`: String command CLI.
        *   `cmd_strclient.py`: String command client.
        *   `cmd_strjsonrpccli.py`: String JSON-RPC CLI.
    *   **`core/`:** Implements the fundamental servo control logic.
        *   `calibrable_servo.py`: Logic for individual calibrable servos.
        *   `multi_servo.py`: Logic for controlling multiple servos.
        *   `piservo.py`: Core `pigpio` interaction and servo management.
    *   **`helper/`:** Contains helper utilities and worker implementations.
        *   `commonlib.py`: Common utility functions.
        *   `json_cmds.json`: (Likely) JSON command definitions.
        *   `jsonrpc_worker.py`: JSON-RPC worker implementation.
        *   `str_cmd_to_json.md`: Documentation/specification for string command to JSON conversion.
        *   `str_cmd_to_json.py`: Implementation for string command to JSON conversion.
        *   `thread_worker.py`: Generic thread worker implementation.
    *   **`utils/`:** General utility modules.
        *   `clibase.py`: Base classes/functions for CLI.
        *   `clickutils.py`: Utilities related to `click` (CLI framework).
        *   `cliwithhistory.py`: CLI with history functionality.
        *   `mylogger.py`: Custom logging utility.
        *   `onekeycli.py`: Single-key CLI functionality.
        *   `scriptrunner.py`: Script execution utility.
        *   `servo_config_manager.py`: Manages servo configuration, including calibration data.
    *   **`web/`:** Web API related components.
        *   `api_client.py`: Web API client implementation.
        *   `json_api.py`: FastAPI application for the JSON API.
        *   `sample_json.js`: (Likely) Sample JSON data or client-side JavaScript.

*   **`tests/`:**
    *   Unit and integration tests for the `pi0servo` library.
    *   `_pigpio_mock.py`: Mock implementation of the `pigpio` library for testing.
    *   `_testbase_cli.py`: Base classes and utilities for testing CLI commands.
    *   `conftest.py`: Pytest configuration and fixtures.
    *   `test_*.py`: Individual test files covering various modules and functionalities.
    *   `TEST_04_MULTI_SERVO.md`: (Likely) Test documentation for multi-servo.

This structure indicates a well-organized project with clear separation of concerns, distinguishing between core logic, command-line interfaces, web APIs, helper utilities, and tests.
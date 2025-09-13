# Codebase Structure

The project's source code is organized under the `src/pi0servo/` directory, with distinct subdirectories for different functionalities.

- **`src/pi0servo/`**
  - **`__init__.py`**: Package initialization.
  - **`__main__.py`**: Entry point for the package when run as a module.
  - **`py.typed`**: Indicates the package supports type hints.
  - **`command/`**: Contains modules for various command-line interface (CLI) tools.
    - `cmd_apiclient.py`: CLI for the JSON API client.
    - `cmd_calib.py`: CLI for servo calibration.
    - `cmd_servo.py`: CLI for direct servo control.
    - `cmd_strclient.py`: CLI for the string command API client.
  - **`core/`**: Houses the core logic for servo control and management.
    - `calibrable_servo.py`: Implements servo calibration features.
    - `multi_servo.py`: Manages multiple servo motors.
    - `piservo.py`: Basic `pigpio`-based servo control.
  - **`helper/`**: Provides helper utilities and modules.
    - `str_cmd_to_json.py`: Converts string commands to JSON format.
    - `thread_multi_servo.py`: Threading implementation for multi-servo control.
    - `thread_worker.py`: Generic worker thread utility.
  - **`utils/`**: Contains general utility functions and classes.
    - `click_utils.py`: Utilities for `click` CLI framework.
    - `my_logger.py`: Custom logging configuration (not to be modified).
    - `servo_config_manager.py`: Manages servo configuration settings.
  - **`web/`**: Contains modules related to the web API.
    - `api_client.py`: Client-side logic for the API.
    - `json_api.py`: Implements the JSON-based REST API.

- **`docs/`**: Documentation files, including setup guides, API references, and design documents.

- **`tests/`**: Contains unit and integration tests for the project, typically numbered sequentially (e.g., `test_01_piservo.py`).

- **`archives/`**: Stores archived `Tasks.md` files.
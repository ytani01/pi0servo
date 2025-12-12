# Code Style and Conventions

- **Comments**: All comments should be in Japanese.
- **Line Length**: Maximum 78 characters per line.
- **Logging**: Use `get_logger()` from `my_logger.py` for all logging. The `my_logger.py` file should not be modified.
- **`git commit`**: Commits are to be performed only by the user. The AI will suggest a 1-line English commit message.
- **Linting**:
    - `uv run ruff format src samples tests`
    - `uv run ruff check --fix --extend-select I src samples tests`
    - `uv run mypy src samples tests`
- **Testing**: Test files are located in the `tests/` directory and are numbered (e.g., `test_01_piservo.py`).
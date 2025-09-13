# Task Completion Workflow

- `git commit` is user-only.
- Prompt for commit with a 1-line English message.
- When `Tasks.md` is complete:
    1. Report completion to the user and prompt them to update `ToDo.md`.
    2. Run `uv run rename_task.py` to rename `Tasks.md` to `yyyymmdd-HHMM-Tasks-done.md` and move it to `archives/`.

# Commands for Testing, Formatting, and Linting

- Linting:
    - `uv run ruff check ...`
    - `uv run mypy ...`
    - `uv run pyright ...`
- Testing: `uv run python -m pytest -v ...` (tests are in `tests/` and numbered sequentially)
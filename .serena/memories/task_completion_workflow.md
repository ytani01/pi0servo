# Task Completion Workflow

When a task is completed, the following steps should be performed:

1.  **Linting:** Run the linters to ensure code quality and adherence to style guidelines.
    - `uv run ruff check .`
    - `uv run mypy .`
    - `uv run pyright .`

2.  **Testing:** Create or update tests as necessary and run the test suite to verify functionality.
    - `uv run python -m pytest -v`

3.  **Task Management:** If working with `Tasks.md`:
    - Mark the completed task in `Tasks.md`.
    - If all tasks in `Tasks.md` are complete, run `uv run rename_task.py` to archive `Tasks.md`.
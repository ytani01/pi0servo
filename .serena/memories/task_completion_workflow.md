`Tasks.md` is created and managed by AI.
Tasks are executed sequentially from `Tasks.md`.
After each code change: linting, test creation/update/execution.
Upon completion of all tasks in `Tasks.md`: report to user, prompt user to update `ToDo.md`, then run `uv run rename_task.py` to rename `Tasks.md` to `yyyymmdd-HHMM-Tasks-done.md` and move it to `archives/`.
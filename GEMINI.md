# GEMINI.md

Development rules for Gemini CLI.


## 1. Project Goals

- Provide a Python driver for servo motors.
- Must run reliably even on low-spec devices such as **Raspberry Pi Zero 2W**.
- Must use **pigpio**.
- Should work both as a library and as a CLI, so users can run checks and demos easily.


## 2. Project-Wide Rules

- Research thoroughly before experimenting.

- **`git commit` is performed only by the user.**
  - When a commit is appropriate, prompt the user to commit.
  - Always suggest a short, one-line commit message in English.

- **Project configuration and management** must be handled through `uv` and `pyproject.toml`.
  - Always follow the latest `uv` specification.

- **Command execution** should always use `uv run ...`.

- **Installing/adding libraries** must be done with `uv add ...`.

- **Linting** should be run with:
  - `uv run ruff check ...`
  - `uv run mypy ...`
  - `uv run pyright ...`

- **Test programs** must be created under the `tests` directory, numbered sequentially.
- **Running tests** must be done with:  
  `uv run python -m pytest -v ...`

- **Safe file updates**: always create a new file and replace the old one.


## 3. Coding Rules

- Source code comments should generally be in Japanese.
- Keep each line within 78 characters.
- Use `get_logger()` from `my_logger.py` for debug logs.
- Do not modify `my_logger.py`.


## 4. Task Planning and Execution: `ToDo.md` and `Tasks.md`

- `ToDo.md` is edited **only by the user**.
- `Tasks.md` is created and managed by the AI.

- First, check whether `ToDo.md` and `Tasks.md` exist in the project root.
  - If neither exists, do nothing and ask the user what to do.

- If either file exists, follow the rules below.

- Before starting any work, always create a `Tasks.md`, and always ask the user for confirmation before executing.  
  Do not proceed until the user explicitly says **"go ahead"**.


### 4.1 When `Tasks.md` exists

- Follow the tasks in order, starting from the first unchecked item.
- After modifying source code, always:
  - Run linting
  - Create, update, and run test programs

- Mark completed tasks in `Tasks.md`.

- If new tasks are needed, add them to `Tasks.md` first, then execute.

- When modifying `Tasks.md`:
  1. Always ask the user for confirmation before executing.
  2. Do not proceed until the user says **"go ahead"**.

- When all tasks in `Tasks.md` are completed:
  1. Update `ToDo.md` and check off completed items.
  2. Run `uv run rename_task.py`.  
     This script:
     - Renames `Tasks.md` to `yyyymmdd-HHMM-Tasks-done.md`  
       (`yyyymmdd` = date, `HHMM` = time).
     - Moves the file into the `archives` directory.


### 4.2 When `Tasks.md` does not exist

- Review `ToDo.md`:
  - Identify the first unchecked item under **priority items**.
  - Draft an execution plan, break it into detailed tasks, and create a checklist in `Tasks.md`.
  - In principle, one item in `ToDo.md` = one `Tasks.md`.
  - Once `Tasks.md` is created, always ask the user for confirmation before executing.
  - If the user says **"go ahead"**, execute the tasks in order.

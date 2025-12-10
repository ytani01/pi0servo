# Task Completion Steps: pi0servo

When a development task is completed in the `pi0servo` project, follow these steps to ensure code quality, consistency, and proper integration:

1.  **Run Tests:**
    Execute the test suite to verify that your changes have not introduced any regressions and that new features work as expected.
    ```bash
    uv run pytest
    ```

2.  **Run Linter:**
    Check for any linting errors or style violations using `ruff`.
    ```bash
    uv run ruff check .
    ```

3.  **Run Formatter:**
    Automatically format your code to adhere to the project's style guidelines using `ruff format`.
    ```bash
    uv run ruff format .
    ```

4.  **Run Type Checker:**
    Perform static type checking with `mypy` to catch type-related issues.
    ```bash
    uv run mypy src/
    ```

5.  **Review Changes (Git Diff):**
    Before committing, review all your changes using `git diff` to ensure only intended modifications are included.
    ```bash
    git diff
    ```

6.  **Commit Changes:**
    Stage and commit your changes with a clear and concise commit message.
    ```bash
    git add .
    git commit -m "Your descriptive commit message"
    ```

By following these steps, you ensure that your contributions meet the project's quality standards and integrate smoothly into the existing codebase.
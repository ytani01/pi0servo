# Code Style and Conventions

- **Comments:** All comments should be written in Japanese.
- **Line Length:** Code lines should be kept within 78 characters.
- **Logging:** The project uses a custom logging utility from `src/pi0servo/utils/my_logger.py` via `get_logger()`. This logging implementation should not be modified.
- **Git Commits:** `git commit` operations are exclusively performed by the user. The AI will prompt for commits and suggest a single-line English message when necessary.
- **File Updates:** When modifying files, the standard procedure is to create a new file with the changes and then replace the original file.
- **Naming Conventions:** (To be inferred from existing code if not explicitly stated, but `GEMINI.md` and `README.md` don't specify beyond general Python best practices).
- **Type Hints:** (To be inferred from existing code if not explicitly stated).
- **Docstrings:** (To be inferred from existing code if not explicitly stated).
## Linting
- `uv run ruff check ...`
- `uv run mypy ...`
- `uv run pyright ...`

## Testing
- `uv run python -m pytest -v ...`

## Running Entrypoints
- **Calibration Tool:** `uv run pi0servo calib <pin_number>`
- **API Server:** `uv run pi0servo api-server <pin1> <pin2> ...`
- **API Client (JSON):** `uv run pi0servo api-client`
- **String Command API Client:** `uv run pi0servo` (or `uv run pi0servo --angle_factor -1,-1,1,1 --url http://192.168.x.x:8000/cmd`)
- **Servo Command:** `uv run pi0servo servo <pin_number> <pulse_value>`

## System Utilities
- Standard Linux commands (e.g., `git`, `ls`, `cd`, `grep`, `find`, `rm`, `mkdir`, `mv`)
- `uv` for package management and running commands (`uv run ...`, `uv add ...`)

## Other
- **Git Commit:** `git commit` (user-only, AI suggests message)
- **File Updates:** Create new file, then replace old file.
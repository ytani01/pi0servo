#
import pytest

CMD = "uv run pi0servo servo"


class TestBasic:
    """Basic tests."""

    @pytest.mark.parametrize(
        "args, stdout, stderr",
        [
            ("25 1400 -w .5", ["pin=25", "pulse=1400"], ""),
            ("25 1600 -w .5 -d", "pin=25, pulse=1600", "wait_sec=0.5"),
            ("25 1600 -w .5 -h", "Options", ""),
        ],
    )
    def test_servo(self, cli_runner, args, stdout, stderr):
        """servo command"""
        cli_runner.test_command(
            CMD, args, e_stdout=stdout, e_stderr=stderr, timeout=60
        )

    @pytest.mark.parametrize(
        "args, stdout, stderr",
        [
            ("25 0", "done", ["ERROR", "invalid value"]),
            ("25 3000", "done", ["ERROR", "invalid value"]),
            ("", "", ["Usage: ", "Error: Missing argument", "PIN"]),
            ("25", "", ["Usage:", "Error: Missing argument", "PULSE"]),
            ("25 1300 -x", "", ["Usage:", "Error: No such option"]),
        ],
    )
    def test_servo_err(self, cli_runner, args, stdout, stderr):
        """servo command"""
        cli_runner.test_command(CMD, args, e_stdout=stdout, e_stderr=stderr)

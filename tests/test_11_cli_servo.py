#
import pytest


CMD = "uv run pi0servo servo"


class TestBasic:
    """Basic tests."""
    @pytest.mark.parametrize(
        "params, expected",
        [
            ("5 1000", "pin=5, pulse=1000"),
            ("25 2000", "pin=25, pulse=2000")
        ],
    )
    def test_servo(self, cli_runner, params, expected):
        """servo command"""
        cmdline = f"{CMD} {params}"
        result = cli_runner.run_command(cmdline.split())
        cli_runner.assert_output_contains(result, stdout=expected)

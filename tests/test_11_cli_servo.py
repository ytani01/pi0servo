#
import pytest

CMD = "uv run pi0servo servo"


class TestBasic:
    """Basic tests."""

    @pytest.mark.parametrize(
        "args, stdout, stderr",
        [
            ("25 1000 -w .5", "pin=25, pulse=1000", ""),
            ("25 2000 -w .5 -d", "pin=25, pulse=2000", "wait_sec=0.5"),
            ("25 2000 -w .5 -h", "Options", ""),
            ("25 0", "done", "invalid value"),
            ("25 3000", "done", "invalid value"),
            ("", "", "Error: Missing argument"),
            ("25", "", "Error: Missing argument"),
            ("25 2000 -x", "", "Error: No such option"),
        ],
    )
    def test_servo(self, cli_runner, args, stdout, stderr):
        """servo command"""
        cmdline = f"{CMD} {args}"
        print(f"\n* cmdline='{cmdline}'")

        result = cli_runner.run_command(cmdline.split())
        print(f"* stdout='''{result.stdout}'''")
        print(f"** expect='{stdout}'")
        print(f"* stderr='''{result.stderr}'''")
        print(f"** expect='{stderr}'")

        cli_runner.assert_output_contains(
            result, stdout=stdout, stderr=stderr
        )

#
import pytest
from click.testing import CliRunner

from pi0servo.__main__ import cli


class TestCliServo:
    """Tests for the 'servo' CLI command using CliRunner."""

    def test_servo_success(self, click_runner: CliRunner, mocker_pigpio):
        """Test successful servo command execution."""
        args = ["servo", "25", "1600", "-w", "0.5", "-d"]
        result = click_runner.invoke(cli, args)
        assert result.exit_code == 0
        assert "pin=25, pulse=1600" in result.output
        assert "wait_sec=0.5" in result.output

    def test_servo_help(self, click_runner: CliRunner):
        """Test servo command with --help option."""
        args = ["servo", "--help"]
        result = click_runner.invoke(cli, args)
        assert result.exit_code == 0
        assert "Usage: cli servo [OPTIONS] PIN PULSE" in result.output
        assert "Options:" in result.output

    @pytest.mark.parametrize(
        ("args", "expected_output"),
        [
            (
                ["servo", "25", "0"],
                ["Error", "not in the range 500<=x<=2500"],
            ),
            (
                ["servo", "25", "3000"],
                ["Error", "not in the range 500<=x<=2500"],
            ),
            (["servo"], ["Error", "Missing argument 'PIN'"]),
            (["servo", "25"], ["Error", "Missing argument 'PULSE'"]),
            (
                ["servo", "25", "1500", "-x"],
                ["Error", "No such option: -x"],
            ),
        ],
    )
    def test_servo_errors(
        self,
        click_runner: CliRunner,
        mocker_pigpio,
        args: list[str],
        expected_output: list[str],
    ):
        """Test various errors for the servo command."""
        result = click_runner.invoke(cli, args)
        assert result.exit_code != 0
        for expected in expected_output:
            assert expected in result.output

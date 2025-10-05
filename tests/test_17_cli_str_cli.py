#
import pytest

CMDNAME = "str-cli"
CMD = f"uv run pi0servo {CMDNAME} --history_file /tmp/testhist"
PINS = "25 27"


class TestCmdStrCli:
    """Test CmdStrCli."""

    @pytest.mark.parametrize(
        "args, stdout, stderr",
        [
            ("", "Please specify GPIO pins", ""),
            ("-d", "Please specify GPIO pins", "DEBUG"),
            ("-h", "Usage: ", ""),
            ("-V", "pi0servo", ""),
        ],
    )
    def test_cli_cmdline(self, cli_runner, args, stdout, stderr):
        """Cilent String CLI."""
        cli_runner.test_command(CMD, args, e_stdout=stdout, e_stderr=stderr)

    @pytest.mark.parametrize(
        "inout",
        [
            [
                {"in": "\n", "out": ["", f"{CMDNAME}>"]},
                {"in": "mv:-30,-30\n", "out": ["method", "[-30, -30]"]},
                {"in": "mv:30,30 mv:0,0\n", "out": ["[30, 30]", "[0, 0]"]},
                {"in": "zz\n", "out": ["cancel", "'value': ", "'qsize': 0"]},
                {"in": "qq\n", "out": ["qsize", "result", "'value': 0"]},
            ],
            [
                {
                    "in": "ms:0.5 mv:0,0 ww\n",
                    "out": ["'qsize': 1", "'qsize': 0"],
                },
            ],
            [
                {"in": "mv:0\n", "out": ["{'angles': [0]}", "ERROR"]},
                {"in": "a\n", "out": ["err", "METHOD_NOT_FOUND"]},
            ],
        ],
    )
    def test_cli_inout(self, cli_runner, inout):
        """Cilent String CLI."""
        cli_runner.test_interactive(CMD, PINS, in_out=inout)

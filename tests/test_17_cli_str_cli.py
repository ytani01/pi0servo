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
                {"in": "mv:-10,-10\n", "out": ["method", "[-10, -10]"]},
                {"in": "mv:10,10 mv:0,0\n", "out": ["[10, 10]", "[0, 0]"]},
                {"in": "zz\n", "out": ["cancel", "'value': ", "'qsize': 0"]},
                {"in": "qq\n", "out": ["qsize", "result", "'value': 0"]},
                {"in": "ww\n", "out": ["'qsize': 0", "flag': False"]},
            ],
            [
                {"in": "sl:.5 ww\n", "out": ["'qsize': 0", "flag': False"]},
                {"in": "mp:0,-50\n", "out": ["50}}}}", f"{CMDNAME}>"]},
                {"in": "sl:.5 ww\n", "out": ["'qsize': 0", "flag': False"]},
                {"in": "mp:0,50\n", "out": ["50}}}}", f"{CMDNAME}>"]},
                {"in": "sl:.5 ww\n", "out": ["'qsize': 0", "flag': False"]},
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

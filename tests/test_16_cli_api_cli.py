#
import pytest

CMDNAME = "api-cli"
CMD = f"uv run pi0servo {CMDNAME} --history_file /tmp/testhist"
PINS = "25 27"


class TestCmdApiCli:
    """Test."""

    @pytest.mark.parametrize(
        "args, stdout, stderr",
        [
            ("", "Please specify GPIO pins", ""),
            ("-d", "Please specify GPIO pins", "DEBUG"),
            ("-h", "Usage: ", ""),
            ("-V", "pi0servo", ""),
        ],
    )
    def test_cli_cmdline_err(self, cli_runner, args, stdout, stderr):
        """servo command"""
        cmdline = f"{CMD} {args}"
        cli_runner.test_command(cmdline, e_stdout=stdout, e_stderr=stderr)

    @pytest.mark.parametrize(
        ["indata", "expected"],
        [
            ("\n", [f"{CMDNAME}>"]),
            (
                '{"method": "move", "params": {"angles": [30, 30]}}\n',
                ["'value': None", f"{CMDNAME}"],
            ),
            (
                (
                    '{"method": "move", "params": {"angles": [30, 30]}}, '
                    '{"method": "move", "params": {"angles": [0, 0]}}'
                    "\n"
                ),
                ["[30, 30]", "[0, 0]"],
            ),
            (
                '{"method": "cancel"}\n',
                ["'value': 0", f"{CMDNAME}>"],
            ),
            ('{"method": "qsize"}\n', ["'value': ", f"{CMDNAME}>"]),
            (
                "["
                '{"method":"move_sec","params": {"sec": 1}}, '
                '{"method":"move","params":{"angles":[20,-20]}}, '
                '{"method":"move","params":{"angles":[0,0]}}, '
                '{"method":"wait"}'
                "]\n",
                ["'qsize': 1", "'qsize': 0"],
            ),
            ("a\n", ["JSONDecodeError", f"{CMDNAME}>"]),
        ],
    )
    def test_cli_interactive(self, cli_runner, indata, expected):
        """servo command"""
        cmdline = f"{CMD} {PINS}"
        inout = {"in": indata, "out": expected}
        cli_runner.test_interactive(cmdline, in_out=inout)

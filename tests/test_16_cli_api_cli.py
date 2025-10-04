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
        result = cli_runner.run_command(cmdline.split())
        print(f"* stdout='''{result.stdout}'''")
        print(f"** expect='{stdout}'")
        print(f"* stderr='''{result.stderr}'''")
        print(f"** expect='{stderr}'")

        cli_runner.assert_output_contains(
            result, stdout=stdout, stderr=stderr
        )

    @pytest.mark.parametrize(
        "inout",
        [
            [
                {"in": "\n", "out": ["", f"{CMDNAME}>"]},
                {
                    "in": (
                        '{"method": "move", "params": {"angles": [30, 30]}}\n'
                    ),
                    "out": ["'value': None", f"{CMDNAME}"],
                },
            ],
            [
                {
                    "in": (
                        '{"method": "move", "params": {"angles": [30, 30]}}, '
                        '{"method": "move", "params": {"angles": [0, 0]}}'
                        "\n"
                    ),
                    "out": ["[30, 30]", "[0, 0]"],
                },
                {
                    "in": '{"method": "cancel"}\n',
                    "out": ["'value': 0", f"{CMDNAME}>"],
                },
                {
                    "in": '{"method": "qsize"}\n',
                    "out": ["'value': ", f"{CMDNAME}>"],
                },
            ],
            [
                {
                    "in": (
                        "["
                        '{"method":"move_sec","params": {"sec": 1}}, '
                        '{"method":"move","params":{"angles":[20,-20]}}, '
                        '{"method":"move","params":{"angles":[0,0]}}, '
                        '{"method":"wait"}'
                        "]\n"
                    ),
                    "out": ["'qsize': 1", "'qsize': 0"],
                },
                {"in": "a\n", "out": ["JSONDecodeError", f"{CMDNAME}>"]},
            ],
        ],
    )
    def test_cli_interactive(self, cli_runner, inout):
        """servo command"""
        cmdline = f"{CMD} {PINS}"
        cli_runner.test_interactive(cmdline, in_out=inout)

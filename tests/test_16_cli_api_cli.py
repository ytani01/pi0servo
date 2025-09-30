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
            (
                "",
                "Please specify GPIO pins",
                ""
            ),
            (
                "-d",
                "Please specify GPIO pins",
                "DEBUG"
            ),
            (
                "-h",
                "Usage: ",
                ""
            ),
            (
                "-V",
                "pi0servo",
                ""
            ),
        ]
    )
    def test_cli_err1(self, cli_runner, args, stdout, stderr):
        """servo command"""
        cmdline = f"{CMD} {args}"
        print(f"\n* cmdline='{cmdline}'")

        result = cli_runner.run_command(cmdline.split())
        print(f"* stdout='''{result.stdout}'''")
        print(f"** expect='{stdout}'")
        print(f"* stderr='''{result.stderr}'''")
        print(f"** expect='{stderr}'")

        cli_runner.assert_output_contains(
            result,
            stdout=stdout,
            stderr=stderr
        )

    @pytest.mark.parametrize(
        "instr, expect1, expect2",
        [
            (
                '\n',
                "",
                f"{CMDNAME}>"
            ),
            (
                '{"method": "move", "params": {"angles": [30, 30]}}\n',
                "OK",
                f"{CMDNAME}"
            ),
            (
                '['
                '{"method": "move", "params": {"angles": [30, 30]}},'
                '{"method": "move", "params": {"angles": [0, 0]}}'
                ']\n',
                "OK",
                f"{CMDNAME}>"
            ),
            (
                '{"method": "cancel"}\n',
                "'value': 0",
                f"{CMDNAME}>"
            ),
            (
                '{"method": "qsize"}\n',
                "'value': ",
                f"{CMDNAME}>"
            ),
            (
                "a\n",
                "JSONDecodeError",
                f"{CMDNAME}>"
            ),
        ],
    )
    def test_cli(self, cli_runner, instr, expect1, expect2):
        """servo command"""
        cmdline = f"{CMD} {PINS}"
        print(f"* cmdline='{cmdline}'")

        session = cli_runner.run_interactive_command(cmdline.split())

        session.send_key(instr)
        if expect1:
            print(f"expect1={expect1}")
            assert session.expect(expect1)
        if expect2:
            print(f"expect2={expect2}")
            assert session.expect(expect2)

        session.close()
        # time.sleep(3)

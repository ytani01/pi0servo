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
            result, stdout=stdout, stderr=stderr
        )

    @pytest.mark.parametrize(
        "instr, expect1, expect2",
        [
            ("\n", "", f"{CMDNAME}>"),
            (
                "mv:-30,-30\n",
                "method",
                "[-30, -30]",
            ),
            ("mv:30,30 mv:0,0\n", "[30, 30]", "[0, 0]"),
            ("zz\n", "cancel", "'value': 0"),
            ("qq\n", "result", "'value': 0"),
            ("ms:0.5 mv:0,0 ww\n", "'qsize': 1", "'qsize': 0"),
            (
                "mv:0\n",
                "{'angles': [0]}",
                "ERROR",
            ),
            (
                "a\n",
                "err",
                "METHOD_NOT_FOUND",
            ),
        ],
    )
    def test_cli(self, cli_runner, instr, expect1, expect2):
        """servo command"""
        cmdline = f"{CMD} {PINS}"
        print(f"* cmdline='{cmdline}'")

        session = cli_runner.run_interactive_command(cmdline.split())

        print(f"* instr={instr!r}")
        session.send_key(instr)
        if expect1:
            print(f"* expect1={expect1}")
            assert session.expect(expect1)
        if expect2:
            print(f"* expect2={expect2}")
            assert session.expect(expect2)

        session.close()
        # time.sleep(3)

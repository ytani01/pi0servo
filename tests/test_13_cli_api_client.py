#
import time

import pytest

CMD = "uv run pi0servo api-client --history_file /tmp/testhist"


class TestBasic:
    """Basic tests."""

    @pytest.mark.parametrize(
        "inout",
        [
            [
                {
                    "in": '{"method": "cancel"}\n',
                    "out": ["NewConnectionError", "result=", "api-client>"],
                },
                {"in": "a\n", "out": ["JSONDecodeError", "api-client>"]},
            ],
        ],
    )
    def test_api_client(self, cli_runner, inout):
        """servo command"""
        cli_runner.test_interactive(CMD, in_out=inout)

        # session = cli_runner.run_interactive_command(cmdline)

        # session.send_key(instr)
        # assert session.expect(expect1)
        # assert session.expect(expect2)

        # session.close()
        # time.sleep(3)

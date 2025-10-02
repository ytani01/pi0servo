#
import time

import pytest

CMD = "uv run pi0servo api-client --history_file /tmp/testhist"


class TestBasic:
    """Basic tests."""

    @pytest.mark.parametrize(
        "instr, expect1, expect2",
        [
            ('{"method": "cancel"}\n', "result=", "api-client"),
            ("a\n", "JSONDecodeError", "api-client>"),
        ],
    )
    def test_api_client(self, cli_runner, instr, expect1, expect2):
        """servo command"""
        cmdline = f"{CMD}"
        print(f"* cmdline='{cmdline}'")

        session = cli_runner.run_interactive_command(cmdline.split())

        session.send_key(instr)
        assert session.expect(expect1)
        assert session.expect(expect2)

        session.close()
        time.sleep(3)

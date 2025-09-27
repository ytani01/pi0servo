#
import time

import pytest

CMD = "uv run pi0servo api-client"


class TestBasic:
    """Basic tests."""
    @pytest.mark.parametrize(
        "instr, expect",
        [
            ("\n",  "api-client>"),
            ("a\n", "api-client>"),
            ("a\n", "Error"),
        ],
    )
    def test_servo(self, cli_runner, instr, expect):
        """servo command"""
        cmdline = f"{CMD}"
        print(f'''
* cmdline='{cmdline}''')

        session = cli_runner.run_interactive_command(cmdline.split())

        session.send_key(instr)
        assert session.expect(expect)

        session.close()
        time.sleep(2)

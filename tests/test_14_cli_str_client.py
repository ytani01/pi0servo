#
import time

import pytest

CMD = "uv run pi0servo str-client"

class TestBasic:
    """Basic tests."""
    @pytest.mark.parametrize(
        "instr, expect",
        [
            ("\n",  "str-client>"),
            ("a\n", "str-client>"),
            ("a\n", "Error"),
        ],
    )
    def test_servo(self, cli_runner, instr, expect):
        """servo command"""
        cmdline = f"{CMD}"
        print(f"\n* cmdline='{cmdline}'")
        
        session = cli_runner.run_interactive_command(cmdline.split())

        session.send_key(instr)
        assert session.expect(expect)

        session.close()
        time.sleep(2)

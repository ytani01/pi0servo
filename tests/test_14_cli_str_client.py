#
import time

import pytest

CMD = "uv run pi0servo str-client --history_file /tmp/testhist"


class TestBasic:
    """Basic tests."""
    @pytest.mark.parametrize(
        "instr, expect",
        [
            ("\n",  "str-client>"),
            ("a\n", "str-client>"),
            ("a\n", "error"),
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

#
import time

import pytest

CMD = "uv run pi0servo calib"
PIN = 25

KEY_TAB = '\x09'
KEY_C_C = '\x03'  # Ctrl-C

class TestBasic:
    """Basic tests."""
    @pytest.mark.parametrize(
        "arg, opt, inkey1, expect1, inkey2, expect2",
        [
            (PIN, "", KEY_TAB, "GPIO",        KEY_TAB, "GPIO"),
            (PIN, "", "h",     "Select",      "h",     "Misc"),
            (PIN, "", "q",     "== Quit ==",  "",      ""),
            (PIN, "", KEY_C_C, "conf_file",   "",      ""),
        ],
    )
    def test_servo(
        self, cli_runner, arg, opt, inkey1, expect1, inkey2, expect2
    ):
        """servo command"""
        cmdline = f"{CMD} {arg} {opt}"
        print(f"\n* cmdline='{cmdline}'")
        
        session = cli_runner.run_interactive_command(cmdline.split())
        time.sleep(1)

        if inkey1:
            print(f"* inkey1='{inkey1}'")
            session.send_key(inkey1)
            assert session.expect(expect1)
            time.sleep(1)

        if inkey2:
            print(f"* inkey2='{inkey2}'")
            session.send_key(inkey2)
            assert session.expect(expect2)
            #time.sleep(1)

        session.close()
        time.sleep(1)

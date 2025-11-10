#
import signal
import time

import pytest

CMD = "uv run pi0servo calib -f /tmp/test.json"
PIN = 2

KEY_TAB = "\x09"
KEY_C_C = "\x03"  # Ctrl-C


class TestBasic:
    """Basic tests."""

    @pytest.mark.parametrize(
        ("arg", "opt", "inkey1", "expect1", "inkey2", "expect2"),
        [
            (PIN, "", KEY_TAB, "GPIO", KEY_TAB, "GPIO"),
            (PIN, "", "h", "Select", "h", "Misc"),
            (PIN, "", "q", "== Quit ==", "", ""),
            (PIN, "", KEY_C_C, "conf_file", "", ""),
        ],
    )
    def test_cli_calib(
        self, cli_runner, arg, opt, inkey1, expect1, inkey2, expect2
    ):
        """servo command"""
        cmdline = f"{CMD} {arg} {opt}"

        in_out = [
            {"in": inkey1, "out": expect1},
            {"in": inkey2, "out": expect2},
        ]

        cli_runner.test_interactive(cmdline, in_out=in_out, timeout=10.0)

    @pytest.mark.parametrize(
        ("arg", "opt", "sig"),
        [
            (PIN, "", signal.SIGTERM),
        ],
    )
    def test_cli_calib_signal(self, cli_runner, arg, opt, sig):
        """servo command"""
        cmdline = f"{CMD} {arg} {opt}"
        session = cli_runner.run_interactive_command(cmdline)
        time.sleep(1)

        proc = session.process

        print(f"* send_signal: {sig}")
        proc.send_signal(sig)
        proc.wait(timeout=3)

        ret = proc.returncode
        print(f"""ret={ret}""")

        if ret > 128:
            assert ret - 128 == int(sig)
        elif ret < 0:
            assert -ret == int(sig)
        else:
            assert ret == 0

        session.close()
        time.sleep(1)

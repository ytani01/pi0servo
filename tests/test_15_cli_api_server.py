#
import time

CMD = "uv run pi0servo api-server"
PIN = 25


class TestBasic:
    """Basic tests."""
    def test_start(self, cli_runner):
        """server start"""

        cmdline = f"{CMD} {PIN}"
        print(f'''
* cmdline='{cmdline}''')

        session = cli_runner.run_interactive_command(cmdline.split())

        # time.sleep(5)

        assert session.expect("Initializing")
        assert session.expect("Application startup complete")

        session.close()
        time.sleep(3)

    def test_start_err(self, cli_runner):
        """server start error """

        cmdline = CMD
        print(f'''
* cmdline='{cmdline}''')

        result = cli_runner.run_command(cmdline.split())
        print(f'''stdout='{result.stdout}''')
        print(f'''stderr='{result.stderr}''')

        cli_runner.assert_output_contains(result, stdout="Error")
        cli_runner.assert_output_contains(result, stdout="Usage")
        cli_runner.assert_output_contains(result, stdout="Options")

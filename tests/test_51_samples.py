#
# **Memo**
# このメモは、備忘録として残す。
#
# [問題]
# 'uv run pytest -v tests/test_51_samples.py'は、成功するが、
# 'uv run pytest -v tests'は、失敗する！？
#   :
# [解決]
# 'test_02_servo_config_manager.py'のモンキーパッチの使い方が誤っていて、
# 'os.getcwd'を書き換えていた。
#

import pytest


class TestSamplePrograms:
    """Test sample programs."""

    @pytest.mark.parametrize(
        "sample",
        [
            "sample-01-threadworker.py",
            "sample-02-threadworker-strcmd.py",
            "sample-03-threadmultiservo.py",
        ],
    )
    def test_sample_program(self, cli_runner, sample):
        """Test sample."""
        #
        # 下記のコードは、トラブル対応で有効に機能したので、
        # コメントアウトして残しておく
        #
        # ```
        # print()
        # print(f"* cwd={os.getcwd()}")
        # os.chdir("/home/ytani/work/pi0servo")
        # print(f"* cwd={os.getcwd()}")
        # ```

        cmdline = f"uv run samples/{sample}"
        print(f"* cmdline={cmdline}")
        cli_runner.test_command(cmdline, e_ret=0)

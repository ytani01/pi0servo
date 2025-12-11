#
import signal
import time

import pytest

from pi0servo.command.cmd_calib import CalibApp # 追加

CMD = "python -m pi0servo calib -f /tmp/test.json"
PIN = 2

KEY_TAB = "\t"
KEY_C_C = "\x03"  # Ctrl-C


@pytest.fixture
def calib_app_instance(mocker_pigpio, tmp_path):
    """CalibAppのインスタンスとモックされたpiオブジェクトを提供するフィクスチャ"""
    pi_mock = mocker_pigpio.return_value # pigpio.pi()のインスタンスモック
    pin = 17
    conf_file = tmp_path / "test_calib.json"
    app = CalibApp(pi_mock, pin, str(conf_file), debug=True)
    yield app, pi_mock, conf_file
    app.end()


@pytest.mark.skip(
    reason="Cannot reliably mock pigpio in subprocess for interactive tests"
)
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


class TestCalibAppFunctionality:
    """CalibAppの機能テスト"""

    def test_calibration_save_and_load(self, calib_app_instance, mocker_pigpio):
        """キャリブレーション値の保存とロードのテスト (エンドツーエンド)"""
        app, pi_mock, conf_file = calib_app_instance

        # 既存のServoConfigManagerのキャッシュをクリアするために、新しいインスタンスを作成する
        # （これにより、ファイルから読み込み直されることを保証する）
        from pi0servo.utils.servo_config_manager import ServoConfigManager
        ServoConfigManager._instances = {} # キャッシュをクリア
        
        # モックのget_pulse()の戻り値を設定
        pi_mock.get_servo_pulsewidth.return_value = 1500 # 初期パルス値
        app.servo.move_center() # 初期位置に移動

        # キャリブレーション値を設定 (センター位置のパルス値を変更)
        app.set_target(app.TARGET_CENTER)
        pi_mock.get_servo_pulsewidth.return_value = 1550 # 新しいセンターパルス値
        app.move_diff(50) # 50パルスだけ動かす
        app.set_calibration() # この時点で保存される

        # キャリブレーション値を設定 (最小位置のパルス値を変更)
        app.set_target(app.TARGET_MIN)
        pi_mock.get_servo_pulsewidth.return_value = 1050 # 新しい最小パルス値
        app.move_diff(50) # 50パルスだけ動かす
        app.set_calibration() # この時点で保存される

        # キャリブレーション値を設定 (最大位置のパルス値を変更)
        app.set_target(app.TARGET_MAX)
        pi_mock.get_servo_pulsewidth.return_value = 1950 # 新しい最大パルス値
        app.move_diff(-50) # -50パルスだけ動かす
        app.set_calibration() # この時点で保存される

        # appを終了 (これにより設定ファイルが確実に書き込まれる)
        app.end()

        # 新しいCalibAppインスタンスを同じ設定ファイルで起動し、値が正しくロードされていることを確認
        reloaded_app = CalibApp(pi_mock, app.pin, str(conf_file), debug=True)
        assert reloaded_app.servo.pulse_center == 1550
        assert reloaded_app.servo.pulse_min == 1050
        assert reloaded_app.servo.pulse_max == 1950
        reloaded_app.end()




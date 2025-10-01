#
# (c) 2025 Yoichi Tanibayashi
#
"""
tests/test_07_threadworker.py
"""
import time
from unittest.mock import MagicMock, patch

import pytest

from pi0servo.core.multi_servo import MultiServo
from pi0servo.helper.thread_worker import ThreadWorker


@pytest.fixture
def mocker_multiservo():
    """MultiServoをモックするためのフィクスチャ"""
    with patch("pi0servo.core.multi_servo.MultiServo") \
            as mock_mservo_constructor:
        mock_mservo_instance = MagicMock(spec=MultiServo)
        mock_mservo_constructor.return_value = mock_mservo_instance
        yield mock_mservo_constructor


@pytest.fixture
def thread_worker(mocker_multiservo):
    """ThreadWorkerのテスト用インスタンスを生成するフィクスチャ"""
    mservo = mocker_multiservo()
    worker = ThreadWorker(mservo, debug=False)
    worker.start()  # スレッドを開始
    yield worker
    worker.end()  # テスト終了時にスレッドを終了


class TestThreadWorker:
    """ThreadWorkerクラスのテスト"""

    def test_init(self, thread_worker, mocker_multiservo):
        """初期化のテスト"""
        mservo = mocker_multiservo()
        assert thread_worker.mservo == mservo
        assert thread_worker.qsize == 0

    def test_send_move_all_angles_sync(self, thread_worker,
                                       mocker_multiservo):
        """move_all_angles_syncコマンドのテスト"""
        mservo = mocker_multiservo()
        cmd = {
            "method": "move_all_angles_sync",
            "params": {
                "angles": [30, None, "center"],
                "move_sec": 0.2,
                "step_n": 40
            }
        }
        thread_worker.send(cmd)
        time.sleep(0.5)  # コマンド処理を待つ

        mservo.move_all_angles_sync.assert_called_once_with(
            [30, None, "center"], 0.2, 40
        )
        assert thread_worker.qsize == 0

    def test_send_move_all_pulses(self, thread_worker, mocker_multiservo):
        """move_all_pulsesコマンドのテスト"""
        mservo = mocker_multiservo()
        cmd = {
            "method": "move_all_pulses",
            "params": {
                "pulses": [1000, 2000, None, 0]
            }
        }
        thread_worker.send(cmd)
        time.sleep(0.5)  # コマンド処理を待つ

        mservo.move_all_pulses.assert_called_once_with(
            [1000, 2000, None, 0]
        )
        assert thread_worker.qsize == 0

    def test_send_move_pulse_relative(self, thread_worker, mocker_multiservo):
        """move_pulse_relativeコマンドのテスト"""
        mservo = mocker_multiservo()
        cmd = {
            "method": "move_pulse_relative",
            "params": {
                "servo": 2,
                "pulse_diff": -20
            }
        }
        thread_worker.send(cmd)
        time.sleep(0.5)  # コマンド処理を待つ

        mservo.move_pulse_relative.assert_called_once_with(
            2, -20, forced=True
        )
        assert thread_worker.qsize == 0

    def test_send_set_command(self, thread_worker, mocker_multiservo):
        """setコマンドのテスト"""
        mservo = mocker_multiservo()
        cmd = {
            "method": "set",
            "params": {
                "servo": 1,
                "target": "center"
            }
        }
        thread_worker.send(cmd)
        time.sleep(0.5)  # コマンド処理を待つ

        mservo.set_pulse_center.assert_called_once_with(1)
        assert thread_worker.qsize == 0

    def test_send_invalid_command(self, thread_worker):
        """無効なコマンドのテスト"""
        cmd = {
            "method": "invalid_method",
            "params": {}
        }
        reply_json = thread_worker.send(cmd)
        time.sleep(0.5)  # コマンド処理を待つ

        assert reply_json["error"]["code"] == -32601
        assert "Invalid command" in reply_json["error"]["message"]
        assert thread_worker.qsize == 0

    def test_clear_cmdq(self, thread_worker):
        """clear_cmdqのテスト"""
        cmd1 = {"method": "move", "params": {"angles": [0]}}
        cmd2 = {"method": "sleep", "params": {"sec": 0.1}}
        thread_worker.send(cmd1)
        thread_worker.send(cmd2)

        thread_worker.clear_cmdq()
        assert thread_worker.qsize == 0

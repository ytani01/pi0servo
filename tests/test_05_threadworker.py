#
# (c) 2025 Yoichi Tanibayashi
#
"""
tests/test_07_threadworker.py
"""

import threading
import time
from unittest.mock import MagicMock, patch
import logging # 追加

import pytest

from pi0servo.core.multi_servo import MultiServo
from pi0servo.helper.thread_worker import ThreadWorker

PINS = [17, 18]


@pytest.fixture
def mocker_multiservo():
    """MultiServoをモックするためのフィクスチャ"""
    with patch(
        "pi0servo.helper.thread_worker.MultiServo"
    ) as mock_mservo_constructor:
        mock_mservo_instance = MagicMock(spec=MultiServo)
        mock_mservo_constructor.return_value = mock_mservo_instance
        yield mock_mservo_constructor


@pytest.fixture
def thread_worker(mocker_multiservo, mocker_pigpio):
    """ThreadWorkerのテスト用インスタンスを生成するフィクスチャ"""
    pi = mocker_pigpio()
    mocker_multiservo()
    worker = ThreadWorker(pi, PINS, debug=False)
    worker.start()  # スレッドを開始
    yield worker
    worker.end()  # テスト終了時にスレッドを終了


class TestThreadWorker:
    """ThreadWorkerクラスのテスト"""

    def _wait_for_mock_call(
        self, mock_obj, timeout=1.0, interval=0.01, sleep_func=time.sleep
    ):
        """
        モックオブジェクトが呼び出されるまで待機するヘルパーメソッド。
        time.sleepの代わりにこれを使用することで、テストの信頼性と速度を向上させる。
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if mock_obj.call_count > 0:
                return
            sleep_func(interval)
        raise TimeoutError(
            f"Mock object {mock_obj} was not called within {timeout} seconds"
        )

    def test_init(self, thread_worker):
        """初期化のテスト"""
        mservo_instance = thread_worker.mservo
        assert thread_worker.mservo == mservo_instance
        assert thread_worker.qsize == 0

    def test_send_move_all_angles_sync(self, thread_worker):
        """move_all_angles_syncコマンドのテスト"""
        mservo_instance = thread_worker.mservo
        cmd = {
            "method": "move_all_angles_sync",
            "params": {
                "angles": [30, None, "center"],
                "move_sec": 0.2,
                "step_n": 40,
            },
        }
        thread_worker.send(cmd)
        self._wait_for_mock_call(mservo_instance.move_all_angles_sync)

        mservo_instance.move_all_angles_sync.assert_called_once_with(
            [30, None, "center"], 0.2, 40
        )
        assert thread_worker.qsize == 0

    def test_send_move_all_pulses(self, thread_worker):
        """move_all_pulsesコマンドのテスト"""
        mservo_instance = thread_worker.mservo
        cmd = {
            "method": "move_all_pulses",
            "params": {"pulses": [1000, 2000, None, 0]},
        }
        thread_worker.send(cmd)
        self._wait_for_mock_call(mservo_instance.move_all_pulses)

        mservo_instance.move_all_pulses.assert_called_once_with(
            [1000, 2000, None, 0]
        )
        assert thread_worker.qsize == 0

    def test_send_move_pulse_relative(self, thread_worker):
        """move_pulse_relativeコマンドのテスト"""
        mservo_instance = thread_worker.mservo
        cmd = {
            "method": "move_pulse_relative",
            "params": {"servo_i": 2, "pulse_diff": -20},
        }
        thread_worker.send(cmd)
        self._wait_for_mock_call(mservo_instance.move_pulse_relative)

        mservo_instance.move_pulse_relative.assert_called_once_with(
            2, -20, forced=True
        )
        assert thread_worker.qsize == 0

    def test_send_set_command(self, thread_worker):
        """setコマンドのテスト"""
        mservo_instance = thread_worker.mservo
        cmd = {"method": "set", "params": {"servo": 1, "target": "center"}}
        thread_worker.send(cmd)
        self._wait_for_mock_call(mservo_instance.set_pulse_center)

        mservo_instance.set_pulse_center.assert_called_once_with(1)
        assert thread_worker.qsize == 0

    def test_send_invalid_command(self, thread_worker):
        """無効なコマンドのテスト"""
        cmd = {"method": "invalid_method", "params": {}}
        reply_json = thread_worker.send(cmd)

        assert reply_json["error"]["code"] == -32601
        assert "Invalid command" in reply_json["error"]["message"]
        assert thread_worker.qsize == 0

    @patch("time.sleep")
    def test_handle_sleep(self, mock_sleep, thread_worker, mocker):
        """_handle_sleepのテスト"""
        # _cmdq.getをモックして、コマンドが処理されるのを待つ
        mock_cmdq_get = mocker.patch.object(thread_worker._cmdq, "get")

        cmd = {"method": "sleep", "params": {"sec": 0.1}}
        thread_worker.send(cmd)
        # _wait_for_mock_callがmock_sleepを呼ばないように、
        # ダミーのsleep_funcを渡す
        self._wait_for_mock_call(
            mock_cmdq_get, sleep_func=lambda x: None
        )  # コマンドが処理されるのを待つ

        mock_sleep.assert_called_once_with(0.1)
        assert thread_worker.qsize == 0

    def test_clear_cmdq(self, thread_worker):
        """clear_cmdqのテスト"""
        cmd1 = {"method": "move", "params": {"angles": [0]}}
        cmd2 = {"method": "sleep", "params": {"sec": 0.1}}
        thread_worker.send(cmd1)
        thread_worker.send(cmd2)

        thread_worker.clear_cmdq()
        assert thread_worker.qsize == 0

    def test_send_cancel_command(self, thread_worker):
        """cancelコマンドのテスト"""
        cmd1 = {"method": "move", "params": {"angles": [0]}}
        cmd2 = {"method": "sleep", "params": {"sec": 0.1}}
        thread_worker.send(cmd1)
        thread_worker.send(cmd2)

        cmd_cancel = {"method": thread_worker.CMD_CANCEL}
        reply = thread_worker.send(cmd_cancel)

        assert reply["result"]["value"] == 2  # 2つのコマンドがクリアされた
        assert thread_worker.qsize == 0

    def test_send_qsize_command(self, thread_worker):
        """qsizeコマンドのテスト"""
        cmd1 = {"method": "move", "params": {"angles": [0]}}
        thread_worker.send(cmd1)

        cmd_qsize = {"method": thread_worker.CMD_QSIZE}
        reply = thread_worker.send(cmd_qsize)

        assert reply["result"]["value"] == 1
        assert thread_worker.qsize == 1

    def test_send_wait_command(self, thread_worker, mocker):
        """waitコマンドのテスト"""
        # _busy_flagとqsizeをモックして、waitコマンドの動作を制御する
        thread_worker._busy_flag = True
        mock_cmdq_qsize = mocker.patch.object(
            thread_worker._cmdq, "qsize", return_value=1
        )

        cmd_wait = {"method": thread_worker.CMD_WAIT}

        # 別スレッドでwaitコマンドを送信し、ブロックされることを確認
        send_thread = threading.Thread(
            target=thread_worker.send, args=(cmd_wait,)
        )
        send_thread.start()

        # waitコマンドがブロックされている間に、_busy_flagとqsizeを変更
        time.sleep(0.1)  # waitコマンドが実行されるのを待つ
        assert send_thread.is_alive()

        thread_worker._busy_flag = False
        mock_cmdq_qsize.return_value = 0  # qsizeを0に変更

        send_thread.join(timeout=1)  # waitコマンドが終了するのを待つ
        assert not send_thread.is_alive()

        # 最終的なqsizeが0であることを確認
        assert thread_worker.qsize == 0

    def test_send_error_key_command(self, thread_worker):
        """send()メソッドのエラーキーチェックのテスト"""
        cmd = {"error": "INVALID_JSON", "data": "some_data"}
        reply = thread_worker.send(cmd)

        assert (
            reply["error"]["code"] == thread_worker.ERROR_CODE["INVALID_JSON"]
        )
        assert reply["error"]["message"] == "INVALID_JSON"
        assert reply["error"]["data"] == "some_data"
        assert thread_worker.qsize == 0

    def test_run_method_error_handling(self, thread_worker, mocker):
        """run()メソッドのエラーハンドリングのテスト"""
        # エラーを発生させるハンドラをモック
        mocker.patch.object(
            thread_worker,
            "_handle_move_all_angles_sync",
            side_effect=ValueError("Test Error in Handler"),
        )
        mock_cmdq_get = mocker.patch.object(thread_worker._cmdq, "get")

        cmd = {"method": "move_all_angles_sync", "params": {"angles": [0]}}
        thread_worker.send(cmd)

        # エラーがログに記録されることを確認
        # （直接アサートは難しいが、ログ出力を確認）
        # ここでは、コマンドが処理され、キューが空になることを確認する
        self._wait_for_mock_call(
            mock_cmdq_get
        )  # コマンドが処理されるのを待つ

        assert thread_worker.qsize == 0
        # ログの確認はpytestのcaplogフィクスチャなどを使うが、ここでは省略

    def test_handle_move_all_angles_sync_relative(self, thread_worker):
        """_handle_move_all_angles_sync_relativeのテスト"""
        mservo_instance = thread_worker.mservo
        cmd = {
            "method": "move_all_angles_sync_relative",
            "params": {
                "angle_diffs": [10, -10],
                "move_sec": 0.1,
                "step_n": 10,
            },
        }
        thread_worker.send(cmd)
        self._wait_for_mock_call(
            mservo_instance.move_all_angles_sync_relative
        )

        mservo_instance.move_all_angles_sync_relative.assert_called_once_with(
            [10, -10], 0.1, 10
        )
        assert thread_worker.qsize == 0

    def test_handle_move_all_angles(self, thread_worker):
        """_handle_move_all_anglesのテスト"""
        mservo_instance = thread_worker.mservo
        cmd = {"method": "move_all_angles", "params": {"angles": [45, -45]}}
        thread_worker.send(cmd)
        self._wait_for_mock_call(mservo_instance.move_all_angles)

        assert thread_worker.qsize == 0

    def test_handle_move_all_pulses_relative(self, thread_worker):
        """_handle_move_all_pulses_relativeのテスト"""
        mservo_instance = thread_worker.mservo
        cmd = {
            "method": "move_all_pulses_relative",
            "params": {"pulse_diffs": [100, -100]},
        }
        thread_worker.send(cmd)
        self._wait_for_mock_call(mservo_instance.move_all_pulses_relative)

        assert thread_worker.qsize == 0

    def test_handle_move_sec(self, thread_worker, mocker):
        """_handle_move_secのテスト"""
        mock_cmdq_get = mocker.patch.object(thread_worker._cmdq, "get")
        cmd = {"method": "move_sec", "params": {"sec": 0.3}}
        thread_worker.send(cmd)
        self._wait_for_mock_call(
            mock_cmdq_get
        )  # コマンドが処理されるのを待つ

        assert thread_worker.qsize == 0

    def test_handle_step_n(self, thread_worker, mocker):
        """_handle_step_nのテスト"""
        mock_cmdq_get = mocker.patch.object(thread_worker._cmdq, "get")
        cmd = {"method": "step_n", "params": {"n": 50}}
        thread_worker.send(cmd)
        self._wait_for_mock_call(
            mock_cmdq_get
        )  # コマンドが処理されるのを待つ

        assert thread_worker.step_n == 50
        assert thread_worker.qsize == 0

    def test_busy_flag_logic(self, thread_worker, mocker):
        """_busy_flagのロジックのテスト"""
        mservo_instance = thread_worker.mservo

        # 初期状態ではbusy_flagはFalse
        assert thread_worker._busy_flag is False

        # コマンドを送信
        cmd = {"method": "move_all_angles", "params": {"angles": [0]}}
        thread_worker.send(cmd)

        # コマンド処理後、キューが空になったらbusy_flagはFalseに戻る
        self._wait_for_mock_call(mservo_instance.move_all_angles)
        assert thread_worker._busy_flag is False
        assert thread_worker.qsize == 0


    def test_command_order_and_processing(self, thread_worker, mocker): # mocker を追加
        """複数のコマンドが正しい順序で処理されることを検証"""
        mservo_instance = thread_worker.mservo
        cmd1 = {"method": "move_all_angles", "params": {"angles": [10]}}
        cmd2 = {"method": "move_all_angles", "params": {"angles": [20]}}
        cmd3 = {"method": "move_all_angles", "params": {"angles": [30]}}

        thread_worker.send(cmd1)
        thread_worker.send(cmd2)
        thread_worker.send(cmd3)

        self._wait_for_mock_call(mservo_instance.move_all_angles, timeout=2.0)
        self._wait_for_mock_call(mservo_instance.move_all_angles, timeout=2.0)
        self._wait_for_mock_call(mservo_instance.move_all_angles, timeout=2.0)

        # 呼び出し順序を検証
        mservo_instance.move_all_angles.assert_has_calls([
            mocker.call([10]),
            mocker.call([20]),
            mocker.call([30]),
        ])
        assert thread_worker.qsize == 0



    def test_error_logging(self, thread_worker, mocker):
        """エラーハンドリング時のログ出力のテスト"""
        mservo_instance = thread_worker.mservo
        error_message = "Mocked MServo error"
        mservo_instance.move_all_angles.side_effect = ValueError(error_message)
        
        # ThreadWorkerの内部ログオブジェクトをモック
        mock_log = mocker.patch.object(thread_worker, "_ThreadWorker__log")

        cmd = {"method": "move_all_angles", "params": {"angles": [0]}}
        thread_worker.send(cmd)

        # コマンドが処理されるまで待つ
        self._wait_for_mock_call(mservo_instance.move_all_angles, timeout=2.0)

        # エラーログが記録されたことを確認
        mock_log.error.assert_called_once()
        # ログメッセージが正しくフォーマットされていることを検証
        logged_message_format, *logged_args = mock_log.error.call_args[0]
        assert "ValueError" == logged_args[0]
        assert error_message in str(logged_args[1]) # ここを修正

    def test_wait_command_timeout(self, thread_worker, mocker):
        """waitコマンドのタイムアウトテスト"""
        thread_worker._busy_flag = True  # busy状態をシミュレート
        
        # _cmdq.putがブロックしないようにモック（実際はキューにコマンドを入れないので不要だが念のため）
        mocker.patch.object(thread_worker._cmdq, 'put')

        # send() がタイムアウトする場合
        cmd_wait_timeout = {"method": thread_worker.CMD_WAIT, "params": {"timeout": 0.05}} # タイムアウト時間を短く設定
        reply = thread_worker.send(cmd_wait_timeout)

        assert reply["error"]["code"] == thread_worker.ERROR_CODE["TIMEOUT"]
        assert "Timeout" in reply["error"]["message"]
        assert thread_worker.qsize == 0

    def test_send_queue_full(self, mocker_multiservo, mocker_pigpio, mocker):
        """キューが満杯の場合のsend()の挙動をテスト"""
        pi = mocker_pigpio()
        mocker_multiservo()
        # キューサイズを小さく設定
        worker = ThreadWorker(pi, PINS, maxqsize=1, debug=False)
        worker.start()

        cmd1 = {"method": "move_all_angles", "params": {"angles": [10]}}
        cmd2 = {"method": "move_all_angles", "params": {"angles": [20]}}

        worker.send(cmd1)  # 1つ目のコマンドでキューは満杯になる

        # 2つ目のコマンドを送信
        # ThreadWorkerのsend()はキューが満杯の場合、エラーを返す
        reply = worker.send(cmd2)

        assert reply["error"]["code"] == worker.ERROR_CODE["QUEUE_FULL"]
        assert "Queue full" in reply["error"]["message"]
        assert worker.qsize == 1  # 最初のコマンドだけがキューに残っている

        worker.end()



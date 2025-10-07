# Plan for `tests/test_07_threadworker.py` and `src/pi0servo/helper/thread_worker.py` Modifications

## 1. `src/pi0servo/helper/thread_worker.py` の修正 (Critical Bug Fix)

*   **問題点**: `_handle_move_all_angles_sync_relative` および `_handle_move_all_pulses_relative` メソッドが定義されているにもかかわらず、`_command_handlers` にマッピングされていないため、これらのコマンドが処理されない。
*   **修正内容**: `_command_handlers` ディクショナリに以下のエントリを追加する。
    ```python
    self._command_handlers = {
        # ... 既存のエントリ ...
        "move_all_angles_sync_relative": self._handle_move_all_angles_sync_relative,
        "move_all_pulses_relative": self._handle_move_all_pulses_relative,
    }
    ```
*   **関連する `_cmd_list` の修正**: `CMD_SAMPLES_ALL` にこれらのコマンドが含まれていないため、`_cmd_list` にも追加する必要がある。

## 2. `tests/test_07_threadworker.py` の修正 (テストの追加)

### 2.1. `send()` メソッド関連のテスト

*   **`CMD_CANCEL` コマンドのテスト**:
    *   `{"method": "cancel"}` を送信し、`clear_cmdq()` が呼び出され、適切な結果が返されることを確認する。
*   **`CMD_QSIZE` コマンドのテスト**:
    *   `{"method": "qsize"}` を送信し、現在のキューサイズが返されることを確認する。
*   **`CMD_WAIT` コマンドのテスト**:
    *   `{"method": "wait"}` を送信し、キューが空になり `_busy_flag` が `False` になるまでブロックすることを確認する。`_busy_flag` のモックが必要になる。
*   **`send()` メソッドのエラーキーチェック**:
    *   `{"error": "INVALID_JSON", "data": "some_data"}` のようなコマンドを送信し、`mk_reply_error` が適切に呼び出され、エラーが返されることを確認する。

### 2.2. `_handle_...` メソッド関連のテスト

*   **`_handle_move_all_angles_sync_relative` のテスト**:
    *   `{"method": "move_all_angles_sync_relative", "params": {"angle_diffs": [10, -10], "move_sec": 0.1, "step_n": 10}}` のようなコマンドを送信し、`mservo.move_all_angles_sync_relative` が正しい引数で呼び出されることを確認する。
*   **`_handle_move_all_angles` のテスト**:
    *   `{"method": "move_all_angles", "params": {"angles": [45, -45]}}` のようなコマンドを送信し、`mservo.move_all_angles` が正しい引数で呼び出されることを確認する。
*   **`_handle_move_all_pulses_relative` のテスト**:
    *   `{"method": "move_all_pulses_relative", "params": {"pulse_diffs": [100, -100]}}` のようなコマンドを送信し、`mservo.move_all_pulses_relative` が正しい引数で呼び出されることを確認する。
*   **`_handle_move_sec` のテスト**:
    *   `{"method": "move_sec", "params": {"sec": 0.3}}` を送信し、`thread_worker.move_sec` が正しく更新されることを確認する。
*   **`_handle_step_n` のテスト**:
    *   `{"method": "step_n", "params": {"n": 50}}` を送信し、`thread_worker.step_n` が正しく更新されることを確認する。
*   **`_handle_interval` のテスト**:
    *   `{"method": "interval", "params": {"sec": 0.1}}` を送信し、`thread_worker.interval_sec` が正しく更新されることを確認する。
*   **`_handle_sleep` のテスト**:
    *   `{"method": "sleep", "params": {"sec": 0.1}}` を送信し、`time.sleep` がモックされ、正しい引数で呼び出されることを確認する。

### 2.3. その他のテスト

*   **`run()` メソッドのエラーハンドリング**:
    *   `_dispatch_cmd` 内で例外が発生した場合に、`run()` がそれを捕捉し、ログに記録することを確認するテスト。
*   **`_busy_flag` のテスト**:
    *   コマンド処理中に `_busy_flag` が `True` になり、キューが空になると `False` に戻ることを確認するテスト。

## 3. 実施計画

1.  **`src/pi0servo/helper/thread_worker.py` の修正**: `_command_handlers` と `_cmd_list` に不足しているハンドラとコマンドを追加する。
2.  **`tests/test_07_threadworker.py` の修正**: 上記の「テストの追加」セクションでリストアップされたテストケースを実装する。
3.  **テストの実行と検証**: 全てのテストがパスすることを確認する。
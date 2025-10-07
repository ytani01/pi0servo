# Plan for `tests/test_06_str_cmd_to_json.py` Modifications

## 1. テストコードのシンプル化と可読性向上

*   **問題点**: `test_cmdstr_to_jsonliststr` の `expected_json_str` が非常に長く、可読性が低い。
*   **改善案**: `json.loads()` を使用して、期待されるJSON文字列をPythonのリスト/辞書オブジェクトに変換し、それに対してアサートを行う。これにより、テストコードが短くなり、期待される構造が視覚的に分かりやすくなる。
*   **実施内容**:
    1.  `tests/test_06_str_cmd_to_json.py` に `import json` を追加。
    2.  `test_cmdstr_to_jsonliststr` の `expected_json_str` を `expected_json_obj` に変更し、`json.loads()` でPythonオブジェクトに変換する。
    3.  `result = str_cmd_to_json_instance.cmdstr_to_jsonliststr(cmd_str)` の結果も `json.loads(result)` でPythonオブジェクトに変換し、`assert result_obj == expected_json_obj` で比較する。
    4.  同様に、`test_angle_factor_inversion`, `test_set_command_target_inversion`, `test_multiple_commands_in_line`, `test_multiple_commands_with_error` の `expected_json_str` もPythonオブジェクトに変換し、アサートを修正する。

## 2. テスト網羅性の向上 (足りないテストの追加)

### 2.1. `StrCmdToJson` クラスの初期化 (`__init__`)

*   **テスト内容**: `angle_factor` が空のリストの場合や `debug=False` の場合の初期化を検証する。
*   **追加テストケース**:
    *   `test_init_empty_angle_factor`
    *   `test_init_debug_false`

### 2.2. `angle_factor` プロパティ

*   **テスト内容**: 初期化後に `angle_factor` セッターが正しく機能するかを検証する。
*   **追加テストケース**:
    *   `test_angle_factor_setter`

### 2.3. `_create_error_data()` メソッド

*   **テスト内容**: エラーデータが期待通りに生成されるかを検証する。
*   **追加テストケース**:
    *   `test_create_error_data`

### 2.4. `_parse_angles()` メソッドのエッジケース

*   **テスト内容**: `angle_factor` の長さが角度の数と異なる場合や、不正な角度文字列のパースを検証する。
*   **追加テストケース**:
    *   `test_parse_angles_angle_factor_shorter`
    *   `test_parse_angles_angle_factor_longer`
    *   `test_parse_angles_empty_part` (e.g., "10,,20")

### 2.5. `cmdstr_to_json()` メソッドのエッジケース

*   **テスト内容**: 不正な `cmd_str` (スペースを含む、文字列ではない)、`angle_factor` の範囲外アクセス、負の `sec`、`n < 1` などのエラーハンドリングを検証する。
*   **追加テストケース**:
    *   `test_cmdstr_to_json_invalid_str_with_space`
    *   `test_cmdstr_to_json_not_string`
    *   `test_cmdstr_to_json_mp_index_error` (for `angle_factor` out of bounds)
    *   `test_cmdstr_to_json_set_index_error` (for `angle_factor` out of bounds)
    *   `test_cmdstr_to_json_negative_sec` (for `sl`, `ms`, `is`)
    *   `test_cmdstr_to_json_step_n_less_than_one`

### 2.6. `cmdstr_to_jsonlist()` メソッドのエッジケース

*   **テスト内容**: 空のコマンドラインの処理を検証する。
*   **追加テストケース**:
    *   `test_cmdstr_to_jsonlist_empty_line`

## 3. 実施計画

1.  **`tests/test_06_str_cmd_to_json.py` の修正**:
    *   `import json` を追加。
    *   `test_cmdstr_to_jsonliststr` および関連するテストの `expected_json_str` をPythonオブジェクトに変換し、アサートを修正する。
    *   上記「テスト網羅性の向上」でリストアップされた新しいテストケースを追加する。
2.  **テストの実行と検証**: 全てのテストがパスすることを確認する。
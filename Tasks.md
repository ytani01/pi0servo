# Tasks for renaming jsonstr to cmdstr_to_jsonliststr

- [ ] `src/pi0servo/helper/str_cmd_to_json.py` の `jsonstr` メソッドを `cmdstr_to_jsonliststr` にリネームします。
- [ ] `jsonstr` を呼び出している箇所を `cmdstr_to_jsonliststr` に修正します。
- [ ] リンターを実行して、コードスタイルをチェックします。
  - `ruff`: [ ]
  - `mypy`: [ ]
  - `pyright`: [ ]
  - `flake8`: [ ]
- [ ] テストを実行して、変更が問題ないことを確認します。テストが失敗したら、一旦作業を中断し、ユーザーに確認する。
- [ ] `Tasks.md` のタスクが完了したら、ユーザーに報告し、`ToDo.md` の次のタスクに進む。
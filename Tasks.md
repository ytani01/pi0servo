# ToDo: `hatch publish`時の403 Forbiddenエラーの解消

- [ ] `twine`を直接使用してアップロードを試み、問題を切り分ける
- [ ] OSの`keyring`機能がエラーの原因であることを特定する
- [ ] `.env`ファイルに`PYTHON_KEYRING_BACKEND`環境変数を設定し、`keyring`を無効化する
- [ ] `docs/PyPI.md`のドキュメントを更新し、`keyring`に関する設定を追記する
- [ ] `uv run hatch publish -r test`コマンドでTestPyPIへのアップロードが成功することを確認する

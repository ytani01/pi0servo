# PyPIへのパッケージ公開手順

本プロジェクトは `hatch` を使用して PyPI (Python Package Index) へ公開します。
公開には `uv run` を経由してコマンドを実行します。

## 1. 公開用トークンの準備

PyPI および TestPyPI のサイトで、プロジェクト専用のAPIトークンを事前に取得してください。

- [PyPI Account](https://pypi.org/manage/account/)
- [TestPyPI Account](https://test.pypi.org/manage/account/)

## 2. トークンの設定 (.env ファイル)

毎回コマンドラインでトークンを入力する手間を省くため、プロジェクトルートの `.env` ファイルでトークンを管理します。

1.  プロジェクトのルートにある `.env` ファイルに、`hatch`が公式にサポートする環境変数を設定します。

    - `PYTHON_KEYRING_BACKEND`: OSのパスワード管理機能(`keyring`)のエラーを回避するために設定します。
    - `HATCH_INDEX_USER`: ユーザー名を `__token__` に設定します。
    - `HATCH_INDEX_AUTH_TEST`: TestPyPI用のトークンを設定します。(`-r test` オプションに対応)
    - `HATCH_INDEX_AUTH`: 本番PyPI用のトークンを設定します。(デフォルトのPyPIに対応)

    ```bash
    # .env ファイルの中身の例
    export PYTHON_KEYRING_BACKEND="keyring.backends.null.Keyring"
    export HATCH_INDEX_USER="__token__"
    export HATCH_INDEX_AUTH_TEST="ここにTestPyPI用のトークンを貼り付け"
    export HATCH_INDEX_AUTH="ここにPyPI用のトークンを貼り付け"
    ```
    この `.env` ファイルは `.gitignore` に登録されているため、誤ってGitリポジトリに登録されることはありません。

2.  パッケージを公開する前に、ターミナルで以下のコマンドを実行し、環境変数を読み込みます。

    ```bash
    source .env
    ```

## 3. TestPyPIへのアップロード (テスト)

`.env` ファイルを読み込んだ後、以下のシンプルなコマンドでアップロードできます。

```bash
# TestPyPI へのアップロード
uv run hatch publish -r test -u __token__ -a $HATCH_INDEX_AUTH_TEST
```

アップロード後、TestPyPIのプロジェクトページで内容を確認し、`pip install -i https://test.pypi.org/simple/ pi0servo` でインストールできることを確認します。

## 4. PyPIへのアップロード (本番)

TestPyPIでの検証が完了したら、本番のPyPIへアップロードします。

```bash
# PyPI (本番) へのアップロード
uv run hatch publish
```

---
**注意:** トークンは機密情報です。Gitなどのバージョン管理に含めないように注意してください。
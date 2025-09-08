# PyPIへのパッケージ公開手順

本プロジェクトは `hatch` を使用して PyPI (Python Package Index) へ公開します。
公開には `uv run` を経由してコマンドを実行します。

## 1. 公開用トークンの準備

PyPI および TestPyPI のサイトで、プロジェクト用のAPIトークンを事前に取得してください。

- [PyPI Account](https://pypi.org/manage/account/)
- [TestPyPI Account](https://test.pypi.org/manage/account/)

## 2. トークンの設定 (.env ファイル)

毎回コマンドラインでトークンを入力する手間を省くため、プロジェクトルートの `.env` ファイルでトークンを管理します。

1.  プロジェクトのルートにある `.env` ファイルに、取得したトークンを記述します。

    ```bash
    # .env ファイルの中身
    export HATCH_TESTPYPI_TOKEN="ここにTestPyPI用のトークンを貼り付け"
    export HATCH_PYPI_TOKEN="ここにPyPI用のトークンを貼り付け"
    ```
    この `.env` ファイルは `.gitignore` に登録されているため、誤ってGitリポジトリに登録されることはありません。

2.  パッケージを公開する前に、ターミナルで以下のコマンドを実行し、環境変数を読み込みます。

    ```bash
    source .env
    ```
    これで、現在のターミナルセッションでトークンが環境変数として設定されます。

## 3. TestPyPIへのアップロード (テスト)

まず、TestPyPIへアップロードして、パッケージが正しく動作するか確認します。
`.env` ファイルを読み込んだ後、以下のコマンドを実行します。

```bash
# TestPyPI へのアップロード
uv run hatch publish -r testpypi
```

アップロード後、TestPyPIのプロジェクトページで内容を確認し、`pip install -i https://test.pypi.org/simple/ pi0servo` でインストールできることを確認します。

## 4. PyPIへのアップロード (本番)

TestPyPIでの検証が完了したら、本番のPyPIへアップロードします。
`.env` ファイルを読み込んだ後、以下のコマンドを実行します。

```bash
# PyPI (本番) へのアップロード
uv run hatch publish
```
(`-r` オプションがない場合、`pyproject.toml` の `[tool.hatch.publish.pypi]` で設定されたリポジトリ、つまりデフォルトのPyPIに公開されます)

---
**注意:** トークンは機密情報です。Gitなどのバージョン管理に含めないように注意してください。
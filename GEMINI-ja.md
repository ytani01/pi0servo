# GEMINI.md

開発ルール


## 1. 目的
- サーボ用 Python ドライバ
- **Raspberry Pi Zero 2W** など低スペックでも動作
- **pigpio** 使用
- ライブラリ利用 + CLIで確認・デモ可能


## 2. 全体ルール
- 安易に試行錯誤をせず、情報をしっかり調べること。
- **`git commit`はユーザーのみ**
- 必要時にコミット促し、1行英語メッセージ案を示す
- 設定管理は `uv`, `pyproject.toml` を使用（最新版仕様確認）
- コマンド実行: `uv run ...`
- ライブラリ追加: `uv add ...`
- リンティング:
  - `uv run ruff check ...`
  - `uv run mypy ...`
  - `uv run pyright ...`
- テスト: `tests/`以下に作成、実行は `uv run python -m pytest -v ...`
- ファイル更新は新規作成→差替え


## 3. コーディング
- コメントは日本語
- 行長 78文字以内
- ログは `my_logger.py` の `get_logger()`使用（変更禁止）


## 4. タスク管理: `ToDo.md` / `Tasks.md`
- `ToDo.md`: ユーザー専用
- `Tasks.md`: AI管理
- 作業前に必ず `Tasks.md` を作り、**実行確認 ('go ahead') を得るまで実行しない**

### 4.1 `Tasks.md` あり
- 未チェックタスクから順に実行
- コード変更時は lint / test 実施
- 完了タスクはチェック
- 追加タスクは追記後に確認 ('go ahead')
- 全完了後:
  1. `ToDo.md` チェック更新
  2. `uv run rename_task.py` 実行 → `Tasks.md` を `yyyymmdd-HHMM-Tasks-done.md` にリネームし `archives/`へ

### 4.2 `Tasks.md` なし
- `ToDo.md` を確認し、未チェックの先頭優先項目をタスク化
- 詳細に分解して `Tasks.md` 作成
- 必ず確認 ('go ahead') 後に実行

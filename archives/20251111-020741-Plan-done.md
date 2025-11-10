# Linting効率化計画

## 1. 現状のリンティングツール

`pyproject.toml`から、以下のリンティング関連ツールが開発依存関係として定義されています。

- `ruff`
- `mypy`
- `flake8`
- `isort`
- `pylint`
- `pyright`

`ruff`, `mypy`, `pyright` の設定が `pyproject.toml` 内に存在します。

## 2. 問題点

- **冗長性**: `flake8`, `isort`, `pylint` の機能の多くは `ruff` に統合されています。また、`mypy` と `pyright` という2つの型チェッカーが併存しています。
- **非効率**: 複数のツールを実行する必要があり、CI/CDやローカルでの開発サイクルが遅くなります。`ruff` はRust製で非常に高速であり、一本化することでパフォーマンスが大幅に向上します。

## 3. 提案

リンティングと型チェックのプロセスを効率化し、メンテナンスを容易にするために、以下の様にツールを整理・統一することを提案します。

### 3.1. 使用するツール

- **`ruff`**: 主要なリンター兼フォーマッターとして利用します。
- **`mypy`**: 静的型チェッカーとして利用します。

### 3.2. 廃止するツール

以下のツールは `ruff` と `mypy` で代替可能なため、依存関係から削除します。

- `flake8`
- `isort`
- `pylint`
- `pyright`

### 3.3. `ruff` の設定強化

現在の `ruff` の設定 (`lint.select = ["E", "F", "I"]`) は基本的なものに留まっています。これを拡張し、より多くの問題を検出できるようにします。

推奨されるルールセットの例:

```toml
[tool.ruff]
line-length = 78
target-version = "py311"

[tool.ruff.lint]
# E(pycodestyle Error), W(pycodestyle Warning), F(Pyflakes), I(isort),
# C90(mccabe complexity), B(flake8-bugbear), A(flake8-builtins),
# UP(pyupgrade), PT(flake8-pytest-style), SIM(flake8-simplify),
# S(flake8-bandit)
select = ["E", "F", "I", "W", "C90", "B", "A", "UP", "PT", "SIM", "S"]
ignore = []

exclude = [
    ".git",
    "__pycache__",
    "venv",
    "tests/data",
]

[tool.ruff.lint.per-file-ignores]
"conftest.py" = ["F401", "F811"]
"tests/*" = ["S101"] # assertの使用を許可

[tool.ruff.format]
docstring-code-line-length = 78
```

- `flake8-bugbear (B)`, `pyupgrade (UP)`, `flake8-simplify (SIM)` などの一般的なプラグインのルールを追加します。
- `flake8-bandit (S)` を追加することで、基本的なセキュリティチェックも `ruff` で行えるようになります。
- `flake8-pytest-style (PT)` を追加し、pytestのテストコードの品質を向上させます。

### 3.4. 実行コマンド

- **リンティング**: `uv run ruff check .`
- **フォーマット**: `uv run ruff format .`
- **型チェック**: `uv run mypy src/pi0servo tests`

## 4. 結論

上記提案により、リンティングツールが `ruff` と `mypy` に集約され、設定と実行がシンプルになります。また、`ruff` の高速性により、開発体験が向上します。

**注意**: この計画はツールの提案と設定の推奨に留まります。ソースコードや既存ファイルの編集は行いません。

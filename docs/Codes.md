# `src/pi0servo` ディレクトリの概要

`src/pi0servo` ディレクトリには、`pigpio` ライブラリを利用して Raspberry Pi Zero 2W 上でサーボを制御するためのコアロジックとインターフェースが含まれています。アーキテクチャはモジュール化されており、`core`、`command`、`helper`、`utils`、`web` の各サブディレクトリに機能が分離されています。

## 1. `core/` (コアサーボ制御ロジック)

サーボモーター制御の基本的な機能を提供します。

*   **`piservo.py`**: `pigpio` を使用して単一のサーボを制御するための最も基本的なクラス `PiServo` を提供します。パルス幅の設定とサーボのオン・オフを管理します。
*   **`calibrable_servo.py`**: `PiServo` を拡張し、キャリブレーション機能を追加した `CalibrableServo` クラスを提供します。最小、最大、中央のパルス幅を定義し、角度とパルス幅の相互変換を行います。キャリブレーションデータは `ServoConfigManager` を通じて永続化されます。
*   **`multi_servo.py`**: `CalibrableServo` のインスタンスを複数管理する `MultiServo` クラスを提供します。複数のサーボを同時に制御するためのメソッド（同期移動など）を提供します。

## 2. `command/` (コマンドラインインターフェース)

ユーザーがサーボを制御するための様々なコマンドラインインターフェースを提供します。

*   **`cmd_servo.py`**: `PiServo` を使用して、単一のサーボを直接制御するための基本的なCLIコマンド `servo` を実装します。
*   **`cmd_calib.py`**: `blessed` ライブラリを使用して、サーボを対話的にキャリブレーションするためのCUIアプリケーション `CalibApp` を実装します。
*   **`cmd_apicli.py`**: JSON形式のコマンドをローカルの `ThreadWorker` に送信し、`MultiServo` を直接制御するためのCLI `CmdApiCli` を実装します。
*   **`cmd_apiclient.py`**: リモートのAPIサーバーと通信するためのCLIクライアント `CmdApiClient` を実装します。`ApiClient` を使用してHTTP経由でJSONコマンドを送信します。
*   **`cmd_strcli.py`**: `cmd_apicli.py` を拡張し、人間が読みやすい文字列ベースのコマンドを受け付けます。コマンドは `StrCmdToJson` を使用してJSONに変換された後、ローカルの `ThreadWorker` に送信されます。
*   **`cmd_strclient.py`**: `cmd_apiclient.py` を拡張し、文字列ベースのコマンドを受け付けます。コマンドは `StrCmdToJson` を使用してJSONに変換された後、リモートのAPIサーバーに送信されます。
*   **`cmd_apiserver.py`**: `uvicorn` を使用して、FastAPIで実装されたJSON APIサーバーを起動する `CmdApiServer` を実装します。

## 3. `helper/` (ヘルパーユーティリティ)

非同期処理やコマンド変換など、制御を補助する機能を提供します。

*   **`str_cmd_to_json.py`**: "mv:40,30" のような人間が読みやすい文字列コマンドを、`ThreadWorker` が解釈できるJSON形式のコマンドに変換する `StrCmdToJson` クラスを提供します。
*   **`thread_worker.py`**: コマンドをキューで受け取り、別スレッドで順次実行する汎用的な `ThreadWorker` クラスを実装します。これにより、サーボの制御を非同期で行うことができます。
*   **`thread_multi_servo.py`**: `MultiServo` と `ThreadWorker` をラップし、複数のサーボを非同期で制御するための高レベルなインターフェース `ThreadMultiServo` を提供します。

## 4. `utils/` (汎用ユーティリティ)

設定管理などの汎用的な機能を提供します。

*   **`servo_config_manager.py`**: サーボのキャリブレーションデータをJSONファイルに読み書きするための `ServoConfigManager` クラスを提供します。設定ファイルは、カレントディレクトリ、ホームディレクトリ、`/etc/` の順で検索されます。

## 5. `web/` (Web API コンポーネント)

リモートからサーボを制御するためのWeb APIを提供します。

*   **`json_api.py`**: FastAPIを使用して、サーボを制御するためのJSON APIを実装します。`/cmd` エンドポイントでコマンドを受け付け、`ThreadWorker` を介してサーボを制御します。
*   **`api_client.py`**: `requests` ライブラリを使用して、Web APIにJSONコマンドをPOSTするための `ApiClient` クラスを提供します。

## `__main__.py` と `__init__.py`

*   **`__main__.py`**: `click` ライブラリを使用して、`command/` ディレクトリ内の各コマンドをサブコマンドとして持つCLIのエントリーポイントを定義します。
*   **`__init__.py`**: `pi0servo` パッケージの初期化ファイルです。主要なクラスをトップレベルに公開し、パッケージのバージョンを定義します。

## 全体的なアーキテクチャ

このプロジェクトは、関心事の分離の原則に基づいて、うまく構造化されています。

*   **低レベル制御**: `core/piservo.py` がハードウェアに最も近い層です。
*   **抽象化**: `core/calibrable_servo.py` と `core/multi_servo.py` が、単一および複数のサーボに対する抽象化を提供します。
*   **非同期処理**: `helper/thread_worker.py` と `helper/thread_multi_servo.py` が、ブロッキングしない非同期な制御を可能にしています。
*   **多様なインターフェース**: ユーザーは、単純な直接制御 (`cmd_servo`)、対話的なキャリブレーション (`cmd_calib`)、ローカルでのスクリプト実行 (`cmd_strcli`, `cmd_apicli`)、リモートでの制御 (`cmd_strclient`, `cmd_apiclient`, `web/json_api.py`) など、様々な方法でサーボを操作できます。
*   **コマンド変換**: `helper/str_cmd_to_json.py` が、ユーザーフレンドリーなコマンドと内部的なJSONフォーマットの間の便利な変換層を提供します。
*   **永続化**: `utils/servo_config_manager.py` がキャリブレーションデータの永続化を担当します。

このモジュール化された設計により、各コンポーネントの独立性が高まり、保守と拡張が容易になっています。
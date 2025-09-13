# Tasks.md

- [ ] **1. 共通初期化のための基底コンポーネントの導入**
    - [ ] `src/pi0servo/base/` ディレクトリを作成する。
    - [ ] `src/pi0servo/base/base_component.py` ファイルを作成し、`BaseComponent` クラスを定義する。
    - [ ] `BaseComponent` に `_debug` と `__log` の初期化ロジックを実装する。
    - [ ] `CmdApiClient`, `CalibApp`, `MultiServo`, `PiServo`, `CalibrableServo`, `StrCmdToJson`, `ThreadWorker`, `JsonApi`, `ApiClient`, `ServoConfigManager` を `BaseComponent` を継承するように修正する。
    - [ ] 各クラスから冗長な `_debug` と `__log` の初期化コードを削除する。

- [ ] **2. インターフェース/ABC を使用したコンポーネントの分離**
    - [ ] `src/pi0servo/interfaces/` ディレクトリを作成する。
    - [ ] `src/pi0servo/interfaces/i_servo_controller.py` を作成し、`IServoController` ABC を定義する。
    - [ ] `src/pi0servo/interfaces/i_command_executor.py` を作成し、`ICommandExecutor` ABC を定義する。
    - [ ] `MultiServo` が `IServoController` を実装するように修正する。
    - [ ] `ThreadWorker` が `ICommandExecutor` を実装するように修正する。
    - [ ] `JsonApi` のコンストラクタを修正し、`IServoController` と `ICommandExecutor` のインスタンスを依存性注入で受け入れるようにする。
    - [ ] `ThreadMultiServo` のコンストラクタを修正し、`IServoController` と `ICommandExecutor` のインスタンスを依存性注入で受け入れるようにする。

- [ ] **3. Enum を使用したコマンド処理の強化**
    - [ ] `src/pi0servo/enums/` ディレクトリを作成する。
    - [ ] `src/pi0servo/enums/command_type.py` を作成し、`CommandType` Enum を定義する。
    - [ ] `src/pi0servo/enums/angle_alias.py` を作成し、`AngleAlias` Enum を定義する。
    - [ ] `src/pi0servo/enums/set_target.py` を作成し、`SetTarget` Enum を定義する。
    - [ ] `StrCmdToJson` を修正し、`COMMAND_MAP`, `ANGLE_ALIAS_MAP`, `SET_TARGET` でこれらの Enum を使用するようにする。
    - [ ] `ThreadWorker` の `_command_handlers` を修正し、`CommandType` Enum を使用するようにする。

- [ ] **4. エラー報告の標準化**
    - [ ] 標準化されたエラー構造を定義する (例: `error_code`, `message`, `details` を持つ辞書)。
    - [ ] `StrCmdToJson` の `_create_error_data` を修正し、この標準化されたエラー構造を返すようにする。
    - [ ] `JsonApi` と `ThreadWorker` が詳細なエラーメッセージを伝播するように修正する。

- [ ] **5. `MultiServo` の明示的な API の改善**
    - [ ] `MultiServo` で `CalibrableServo` インスタンスに委譲するすべてのパブリックメソッドを明示的に定義する。
    - [ ] `MultiServo` から `__getattr__` を削除する。

- [ ] **6. `ServoConfigManager` の柔軟性の向上**
    - [ ] `ServoConfigManager` のコンストラクタに、設定ファイルのカスタム検索パスを指定できるようにする引数を追加する。
    - [ ] `_find_conf_file` を修正し、提供されたパスをハードコードされたデフォルトよりも優先するようにする。

- [ ] **7. `sample_json.js` の再配置**
    - [ ] `src/pi0servo/web/sample_json.js` を `docs/samples/` ディレクトリに移動する。

- [ ] **8. `pigpio` 相互作用のカプセル化**
    - [ ] `src/pi0servo/drivers/` ディレクトリを作成する。
    - [ ] `src/pi0servo/drivers/pigpio_client.py` を作成し、`PigpioClient` クラスを定義する。
    - [ ] `PigpioClient` に `pigpio.pi()` インスタンスをラップし、抽象的なインターフェースを提供する。
    - [ ] `PiServo` および `MultiServo` を修正し、`PigpioClient` インスタンスを受け入れるようにする。

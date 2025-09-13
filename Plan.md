# pi0servo リファクタリング計画

## 1. 特定された問題点

1.  **密結合と抽象化の欠如:**
    *   `JsonApi` と `ThreadMultiServo` は、`MultiServo` と `ThreadWorker` の具体的な実装に密結合しています。
    *   これにより、テスト容易性と柔軟性が損なわれています。

2.  **冗長な初期化:**
    *   複数のクラスで `_debug` と `__log` の初期化が繰り返されています。

3.  **コマンド処理におけるマジック文字列:**
    *   `StrCmdToJson` と `ThreadWorker` は文字列ベースのコマンドマッピングに依存しており、潜在的な不整合と型安全性の低下につながっています。

4.  **基本的なエラー処理:**
    *   `StrCmdToJson` は詳細なエラー情報に欠ける単純な `{"err": strcmd}` を返します。

5.  **`MultiServo` の暗黙的な API:**
    *   `MultiServo` は `__getattr__` を使用して呼び出しを委譲しており、その公開 API が不明確で、潜在的にエラーが発生しやすくなっています。

6.  **設定パスのハードコーディング:**
    *   `ServoConfigManager` は設定ファイルの検索パスをハードコーディングしており、柔軟性が制限されています。

7.  **型ヒントの不整合:**
    *   `JsonApi` の `exec_cmd` のような一部の領域では、より正確な型ヒントが望まれます。

8.  **`pigpio` インスタンスの直接使用:**
    *   `pigpio.pi()` インスタンスの直接渡しは、さらに抽象化することができます。

9.  **`sample_json.js` の配置ミス:**
    *   JavaScript のサンプルファイルが Python のソースディレクトリ内に配置されています。

## 2. 提案される改善点

1.  **共通初期化のための基底コンポーネントの導入:**
    *   共通の `_debug` と `__log` の初期化を処理する `BaseComponent` クラスを (例: `src/pi0servo/base/` または `src/pi0servo/utils/` に) 作成します。
    *   関連するすべてのクラスは `BaseComponent` を継承します。

2.  **インターフェース/ABC を使用したコンポーネントの分離:**
    *   `MultiServo` (例: `IServoController`) と `ThreadWorker` (例: `ICommandExecutor`) の抽象基底クラス (ABC) またはインターフェースを定義します。
    *   依存性注入を使用して、これらの依存関係を `JsonApi` と `ThreadMultiServo` に提供します。

3.  **Enum を使用したコマンド処理の強化:**
    *   コマンド名、角度エイリアス、および `set` ターゲットの Python `Enum` クラスを導入します。
    *   型安全性と可読性を向上させるために、`StrCmdToJson` と `ThreadWorker` を更新してこれらの Enum を使用するようにします。

4.  **エラー報告の標準化:**
    *   一貫したエラー構造 (例: `error_code`、`message`、`details`) を実装します。
    *   `StrCmdToJson` を変更して、この標準化されたエラー構造を返すようにします。

5.  **`MultiServo` の明示的な API の改善:**
    *   `MultiServo` で `CalibrableServo` インスタンスに委譲するすべてのパブリックメソッドを明示的に定義します。
    *   パブリック API メソッドに `__getattr__` を使用することを削除または慎重に再検討します。

6.  **`ServoConfigManager` の柔軟性の向上:**
    *   `ServoConfigManager` のコンストラクタに、設定ファイルのカスタム検索パスを指定できるようにする引数を追加します。

7.  **`sample_json.js` の再配置:**
    *   `src/pi0servo/web/sample_json.js` を `docs/samples/` または `examples/` に移動します。

8.  **`pigpio` 相互作用のカプセル化:**
    *   `pigpio.pi()` インスタンスをラップし、より抽象的なインターフェースを提供する `PigpioClient` クラスの作成を検討します。

この計画は、`pi0servo` コードベースのモジュール性、保守性、および堅牢性を向上させることを目的としています。
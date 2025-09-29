### `ThreadWorker` で使用可能なJSONコマンドパターン

`ThreadWorker`は、
JSON形式の文字列またはPythonの辞書オブジェクトを
コマンドとしてキューを介して受け取ります。
各コマンドの基本的な構造は 
`{"method": "コマンド名", "params": {...}}` です。

**重要**
"method","params"については、JSON-RPCのフォーマットに従います。


以下に、利用可能なコマンドとそのJSONサンプルを示します。

#### 1. サーボの同期移動

複数のサーボを指定した時間をかけて同期的に目標角度へ移動させます。

- **コマンド**: `move` または `move_all_angles_sync`
- **説明**: `move`は`move_all_angles_sync`の省略形です。`angles`配列で各サーボの目標角度を指定します。配列の要素に`None`を指定すると、そのサーボは現在の位置を維持します。

**基本形**
```json
{
  "method": "move",
  "params": {
    "angles": [30, -30, 0, 90]
  }
}
```

**オプション付き（移動時間とステップ数を指定）**
```json
{
  "method": "move_all_angles_sync",
  "params": {
    "angles": [45, null, "center", -45],
    "move_sec": 0.5,
    "step_n": 50
  }
}
```
* `angles`内の `null` は `None` と同じ意味です。`"center"` のような文字列も使用できます。

---

#### 2. サーボの個別移動（非同期）

各サーボを即座に指定の角度またはパルス幅へ移動させます。

- **コマンド**: `move_all_angles`
- **説明**: 各サーボを即座に指定の角度に移動させます。

```json
{
  "method": "move_all_angles",
  "params": {
    "angles": [-90, 90, null, 0]
  }
}
```

- **コマンド**: `move_all_pulses`
- **説明**: 各サーボを即座に指定のパルス幅に移動させます。`0`を指定するとサーボはオフになります。

```json
{
  "method": "move_all_pulses",
  "params": {"pulses": [500, 2500, 1500, 0]}
}
```

---

#### 3. 動作パラメータの設定

同期移動 (`move`/`move_all_angles_sync`) のデフォルト動作や、コマンド間のインターバルを設定します。

- **コマンド**: `move_sec`
- **説明**: 同期移動のデフォルトの移動時間を秒単位で設定します。

```json
{
  "method": "move_sec",
  "params": {"sec": 0.8}
}
```

- **コマンド**: `step_n`
- **説明**: 同期移動のデフォルトのステップ数を設定します。

```json
{
  "method": "step_n",
  "params": {"n": 100}
}
```

- **コマンド**: `interval`
- **説明**: 各移動コマンドの実行後に挿入される待機時間（インターバル）を秒単位で設定します。

```json
{
  "method": "interval",
  "params": {"sec": 0.5}
}
```

---

#### 4. 制御コマンド

コマンドキューの制御や、処理の一時停止を行います。

- **コマンド**: `sleep`
- **説明**: 指定した時間、処理を一時停止します。

```json
{
  "method": "sleep",
  "params": {"sec": 2.0}
}
```

- **コマンド**: `cancel`
- **説明**: コマンドキューに溜まっている未実行のコマンドをすべてクリアします。

```json
{
  "method": "cancel"
}
```

---

#### 5. キャリブレーション設定の保存

位置の調整

- **コマンド**: `move_pulse_relative`
- **説明**: 特定のサーボを相対的に動かす。キャリブレーション位置の調整用。

```json
{
  "method": "move_pulse_relative",
  "params": {
    "servo": 0,
    "pulse_diff": -20
  }
}
```

現在のパルス値を 'center' | 'min' | 'max' として保存。

- **コマンド**: `set`
- **説明**: 特定のサーボのキャリブレーション値を設定します。

**中央位置(center)の設定**
```json
{
  "method": "set",
  "params": {
    "servo": 0,
    "target": "center"
  }
}
```

**最小位置(min)の設定**
```json
{
  "method": "set",
  "params": {
    "servo": 1,
    "target": "min"
  }
}
```

**最大位置(max)の設定**
```json
{
  "method": "set",
  "params" {
    "servo": 2,
    "target": "max"
  }
}
```

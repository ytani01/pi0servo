# str_to_json

## 書式

def str_to_json(cmdstr: str): -> str

## 機能

コマンド文字列`cmdstr`を以下の例に基づいて、JSON文字列に変換する。

## 基本ルール

- 先頭の2文字は、コマンド種別

- コマンドとパラメータの間の区切り文字は、':'

- ':'以降は、コマンド毎に異なるパラメータ

- コマンド文字列の途中に空白文字は入ってはならない。

- 変換できない場合は、以下を返す。
  '{"err": **元のコマンド文字列**}'

- コマンドの種類は以下の通り
  - 'mv': {"method": "move_all_angles_sync"}
  - 'mr': {"method": "move_all_angles_sync_relative"}
  - 'sl': {"method": "sleep"}
  - 'ms': {"method": "move_sec"}
  - 'st': {"method": "step_n"}
  - 'is': {"method": "interval"}
  - 'mp': {"method": "move_pulse_relative"}
  - 'sc': {"method": "set"}  # set center
  - 'sn': {"method": "set"}  # set min
  - 'sx': {"method": "set"}  # set max
  - 'ca': {"method": "cancel"}
  - 'zz': {"method": "cancel"}
  - 'qs': {"method": "qsize"}
  - 'qq': {"method": "qsize"}
  - 'wa': {"method": "wait"}
  - 'ww': {"method": "wait"}

## 補足ルール

- angles: list[float]: -90 <= angle <= 90
- sec: float: > 0
- n: int: > 1

### angles

'.', null(None): 動かさない
"min","n": -90.0
"max","x": 90.0
"center","c": 0.0

## 例

入力: 'mv:40,30,20,10'
出力: '{"method": "move_all_angles_sync", "params": {"angles": [40,30,20,10]}}'

入力: 'mv:-40,.,.'
出力: '{"method": "move_all_angles_sync", "params": {"angles": [-40,null,null]}}'

入力: 'mv:max,min,center'
出力: '{"method": "move_all_angles_sync", "params": {"angles": ["max","min","center"]}}'

入力: 'mv:x,n,c'
出力: '{"method": "move_all_angles_sync", "params": {"angles": ["max","min","center"]}}'

入力: 'mv:x,.,center,20'
出力: '{"method": "move_all_angles_sync", "params": {"angles": ["max",null,"center",20]}}'

入力: 'mr:-10,0,0,10'
出力: '{"method": "move_all_angles_sync_relative", "params": {"angle-diffs": [-10,0,0,10]}}'

入力: 'sl:0.5'
出力: '{"method": "sleep", "params": {"sec": 0.5}}'

入力: 'sl:1'
出力: '{"method": "sleep", "params": {"sec": 1}}'

入力: 'ms:1.5'
出力: '{"method": "move_sec", "params": {"sec": 1.5}}'

入力: 'st:1'
出力: '{"method": "step_n", "params": {"n": 1}}'

入力: 'st:40'
出力: '{"method": "step_n", "params": {"n": 40}}'

入力: 'is:0.5'
出力: '{"method": "interval", "params": {"sec": 0.5}}'

入力: 'mp:2,-20'
出力: '{"method": "move_pulse_relative", "params": {"servo_i": 2, "pulse_diff": -20}}'

入力: 'sc:1'
出力: '{"method": "set", "params": {"servo_i": 1, "target": "center"}}'

入力: 'sn:2'
出力: '{"method": "set", "params": {"servo_i": 2, "target": "min"}}'

入力: 'sx:0'
出力: '{"method": "set", "params": {"servo_i": 0, "target": "max"}}'

入力: 'ca'
出力: '{"method": "cancel"}

入力: 'zz'
出力: '{"method": "cancel"}

入力: 'qs'
出力: '{"method": "qsize"}

入力: 'qq'
出力: '{"method": "qsize"}

入力: 'wa'
出力: '{"method": "wait"}

入力: 'ww'
出力: '{"method": "wait"}

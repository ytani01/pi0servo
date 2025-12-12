# Command string to JSON-RPC request data

## 文字列コマンドの基本ルール

- 先頭の2文字は、コマンド種別

- コマンドとパラメータの間の区切り文字は、':'

- コマンド文字列の途中に空白文字は入ってはならない。

- 変換できない場合は、以下を返す。
  {"method": "ERROR", "error": error_message, "data": strcmd}

- コマンドの種類は以下の通り
  - 'mv': {"method": "move_all_angles_sync"}
  - 'mr': {"method": "move_all_angles_sync_relative"}
  - 'sl': {"method": "sleep"}
  - 'ms': {"method": "move_sec"}
  - 'st': {"method": "step_n"}
  - 'is': {"method": "interval"}
  - 'mp': {"method": "move_pulse_relative"}

  - 'cb': {"method": "calibration"}

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

- "angles"の数値は、-90以上、90以下
- "sec"の値は、0以上のfloat
- "n"の値は、1以上のint

## 例

cmd: 'mv:40,30,20,10'
json: '{"method": "move_all_angles_sync", "params": {"angles": [40,30,20,10]}}'

cmd: 'mv:-40,.,.'
json: '{"method": "move_all_angles_sync", "params": {"angles": [-40,null,null]}}'

cmd: 'mv:max,min,center'
json: '{"method": "move_all_angles_sync", "params": {"angles": ["max","min","center"]}}'

cmd: 'mv:x,n,c'
json: '{"method": "move_all_angles_sync", "params": {"angles": ["max","min","center"]}}'

cmd: 'mv:x,.,center,20'
json: '{"method": "move_all_angles_sync", "params": {"angles": ["max",null,"center",20]}}'

cmd: 'mr:-10,0,0,10'
json: '{"method": "move_all_angles_sync_relative", "params": {"angle-diffs": [-10,0,0,10]}}'

cmd: 'sl:0.5'
json: '{"method": "sleep", "params": {"sec": 0.5}}'

cmd: 'sl:1'
json: '{"method": "sleep", "params": {"sec": 1}}'

cmd: 'ms:1.5'
json: '{"method": "move_sec", "params": {"sec": 1.5}}'

cmd: 'st:1'
json: '{"method": "step_n", "params": {"n": 1}}'

cmd: 'st:40'
json: '{"method": "step_n", "params": {"n": 40}}'

cmd: 'is:0.5'
json: '{"method": "interval", "params": {"sec": 0.5}}'

cmd: 'mp:2,-20'
json: '{"method": "move_pulse_relative", "params": {"servo_i": 2, "pulse_diff": -20}}'

cmd: 'cb:0,c'
json: '{"method": "set", "params": {"servo_i": 0, "target": "center", "pulse": None}}

cmd: 'cb:1,n,1500'
json: '{"method": "set", "params": {"servo_i": 1, "target": "min", "pulse": 1500}}

<!-- cmd: 'sc:1,1500' -->
<!-- json: '{"method": "set", "params": {"servo_i": 1, "target": "center", "pulse": 1500}}' -->

<!-- cmd: 'sn:2,500' -->
<!-- json: '{"method": "set", "params": {"servo_i": 2, "target": "min", "pulse": 500}}' -->

<!-- cmd: 'sx:0,2500' -->
<!-- json: '{"method": "set", "params": {"servo_i": 0, "target": "max", "pulse": 2500}}' -->

cmd: 'ca'
json: '{"method": "cancel"}

cmd: 'zz'
json: '{"method": "cancel"}

cmd: 'qs'
json: '{"method": "qsize"}

cmd: 'qq'
json: '{"method": "qsize"}

cmd: 'wa'
json: '{"method": "wait"}

cmd: 'ww'
json: '{"method": "wait"}

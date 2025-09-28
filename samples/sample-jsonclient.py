#
# JSONクライアントのサンプルプログラム
#
import json

from pi0servo import ApiClient

DEBUG_FLAG = False

URL = "http://localhost:8000/cmd"
print(f"* URL = {URL}\n")


# API Client オブジェクト生成
sv = ApiClient(URL, debug=DEBUG_FLAG)


print("* JSONコマンド: 配列で複数一括送信可能")
cmd_json = [
    {"method": "move", "params": {"angles": [30, -30]}},
    {"method": "mova", "params": {"angles": [0, 0]}},  # invalid method
    #{"method": "move", "params": {"angles": [100,100]}},  # invalid angles
    {"method": "move"},
    {"method": "move", "params": {"angles": [0, 0]}},
]
print(f"cmd_json = {cmd_json}\n")


print("* 配列をそのまま送る")
print(f">>> {cmd_json}")
result = sv.post(json.dumps(cmd_json))  # 送信
result_json = sv.get_result_json(result)  # 返信の解読
print(f"<<< {result_json}\n")


print("* 配列要素を一つずつ送る")
for cmd in cmd_json:
    print(f">>> {cmd}")
    result = sv.post(json.dumps(cmd))
    result_json = sv.get_result_json(result)
    print(f"<<< {result_json}\n")

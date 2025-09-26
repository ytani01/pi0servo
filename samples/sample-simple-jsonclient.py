#
# JSONクリアンとのサンプルプログラム
#
import json

from pi0servo import ApiClient

DEBUG_FLAG = False

URL = "http://localhost:8000/cmd"
print(f"* URL = {URL}\n")


# API Client オブジェクト生成
sv = ApiClient(URL, debug=DEBUG_FLAG)


print("* JSONコマンド: 配列で複数可能")
cmd_json = [
    {"cmd": "move", "angles": [30, -30]},
    {"cmd": "move", "angles": [0, 0]},
]
print(f"cmd_json = {cmd_json}\n")

print("* 配列をそのまま送る")
result = sv.post(json.dumps(cmd_json))
result_json = sv.get_result_json(result)
print(f"result = {result_json}\n")


print("* 配列要素を一つずつ送る")
for j in cmd_json:
    print(f"- j = {j}")
    result = sv.post(json.dumps(j))
    result_json = sv.get_result_json(result)
    print(f"  result = {result_json}")

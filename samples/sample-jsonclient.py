#
# JSONクライアントのサンプルプログラム
#
from pi0servo import ApiClient

DEBUG_FLAG = False

URL = "http://localhost:8000/cmd"
print(f"* URL = {URL}\n")


# API Client オブジェクト生成
api_client = ApiClient(URL, debug=DEBUG_FLAG)

print("* JSONコマンド: 配列で複数一括送信可能")
cmd_json_list = [
    {"method": "move", "params": {"angles": [10, -10]}},
    {"method": "mova", "params": {"angles": [0, 0]}},  # invalid command
    {"method": "move"},  # サーバー側でエラー
    {"method": "sleep", "params": {"sec": 1.0}},
    {"method": "move", "params": {"angles": [0, 0]}},
    {"method": "wait"},  # サーバー側の動作が完了するまで待つ
]
print(f"cmd_json_list = {cmd_json_list}\n")

print("* 配列要素を一つずつ送る")
for cmd in cmd_json_list:
    print(f">>> {cmd}")
    result_json = api_client.post(cmd)
    print(f"  <<< {result_json}")
print()

print("* 配列をそのまま送る")
print(f">>> {cmd_json_list}")

result_json_list = api_client.post(cmd_json_list)
for result_json in result_json_list:
    print(f"  <<< {result_json}")
print()

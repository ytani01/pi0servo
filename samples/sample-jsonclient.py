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
cmd_json = [
    {"method": "move", "params": {"angles": [30, -30]}},
    {"method": "mova", "params": {"angles": [0, 0]}},  # invalid method
    # {"method": "move", "params": {"angles": [100,100]}},  # invalid angles
    {"method": "move"},
    {"method": "move", "params": {"angles": [0, 0]}},
]
print(f"cmd_json = {cmd_json}\n")


print("* 配列をそのまま送る")
print(f">>> {cmd_json}")
result_json = api_client.post(cmd_json)
print(f"   <<< {result_json}\n")


print("* 配列要素を一つずつ送る")
for cmd in cmd_json:
    print(f">>> {cmd}")
    result_json = api_client.post(cmd)
    print(f"   <<< {result_json}\n")

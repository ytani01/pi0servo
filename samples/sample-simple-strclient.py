#
# strクライントのサンプルプログラム
#
from pi0servo import ApiClient, StrCmdToJson

DEBUG_FLAG = False

URL = "http://localhost:8000/cmd"
print(f"* URL = {URL}\n")


# API Client オブジェクト生成
sv = ApiClient(URL, debug=DEBUG_FLAG)
s2j = StrCmdToJson(angle_factor=[1, -1], debug=DEBUG_FLAG)

print("* JSONコマンド: 配列で複数一括送信可能")
strcmds = [
    "mv:30,-30",
    "mv:0,0",
    "mv:-30,30 mv:0,0",
]
print(f"strcmds = {strcmds}")

for cmd in strcmds:
    print(f">>> {cmd}")
    jsoncmd = s2j.cmdstr_to_jsonliststr(cmd)
    print(f" jsoncmd={jsoncmd}")
    result = sv.post(jsoncmd)
    result_json = sv.get_result_json(result)
    print(f"<<< {result_json}\n")

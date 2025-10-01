#
# strクライントのサンプルプログラム
#
from pi0servo import ApiClient, StrCmdToJson

DEBUG_FLAG = False

URL = "http://localhost:8000/cmd"
print(f"* URL = {URL}\n")


# API Client オブジェクト生成
api_client = ApiClient(URL, debug=DEBUG_FLAG)
parser = StrCmdToJson(angle_factor=[1, -1], debug=DEBUG_FLAG)

str_cmds = [
    "mv:30,-30",
    "mv:0,0",
    "mv:-30,30 mv:0,0",
    "ww"
]
print(f"strcmds = {str_cmds}")


print("# 個別送信")
for cmd in str_cmds:
    print(f">>> {cmd}")

    jsoncmd = parser.cmdstr_to_jsonlist(cmd)
    print(f" jsoncmd={jsoncmd}")

    result_json = api_client.post(jsoncmd)
    print(f"   <<< {result_json}\n")


print("# 一括送信")
cmdline = " ".join(str_cmds)
print(f">>> {cmdline}")

cmdjson = parser.cmdstr_to_jsonlist(cmdline)
print(f"cmdjson={cmdjson}")

result_json = api_client.post(cmdjson)
print(f"   <<< {result_json}\n")

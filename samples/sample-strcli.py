#
# strクライントのサンプルプログラム
#
import sys

import pigpio

from pi0servo import MultiServo, StrCmdToJson, ThreadWorker

DEBUG_FLAG = {
    "parser": False,
    "mservo": False,
    "thr_worker": False,
}

PINS = [25, 27]
ANGLE_FACTOR = [1, -1]

#
# **重要**
#
# コマンドは、非同期に実行されるため、
# 最後に、waitコマンド "ww" を入れないと、
# 動作完了前に、プログラムが終了してしまい、実行中にキャンセルされてしまう。
#
STR_CMDS = ["mv:30,-30", "mv:0,0", "mv:-30,30 mv:0,0", "ww"]
print(f"STR_CMDS = {STR_CMDS}")


def exec_one_string_command(strcmd: str):
    """Execute one string command"""


pi = None
mservo = None
try:
    pi = pigpio.pi()
    if not pi.connected:
        sys.exit(1)

    parser = StrCmdToJson(
        angle_factor=ANGLE_FACTOR, debug=DEBUG_FLAG["parser"]
    )
    mservo = MultiServo(pi, PINS, debug=DEBUG_FLAG["mservo"])

    with ThreadWorker(mservo, debug=DEBUG_FLAG["thr_worker"]) as thr_worker:
        for strcmd in STR_CMDS:
            print(f"strcmd = {strcmd}")

            jsoncmdlist = parser.cmdstr_to_jsonlist(strcmd)
            print(f"  jsoncmdlist = {jsoncmdlist}")

            for jsoncmd in jsoncmdlist:
                print(f"    jsoncmd = {jsoncmd}")

                ret = thr_worker.send(jsoncmd)
                print(f"      ret = {ret}")

finally:
    if mservo:
        mservo.off()
    if pi and pi.connected:
        pi.stop()

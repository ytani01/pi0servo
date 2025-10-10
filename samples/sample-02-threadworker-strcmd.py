import pigpio

from pi0servo import StrCmdToJson, ThreadWorker

PINS = [25, 27]
ANGLE_FACTOR = [1, -1]

STR_CMDS = [
    "is:0.3",
    "mv:10,10",
    "mr:10,-10",
    "mv:0,0",
    "is:0 mp:0,100 mp:1,-100 sl:0.5",  # "mp"のあとは、sleep 0.5s程度必要
    "ms:0.2 mv:0,0",
    "wa",  # workerスレッドのすべての動作が完了するまで待つ
]

DEBUG_FLAG = {
    "servo": False,
    "parser": False,
    "worker": False,
}


def main():
    """main"""
    print("START")
    pi = None
    servo = None
    worker = None
    try:
        pi = pigpio.pi()
        parser = StrCmdToJson(
            angle_factor=ANGLE_FACTOR, debug=DEBUG_FLAG["parser"]
        )
        with ThreadWorker(pi, PINS, debug=DEBUG_FLAG["worker"]) as worker:
            for _strcmd in STR_CMDS:
                print(f">>> {_strcmd}")

                _jsoncmdlist = parser.cmdstr_to_jsonlist(_strcmd)
                print(f"  >>> {_jsoncmdlist}")

                for _jsoncmd in _jsoncmdlist:
                    print(f"    >>> {_jsoncmd}")

                    result = worker.send(_jsoncmd)
                    print(f"    <<< {result}")
                    print()

    finally:  # 必ず実行される: 異常終了時でも、適切に終了処理を行う
        if servo:
            servo.off()
        if pi:
            pi.stop()
        print("END")


if __name__ == "__main__":
    main()

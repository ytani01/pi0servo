import pigpio

from pi0servo import MultiServo, StrCmdToJson, ThreadWorker

PINS = [25, 27]
DEBUG_FLAG = False

STR_CMDS = [
    "ms:0.5",
    "mv:45,45",
    "mv:0,0",
    "sl:2.0",
    "mv:45,-45",
    "mv:0,0",
    "ms:0.2",
    "mv:-45,45",
    "mv:0,0",
    "mv:-45,-45",
    "mv:0,0",
    "wa",  # workerスレッドのすべての動作が完了するまで待つ
]


def main():
    """main"""
    print("START")

    # pigpioの初期化
    pi = pigpio.pi()
    if not pi.connected:
        print("ERROR: pigpio connection")
        return

    servo = None
    worker = None
    try:
        # オブジェクトの初期化
        servo = MultiServo(pi, PINS, debug=DEBUG_FLAG)
        worker = ThreadWorker(servo, debug=DEBUG_FLAG)
        parser = StrCmdToJson(angle_factor=[1, -1], debug=DEBUG_FLAG)

        worker.start()  # ワーカースレッドを裏で動かす

        # コマンド呼び出し
        for _strcmd in STR_CMDS:
            _jsoncmd = parser.cmdstr_to_json(_strcmd)  # JSONに翻訳
            print(f">>> {_strcmd} = {_jsoncmd}")
            result = worker.send(_jsoncmd)
            print(f"  <<< {result}\n")

    finally:  # 必ず実行される: 異常終了時でも、適切に終了処理を行う
        if worker:
            worker.end()
        if servo:
            servo.off()
        if pi:
            pi.stop()
        print("END")


if __name__ == "__main__":
    main()

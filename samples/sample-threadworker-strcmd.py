import pigpio

from pi0servo import MultiServo, StrCmdToJson, ThreadWorker

PINS = [25, 27]
DEBUG_FLAG = False

STRCMDS = [
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

    "wa",
]


def main():
    """main"""

    print("START")

    # pigpioの初期化
    pi = pigpio.pi()
    if not pi.connected:
        print("ERROR: pigpio connection")
        return

    worker = None
    try:  # 異常終了のための備え
        # オブジェクトの初期化
        servo = MultiServo(pi, PINS, debug=DEBUG_FLAG)  # 複数サーボ
        worker = ThreadWorker(servo, debug=DEBUG_FLAG)  # ワーカースレッド
        parser = StrCmdToJson(  # 文字列コマンドをJSONコマンドに翻訳
            angle_factor=[1, -1], debug=DEBUG_FLAG
        )

        # **IMPORTANT**
        # ワーカースレッドを裏で動かす
        worker.start()

        # コマンド呼び出し
        # - ワーカースレッドで非同期実行されるので、
        #   呼び出しはすぐに戻ってくる。
        for _strcmd in STRCMDS:
            # 文字列コマンドをJSONコマンドに翻訳
            _jsoncmd = parser.cmdstr_to_json(_strcmd)
            print(f"jsoncmd={_jsoncmd}")

            # スレッドワーカーに送信し、返信をすぐに受け取る
            result = worker.send(_jsoncmd)
            print(f">>> {_strcmd} = {_jsoncmd}")
            print(f"    <<< {result}\n")

    finally:  # 必ず実行される: 異常終了時でも、適切に終了処理を行う
        if worker:
            worker.end()
        if pi:
            pi.stop()

        print("END")


if __name__ == "__main__":
    main()

import pigpio

from pi0servo import MultiServo, ThreadWorker

PINS = [25, 27]
DEBUG_FLAG = False

CMD_JSONS = [
    {"method": "step_n", "params": {"n": 20}},
    {"method": "move_sec", "params": {"sec": 1.0}},
    {"method": "move", "params": {"angles": [50, 50]}},
    {"method": "move", "params": {"angles": [-50, 50]}},
    {"method": "move_sec", "params": {"sec": 0.1}},
    {"method": "sleep", "params": {"sec": 1}},
    {"method": "move", "params": {"angles": [50, -50]}},
    {"method": "move", "params": {"angles": [-50, -50]}},
    {"method": "move_sec", "params": {"sec": MultiServo.DEF_MOVE_SEC}},
    {"method": "move", "params": {"angles": [0, 0]}},
    {"method": "wait"},  # すべての動作が完了するまで待つ
]


def main():
    """main"""

    print("START")

    pi = pigpio.pi()
    if not pi.connected:
        return

    # servo = None
    worker = None
    try:
        # オブジェクトの初期化
        servo = MultiServo(pi, PINS, debug=DEBUG_FLAG)
        worker = ThreadWorker(servo, debug=DEBUG_FLAG)
        worker.start()

        # コマンド呼び出し
        # - 非同期実行されるので、すぐに戻ってくるが、処理は未完了
        for cmd in CMD_JSONS:
            print(f">>> {cmd}")
            result = worker.send(cmd)
            print(f"    <<<{result}")

    finally:
        if worker:
            worker.end()
        if pi:
            pi.stop()

        print("END")


if __name__ == "__main__":
    main()

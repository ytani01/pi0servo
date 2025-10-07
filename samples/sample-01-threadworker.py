import pigpio

from pi0servo import MultiServo, ThreadWorker

PINS = [25, 27]
DEBUG_FLAG = False

JSON_CMDS = [
    {"method": "step_n", "params": {"n": 20}},
    {"method": "move_sec", "params": {"sec": 0.5}},
    {"method": "move", "params": {"angles": [10, 10]}},
    {"method": "move", "params": {"angles": [-10, 10]}},
    {"method": "move_sec", "params": {"sec": 0.1}},
    {"method": "sleep", "params": {"sec": 0.5}},
    {"method": "move", "params": {"angles": [10, -10]}},
    {"method": "move", "params": {"angles": [-10, -10]}},
    {"method": "move_sec", "params": {"sec": MultiServo.DEF_MOVE_SEC}},
    {"method": "move", "params": {"angles": [0, 0]}},
    {"method": "wait"},  # workerスレッドのすべての動作が完了するまで待つ
]


def main():
    """main"""
    print("START")

    pi = pigpio.pi()
    if not pi.connected:
        return

    servo = None
    worker = None
    try:
        # オブジェクトの初期化
        servo = MultiServo(pi, PINS, debug=DEBUG_FLAG)
        worker = ThreadWorker(servo, debug=DEBUG_FLAG)

        worker.start()  # ワーカースレッドを裏で動かす

        # コマンド呼び出し
        for cmd in JSON_CMDS:
            print(f">>> {cmd}")
            result = worker.send(cmd)
            print(f"    <<<{result}")

    finally:
        if worker:
            worker.end()
        if servo:
            servo.off()
        if pi:
            pi.stop()
        print("END")


if __name__ == "__main__":
    main()

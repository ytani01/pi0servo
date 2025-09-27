import time

import pigpio

from pi0servo import MultiServo, ThreadWorker

PINS = [25, 27]
DEBUG_FLAG = False

CMD_JSONS = [
    {"cmd": "step_n", "n": 20},
    {"cmd": "move_sec", "sec": 1.0},
    {"cmd": "move", "angles": [50, 50]},
    {"cmd": "move", "angles": [-50, 50]},
    {"cmd": "move_sec", "sec": 0.1},
    {"cmd": "sleep", "sec": 1},
    {"cmd": "move", "angles": [50, -50]},
    {"cmd": "move", "angles": [-50, -50]},
    {"cmd": "move_sec", "sec": MultiServo.DEF_MOVE_SEC},
    {"cmd": "move", "angles": [0, 0]},
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
            print(f"    <<< {result}")

        # **Important**
        # スレッドの処理がすべて完了するのを待つ
        while worker.qsize > 0:
            print(f"qsize = {worker.qsize}")
            time.sleep(1)
        print(f"qsize = {worker.qsize}")

    finally:
        if worker:
            worker.end()
        if pi:
            pi.stop()

        print("END")


if __name__ == "__main__":
    main()

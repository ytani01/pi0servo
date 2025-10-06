import time

import pigpio

from pi0servo import ThreadMultiServo

PINS = [25, 27]
DEBUG_FLAG = False

ANGLES: list[list[int | None]] = [
    [10, 10],
    [0, 0],
    [-10, -10],
    [0, 0],
    [10, -10],
    [0, 0],
    [-10, 10],
    [0, 0],
]


def main():
    """main"""

    print("START")

    pi = pigpio.pi()
    if not pi.connected:
        return

    sv = None
    try:
        sv = ThreadMultiServo(pi, PINS, debug=DEBUG_FLAG)

        for angles in ANGLES:
            sv.move_all_angles_sync(angles)
            print(f"called: move_all_angles_sync({angles})")

        # **Important**
        while sv.qsize > 0:
            print(f"qsize = {sv.qsize}")
            time.sleep(0.5)
        print(f"qsize = {sv.qsize}")

    finally:
        if sv:
            sv.end()
        if pi:
            pi.stop()

        print("END")


if __name__ == "__main__":
    main()

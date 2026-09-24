#!/usr/bin/env python3
"""Gentle sequential test for the five angle servos, gripper, and rail."""

import argparse
import glob
import sys
import time

import serial


BAUD_RATE = 1_000_000
PAUSE_SECONDS = 1.0


def find_port() -> str:
    ports = sorted(
        glob.glob("/dev/ttyACM*")
        + glob.glob("/dev/ttyUSB*")
        + glob.glob("/dev/serial/by-id/*")
    )
    if not ports:
        raise RuntimeError("No serial device found; pass the port explicitly, e.g. --port /dev/ttyACM0")
    return ports[0]


def send(arduino: serial.Serial, command: str) -> None:
    print(f"  {command}", flush=True)
    arduino.write((command + "\n").encode("ascii"))
    arduino.flush()
    time.sleep(PAUSE_SECONDS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="serial port (auto-detected if omitted)")
    args = parser.parse_args()

    port = args.port or find_port()
    print(f"Opening {port} at {BAUD_RATE} baud", flush=True)

    with serial.Serial(port, BAUD_RATE, timeout=1) as arduino:
        # Let the serial connection settle, then test each angle servo top to bottom.
        time.sleep(2)
        for motor in range(1, 6):
            print(f"Motor {motor}", flush=True)
            for angle in (77, 111, 90):
                send(arduino, f"{motor}.{angle}")

        print("Gripper", flush=True)
        send(arduino, "c")
        send(arduino, "o")

        print("Rail", flush=True)
        send(arduino, "f.1000")
        send(arduino, "b.1000")

    print("Wiggle test complete.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nWiggle test interrupted.", file=sys.stderr)
        raise SystemExit(130)

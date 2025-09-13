# Project Purpose

This project provides a Python driver for controlling servo motors with Raspberry Pi, specifically designed for low-spec devices like the Raspberry Pi Zero 2W. It leverages the `pigpio` library to enable synchronized control of multiple inexpensive servo motors (e.g., SG90) without requiring additional hardware like PCA9685.

Key features include:
- Individual servo calibration to compensate for manufacturing differences.
- Synchronized control of multiple servos to move to different angles simultaneously.
- Remote control capabilities via a REST API, supporting both JSON and simplified string commands.
- Command-line interface (CLI) for direct operation and network-based control.
- Flexible GPIO pin assignment for servo control.
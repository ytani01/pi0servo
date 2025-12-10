# Project Purpose: pi0servo

`pi0servo` is a Python library designed for controlling servo motors with Raspberry Pi devices, specifically optimized for low-power models like the Raspberry Pi Zero 2W. Its primary goal is to provide a robust and flexible solution for controlling multiple inexpensive servo motors (e.g., SG90) in a synchronized manner.

Key functionalities include:
- Direct servo control via Raspberry Pi's GPIO using the `pigpio` library, eliminating the need for additional hardware like PCA9685.
- Calibration features to compensate for individual servo motor differences, allowing users to define precise -90, 0, and +90 degree positions and save these settings.
- Synchronized control of multiple servos for applications like robotics.
- Remote control capabilities through a Web API, primarily using a JSON-RPC based interface that supports both JSON and string commands.
- A comprehensive Command-Line Interface (CLI) for direct interaction, calibration, and server/client operations.

The project aims to be highly performant, enabling smooth and synchronized movement of numerous servos even on resource-constrained Raspberry Pi models.
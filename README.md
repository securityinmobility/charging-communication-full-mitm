# Charging Communication MitM

A Man-in-the-Middle (MitM) tool for EV charging communication.

## Overview

This project enables interception and control of the communication between Electric Vehicles (EVs) and Electric Vehicle Supply Equipment (EVSE) for research purposes.

## Requirements

- Python 3.7+
- Serial connection to MitM hardware board

## Installation

```bash
pip install -e . # -e if in development
```

## Quick Start

```bash
# Test connection to hardware
python test_connection.py

# Run with mock interface (for development)
USB=mock python mitm_main.py

# Run with real hardware
USB=/dev/ttyUSB0 python mitm_main.py

# Board is just monitoring and passing on the messages
USB=/dev/ttyUSB0 python scripts/mitm_listen.py
```

## Environment variables 

```
USB         # path to usb port
LOG_LEVEL   # DEBUG, INFO
LOG_FILE    # filename of the file, is created in logs folder
```

## License

GNU Affero General Public License v3.0 (AGPL-3.0)

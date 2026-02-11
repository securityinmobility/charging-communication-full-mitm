# Charging Communication MitM

A Man-in-the-Middle (MitM) tool for EV charging communication.

## Overview

This project enables interception and control of the communication between Electric Vehicles (EVs) and Electric Vehicle Supply Equipment (EVSE) for testing and development purposes.

## Features

- Monitor Control Pilot (CP) and Proximity Pilot (PP) signals
- Simulate both EV and EVSE behavior
- Pass-through mode for transparent forwarding
- Support for all charging states (A, B, C, D, E, F)

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
USB=mock python mitm-main.py

# Run with real hardware
USB=/dev/ttyUSB0 python mitm-main.py
```

## Environment variables 

```
USB         # path to usb port
LOG_LEVEL   # DEBUG, INFO
LOG_FILE    # filename is created in logs folder
```

## License

GNU Affero General Public License v3.0 (AGPL-3.0)

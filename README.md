# Charging Communication MitM

A Man-in-the-Middle (MitM) tool for EV charging communication based on IEC 61851-1 standard.

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
pip install -r requirements.txt
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

## Project Structure

```
.
├── base_classes.py          # Abstract base classes
├── messages.py              # Message protocol definitions
├── mitm_board.py            # Board communication logic
├── mitm_charging-station.py # EVSE simulator
├── mitm_vehicle.py          # EV simulator
├── mitm_usb_interface.py    # Serial interface
└── mocks/                   # Mock implementations
```

## License

GNU Affero General Public License v3.0 (AGPL-3.0)

## References

- [DIN EN 61851-1:2012](https://en.wikipedia.org/wiki/IEC_61851) - Electric vehicle conductive charging system
- [EVSim Documentation](https://evsim.gonium.net/)

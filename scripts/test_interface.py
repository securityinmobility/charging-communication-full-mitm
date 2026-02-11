import sys
import asyncio
import os
import logging
from datetime import datetime

from mitm.log import setup_logging
from mitm.interfaces.usb_interface import UsbInterface 
from mitm.interfaces.mock_usb import MockUsbInterface 
from mitm.mitm_board import MitMBoard
from mitm.messages import Message, MessageLogic, MessageType, ResponseType


def test_messages(interface):
    """Test message creation and responses."""
    # Create a test message
    # PEV Sim CP
    logger.info("PEV Sim CP")
    for value in range(0,255):
        message = bytes([0xC1, value, 0xFF])
        interface.write(message)
        response = interface.read(9)

    # EVSE Sim CP
    logger.info("EVSE Sime CP")
    for value in range(0,255):
        message = bytes([0xC2, value, 0xFF])
        interface.write(message)
        response = interface.read(9)
        
    # Plug Sim PP
    logger.info("Plug Sim PP")
    for value in range(0,255):
        message = bytes([0xC3, value, 0xFF])
        interface.write(message)
        response = interface.read(9)

    # Cable Sim PP
    logger.info("Cable Sim PP")
    for value in range(0,255):
        message = bytes([0xC4, value, 0xFF])
        interface.write(message)
        response = interface.read(9)


if __name__ == "__main__":
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    log_file = os.environ.get("LOG_FILE", None)

    setup_logging(numeric_level, log_file)
    logger = logging.getLogger(__name__)

    try:
        logger.info("MITM Started")
        logger.info("Starting MitM program")
        
        usb_impl = os.environ.get("USB", "mock")
        
        if usb_impl == "mock":
            usb = MockUsbInterface(port="/dev/ttyUSB0", baudrate=9600, error_on_first_message=True)
        else:
            usb = UsbInterface(port=usb_impl, baudrate=9600)

        # Connect to board
        usb.connect()
        
        test_messages(usb)
        
    
    except KeyboardInterrupt:
        logger.debug("MitM program terminated manually")
    finally:
        usb.close()
        logger.info("MitM program terminated")
        logging.shutdown()

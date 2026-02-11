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

protocol_command = [
    # (description, Command, )
    ("set PEV Sim CP", 0xC1, [
        ("no EV connected", "A", 0x00),
        ("EV connected", "B", 0x01),
        ("invalid", "", 0x02),
        ("EV ready", "C", 0x03),
        ("invalid", "", 0x04),
        ()
    ], 0xB1, 0xE1),
    ("set EVSE Sim CP", 0xC2, [], 0xB2, 0xE2),
    ("set Plug Sim PP", 0xC3, [], 0xB3, 0xE3),
    ("set Cable Sim PP", 0xC4, [], 0xB4, 0xE4)
]

def expected_response(message: bytes):
    response = 0xFE
    if message[0] == 0xC1:
        match message[1]:
            case 0x00:
                response = 0xB1
            case 0x01:
                response = 0xB1
            case 0x03: 
                response = 0xB1
            case 0x05:
                response = 0xB1
            case _:
                response = 0xE1
    elif message[0] == 0xC2:
        response = 0xB2
    elif message[0] == 0xC3:
        response = 0xB3
    elif message[0] == 0xC4:
        response = 0xB4
    return bytes([response, message[1], 0xFF])

def test_messages(board: MitMBoard):
    """Test message creation and responses."""
    # Create a test message
    # PEV Sim CP
    for value in range(0,255):
        message = MessageLogic.from_bytes([0xC1, value, 0xFF])
        if message is None: logging.error(f"Failed to create message {bytes([0xC1, value, 0xFF])}") 
        status = board.send_message(message, verbose=True, wait_response=0.1, message_label="message")
        if status == 1: logging.error("Error sending message")

    # EVSE Sim CP
    for value in range(0,255):
        message = MessageLogic.from_bytes([0xC2, value, 0xFF])
        if message is None: logging.error(f"Failed to create message {bytes([0xC1, value, 0xFF])}") 
        status = board.send_message(message, verbose=True, wait_response=0.1, message_label="message")
        if status == 1: logging.error("Error sending message")
        
    # Plug Sim PP
    for value in range(0,255):
        message = MessageLogic.from_bytes([0xC3, value, 0xFF])
        if message is None: logging.error(f"Failed to create message {bytes([0xC1, value, 0xFF])}") 
        status = board.send_message(message, verbose=True, wait_response=0.1, message_label="message")
        if status == 1: logging.error("Error sending message")

    # Cable Sim PP
    for value in range(0,255):
        message = MessageLogic.from_bytes([0xC4, value, 0xFF])
        if message is None: logging.error(f"Failed to create message {bytes([0xC1, value, 0xFF])}") 
        status = board.send_message(message, verbose=True, wait_response=0.1, message_label="message")
        if status == 1: logging.error("Error sending message")


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

        board = MitMBoard(usb_interface=usb)
        
        # Connect to board
        board.connect()
        board.set_pass_through(False)
        
        notification = board.wait_for_notification(1)
        if notification: 
            logger.info(f"Received notification: {notification.messageType}")
        else:
            logger.info(f"No notification received")
        
        notification = board.wait_for_notification(1)
        if notification: 
            logger.info(f"Received notification: {notification.messageType}")
        else:
            logger.info(f"No notification received")
        
        test_messages(board)
        
    
    except KeyboardInterrupt:
        logger.debug("MitM program terminated manually")
    finally:
        board.close()
        logger.info("MitM program terminated")
        logging.shutdown()

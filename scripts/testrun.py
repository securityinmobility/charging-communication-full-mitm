import os
import logging
import time

from mitm.log import setup_logging
from mitm.interfaces.usb_interface import UsbInterface 
from mitm.interfaces.mock_usb import MockUsbInterface 
from mitm.mitm_board import MitMBoard
from mitm.messages import Message, MessageLogic, MessageType, ResponseType

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
        board.set_pass_through(True)
        time.sleep(60)
    except KeyboardInterrupt:
        logger.debug("MitM program terminated manually")
    finally:
        board.close()
        logger.info("MitM program terminated")
        logging.shutdown()

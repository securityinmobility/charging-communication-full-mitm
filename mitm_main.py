import os
import logging

from mitm.log import setup_logging
from mitm.interfaces.usb_interface import UsbInterface 
from mitm.interfaces.mock_usb import MockUsbInterface 
from mitm.mitm_board import MitMBoard
from mitm.messages import Message, MessageLogic, MessageType, ResponseType

def test_messages(board: MitMBoard):
    """Test message creation and responses."""
    # Create a test message
    message1 = Message(messageType="PEV_SIM_CP", messageType_byte=MessageType.PEV_SIM_CP, decision_byte=0x00)
    if message1 is None: logging.error("Failed to create message1") 
    logging.debug(message1)
    message2 = Message(messageType="EVSE_SIM_CP", messageType_byte=MessageType.EVSE_SIM_CP, decision_byte=0x00)
    if message2 is None: logging.error("Failed to create message2")
    message3 = Message(messageType="EVSE_SIM_PP", messageType_byte=MessageType.EVSE_SIM_PP, decision_byte=0x00)
    if message3 is None: logging.error("Failed to create message3")
    message4 = Message(messageType="PEV_SIM_PP", messageType_byte=MessageType.PEV_SIM_PP, decision_byte=0x00)
    if message4 is None: logging.error("Failed to create message4")

    # Send the test messages and check for responses
    logging.info("Sending message1")
    status = board.send_message(message1, verbose=True, wait_response=0.3, message_label="message1")
    if status == 1: logging.error("Error sending message1")
    
    status = board.send_message(message2, verbose=True, wait_response=0.3, message_label="message2")
    if status == 1: logging.error("Error sending message2")
    
    status = board.send_message(message1, verbose=True, wait_response=0.3, message_label="message1")
    if status == 1: logging.error("Error sending message1")

    status = board.send_message(message3, verbose=True, wait_response=0.3, message_label="message3")
    if status == 1: logging.error("Error sending message3")

    status = board.send_message(message4, verbose=True, wait_response=0.3, message_label="message4")
    if status == 1: logging.error("Error sending message4")

    status = board.send_message(message1, verbose=True, wait_response=0.3, message_label="message1")
    if status == 1: logging.error("Error sending message1")

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
        test_messages(board)
        
    except KeyboardInterrupt:
        logger.debug("MitM program terminated manually")
    finally:
        board.close()
        logger.info("MitM program terminated")
        logging.shutdown()

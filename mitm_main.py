import sys
import asyncio
import os
import logging
from datetime import datetime

from mitm.interfaces.usb_interface import UsbInterface 
from mitm.interfaces.mock_usb import MockUsbInterface 
from mitm.mitm_board import MitMBoard
from mitm.messages import Message, MessageLogic, MessageType, ResponseType

def setup_logging(level=logging.INFO):
    """Configure logging for the entire application."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    env_name = os.environ.get("LOG_FILE")
    
    main_log = os.path.join(log_dir, env_name if env_name else f"mitm_{timestamp}.log")
    com_log = os.path.join(log_dir, f"com_{env_name}" if env_name else f"communication_{timestamp}.log")


    # Configure Root Logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(main_log),
            logging.StreamHandler()
        ]
    )
    
    # Configure a dedicated communication Logger
    com_logger = logging.getLogger('communication')
    com_logger.setLevel(logging.INFO)
    com_handler = logging.FileHandler(com_log)
    com_handler.setFormatter(logging.Formatter('%(asctime)s,%(message)s'))
    com_logger.addHandler(com_handler)
    com_logger.propagate = False
    

async def test_messages(board: MitMBoard):
    """Test message creation and responses."""
    # Create a test message
    message1 = Message(messageType="PEV_SIM_CP", messageType_byte=MessageType.PEV_SIM_CP, decision_byte=0x20)
    if message1 is None: logging.error("Failed to create message1") 
    logging.debug(message1)
    message2 = Message(messageType="EVSE_SIM_CP", messageType_byte=MessageType.EVSE_SIM_CP, decision_byte=0x00)
    if message2 is None: logging.error("Failed to create message2")
    message3 = Message(messageType="EVSE_SIM_PP", messageType_byte=MessageType.EVSE_SIM_PP, decision_byte=0x00)
    if message3 is None: logging.error("Failed to create message3")
    message4 = Message(messageType="PEV_SIM_PP", messageType_byte=MessageType.PEV_SIM_PP, decision_byte=0x00)
    if message4 is None: logging.error("Failed to create message4")
    error_msg = Message(messageType="ERROR", messageType_byte=MessageType.ERROR, decision_byte=None)
    if error_msg is None: logging.error("Failed to create error_msg")

    # Send the test messages and check for responses
    status = await board.send_message(error_msg, verbose=True, wait_response=0.2, message_label="error_msg")
    if status == 1: logging.error("Error sending error_msg")

    logging.info("Sending message1")
    status = await board.send_message(message1, verbose=True, wait_response=0.2, message_label="message1")
    if status == 1: logging.error("Error sending message1")
    
    status = await board.send_message(message1, verbose=True, wait_response=0.2, message_label="message1")
    if status == 1: logging.error("Error sending message1")

    status = await board.send_message(message2, verbose=True, wait_response=0.2, message_label="message2")
    if status == 1: logging.error("Error sending message2")

    status = await board.send_message(message3, verbose=True, wait_response=0.2, message_label="message3")
    if status == 1: logging.error("Error sending message3")

    status = await board.send_message(message4, verbose=True, wait_response=0.2, message_label="message4")
    if status == 1: logging.error("Error sending message4")

    status = await board.send_message(error_msg, verbose=True, wait_response=0.2, message_label="error_msg")
    if status == 1: logging.error("Error sending error_msg")

    status = await board.send_message(message1, verbose=True, wait_response=0.2, message_label="message1")
    if status == 1: logging.error("Error sending message1")

async def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting MitM program")
    
    usb_impl = os.environ.get("USB", "mock")
    
    if usb_impl == "mock":
        usb = MockUsbInterface(port="/dev/ttyUSB0", baudrate=9600, error_on_first_message=True)
    else:
        usb = UsbInterface(port=usb_impl, baudrate=9600)

    board = MitMBoard(usb_interface=usb)
    
    try:
        # Connect to board
        await board.connect()
        board.set_pass_through(True)
        await test_messages(board)
        
        notification = await board.wait_for_notification(1)
        if notification: 
            logger.info(f"Received notification: {notification.messageType}")
        else:
            logger.info(f"No notification received")
        
        notification = await board.wait_for_notification(1)
        if notification: 
            logger.info(f"Received notification: {notification.messageType}")
        else:
            logger.info(f"No notification received")
    #except:
    #    logger.error(f"An Exception occured")
    finally:
        board.close()

if __name__ == "__main__":
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    #log_file = os.environ.get("LOG_FILE", None)

    setup_logging(numeric_level)
    logger = logging.getLogger(__name__)

    try:
        logger.info("MITM Started")
        asyncio.run(main())
        logger.info("MitM program terminated")
    except KeyboardInterrupt:
        logger.debug("MitM program terminated manually")
    finally:
        logging.shutdown()

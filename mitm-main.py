import sys
import asyncio
import os
import logging

from mitm_board import MitMBoard
from messages import Message, MessageLogic, MessageType, ResponseType

def setup_logging(level=logging.INFO, log_file='mitm.log'):
    """Configure logging for the entire application."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('mitm.log')
        ]
    )

async def test_messages(board: MitMBoard):
    """Test message creation and responses."""
    # Create a test message
    message1 = Message(messageType="PEV_SIM_CP", messageType_byte=MessageType.PEV_SIM_CP, decision_byte=0x20)
    if message1 is None: logging.error("Failed to create message1")
    message2 = Message(messageType="EVSE_SIM_CP", messageType_byte=MessageType.EVSE_SIM_CP, decision_byte=0x00)
    if message2 is None: logging.error("Failed to create message2")
    message3 = Message(messageType="EVSE_SIM_PP", messageType_byte=MessageType.EVSE_SIM_PP, decision_byte=0x00)
    if message3 is None: logging.error("Failed to create message3")
    message4 = Message(messageType="PEV_SIM_PP", messageType_byte=MessageType.PEV_SIM_PP, decision_byte=0x00)
    if message4 is None: logging.error("Failed to create message4")
    error_msg = Message(messageType="ERROR", messageType_byte=MessageType.ERROR, decision_byte=None)
    if error_msg is None: logging.error("Failed to create error_msg")
    
    # Send the test messages and check for responses
    status = await board.send_message(message1, verbose=True, message_label="message1")
    if status == 1: logging.error("Error sending message1")

    status = await board.send_message(message1, verbose=True, message_label="message1 - 2nd time")
    if status == 1: logging.error("Error sending message1 - 2nd time")

    status = await board.send_message(message2, verbose=True, message_label="message2")
    if status == 1: logging.error("Error sending message2")

    status = await board.send_message(message3, verbose=True, message_label="message3")
    if status == 1: logging.error("Error sending message3")

    status = await board.send_message(message4, verbose=True, message_label="message4")
    if status == 1: logging.error("Error sending message4")

    status = await board.send_message(error_msg, verbose=True, message_label="error_msg")
    if status == 1: logging.error("Error sending error_msg")

    status = await board.send_message(error_msg, verbose=True, message_label="error_msg - 2nd time")
    if status == 1: logging.error("Error sending error_msg - 2nd time")

async def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting MitM program")

    board = MitMBoard(port="/dev/ttyUSB0")
    
    try:
        # Connect to board
        await board.connect()
        board.set_pass_through(True)
        await test_messages(board)

        notification = await board.wait_for_notification(1)
        if notification: logger.info(f"Received notification: {notification.messageType}")
        notification = await board.wait_for_notification(1)
        logger.info(f"Received notification: {notification.messageType}")

    finally:
        board.close()

if __name__ == "__main__":
    log_file = 'mitm.log'
    setup_logging(logging.DEBUG, log_file=log_file)
    logger = logging.getLogger(__name__)

    try:
        asyncio.run(main())
        logger.info("MitM program terminated")
    except KeyboardInterrupt:
        logger.debug("MitM program terminated manually")
    finally:
        logging.shutdown()
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write('\n')
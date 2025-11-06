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
    board.send_message(message1)
    response = await board.wait_for_response(timeout=1)
    if response is None: logging.error("No response received for message1")
    else:
        if response.messageType_byte != MessageLogic.message_types[message1.messageType][1]: logging.error("Unexpected response received")
        else: logging.info("Received expected ACK for message1")

    board.send_message(message1) # Send again
    response = await board.wait_for_response(timeout=1)
    if response is None: logging.error("No response received for message1 - 2nd time")
    else:
        if response.messageType_byte != MessageLogic.message_types[message1.messageType][1]: logging.error("Unexpected response received - 2nd time")
        else: logging.info("Received expected ACK for message1 - 2nd time")

    board.send_message(message2)
    response = await board.wait_for_response(timeout=1)
    if response is None: logging.error("No response received for message2")
    else:
        if response.messageType_byte != MessageLogic.message_types[message2.messageType][1]: logging.error("Unexpected response received")
        else: logging.info("Received expected ACK for message2")

    board.send_message(message3)
    response = await board.wait_for_response(timeout=1)
    if response is None: logging.error("No response received for message3")
    else:
        if response.messageType_byte != MessageLogic.message_types[message3.messageType][1]: logging.error("Unexpected response received")
        else: logging.info("Received expected ACK for message3")
    
    board.send_message(message4)
    response = await board.wait_for_response(timeout=1)
    if response is None: logging.error("No response received for message4")
    else:
        if response.messageType_byte != MessageLogic.message_types[message4.messageType][1]: logging.error("Unexpected response received")
        else: logging.info("Received expected ACK for message4")
    
    board.send_message(error_msg)
    response = await board.wait_for_response(timeout=1)
    if response is None: logging.error("No response received for error_msg")

    board.send_message(error_msg)
    response = await board.wait_for_response(timeout=3)
    if response is None: logging.error("No response received for error_msg")


async def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting MitM program")

    board = MitMBoard(port="/dev/ttyUSB0")
    
    try:
        # Connect to board
        await board.connect()
        
        await test_messages(board)

        notification = await board.wait_for_notification(1)
        logger.info(f"Received notification: {notification.messageType}")
        notification = await board.wait_for_notification(1)
        logger.info(f"Received notification: {notification.messageType}")

    finally:
        board.close()

if __name__ == "__main__":
    log_file = 'mitm.log'
    setup_logging(logging.INFO, log_file=log_file)
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
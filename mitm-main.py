import sys
import asyncio
import os
import logging

from mitm_board import MitMBoard
from messages import Message, MessageFactory, MessageType, ResponseType

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
    message1 = MessageFactory.create_by_type(MessageType.PEV_SIM_CP, decision_byte=0x20)
    if message1 is None: logging.error("Failed to create message1")
    message2 = MessageFactory.create_by_type(MessageType.EVSE_SIM_CP, decision_byte=0x00)
    if message2 is None: logging.error("Failed to create message2")
    message3 = MessageFactory.create_by_type(MessageType.EVSE_SIM_PP, decision_byte=0x00)
    if message3 is None: logging.error("Failed to create message3")
    message4 = MessageFactory.create_by_type(MessageType.PEV_SIM_PP, decision_byte=0x00)
    if message4 is None: logging.error("Failed to create message4")
    error_msg = MessageFactory.create_by_type(MessageType.ERROR)
    if error_msg is None: logging.error("Failed to create error_msg")
    
    # Send the test messages and check for responses
    board.send_message(message1)
    response = await board.wait_for_response(timeout=1)
    if response is None: logging.error("No response received for message1")
    else:
        if response.messageType_byte != message1.ACK: logging.error("Unexpected response received")

    board.send_message(message1) # Send again
    response = await board.wait_for_response(timeout=1)
    if response is None: logging.error("No response received for message1 - 2nd time")
    else:
        if response.messageType_byte != message1.ACK: logging.error("Unexpected response received - 2nd time")

    board.send_message(message2)
    response = await board.wait_for_response(timeout=1)
    if response is None: logging.error("No response received for message2")
    else:
        if response.messageType_byte != message2.ACK: logging.error("Unexpected response received")

    board.send_message(message3)
    response = await board.wait_for_response(timeout=1)
    if response is None: logging.error("No response received for message3")
    else:
        if response.messageType_byte != message3.ACK: logging.error("Unexpected response received")

    board.send_message(message4)
    response = await board.wait_for_response(timeout=1)
    if response is None: logging.error("No response received for message4")
    else:
        if response.messageType_byte != message4.ACK: logging.error("Unexpected response received")

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
        
        """
        # Send a PEV simulation command
        board.send_command(message_type=MessageType.PEV_SIM_CP, decision_byte=0x01)
        
        # Wait for response
        response = await board.wait_for_response(timeout=1)
        if response:
            print(f"Got response: {response.__class__.__name__}")
            if response.decision_byte == ResponseType.ACK_PEV_SIM_CP:
                logger.info("Arduino responded correctly")
        else:
            logger.error(f"Unexpected response from Arduino: {response}")
        """
        await test_messages(board)

        # Listen for notifications
        #notification_task = asyncio.create_task(
        #    board.wait_for_notification()
        #)
        notification = await board.wait_for_notification()
        logger.info(f"Received notification: {notification.__class__.__name__}")
        notification = await board.wait_for_notification()
        logger.info(f"Received notification: {notification.__class__.__name__}")
        # Run for a while to demonstrate
        #await asyncio.sleep(10)

        
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
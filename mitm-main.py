import sys
import asyncio
import os
import logging

from mitm_board import MitMBoard
from messages import Message, MessageType, ResponseType

logging.basicConfig(level=logging.INFO)

async def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting MitM program")

    board = MitMBoard(port="/dev/ttyUSB0")
    
    try:
        # Connect to board
        await board.connect()
        
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
        
        # Listen for notifications
        notification_task = asyncio.create_task(
            board.wait_for_notification()
        )
        
        # Run for a while to demonstrate
        await asyncio.sleep(10)
        
    finally:
        board.close()



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
        logger = logging.getLogger(__name__)
        logger.info("MitM program terminated")
    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.debug("MitM program terminated manually")
import sys
import asyncio
import os
import logging

from mitm_board import MitMBoard
from messages import Message

logging.basicConfig(level=logging.INFO)

async def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting MitM program")

    mitm_board = MitMBoard()

    try:
        mitm_board.send_message(Message(0xC1, 0x00, 0xFF)) 
        response = mitm_board.read_response()
    except Exception as e:
        logger.error(f"Error during communication: {e}")
        sys.exit(1)

    if response == bytes([0xC1, 0x00, 0xFF]):
        logger.info("Arduino responded correctly")
    else:
        logger.error(f"Unexpected response from Arduino: {response}")

    mitm_board.close()

    logger.info("MitM program finished")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.debug("MitM program terminated manually")
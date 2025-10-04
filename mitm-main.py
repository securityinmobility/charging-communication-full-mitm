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
        await mitm_board.connect()

        reader_task = asyncio.create_task(mitm_board.read_messages())   # Start the message reader task

        try:
            mitm_board.send_message(Message(0xC1, 0x00, 0xFF)) 
            
        except Exception as e:
            logger.error(f"Error during communication: {e}")
            sys.exit(1)

        if response == bytes([0xC1, 0x00, 0xFF]):
            logger.info("Arduino responded correctly")
        else:
            logger.error(f"Unexpected response from Arduino: {response}")

        # Example of how to get messages from the queues
        while True:
            # Check notification_queue
            if not mitm_board.notification_queue.empty():
                message = await mitm_board.notification_queue.get()
                print(f"Received from notification queue: {message}")

            # Check response_queue
            if not mitm_board.response_queue.empty():
                message = await mitm_board.response_queue.get()
                print(f"Received from response queue: {message}")

            await asyncio.sleep(1)  # Prevent busy waiting

    except serial.SerialException:
        logging.error("Failed to connect to MitMBoard. Exiting.")
    except KeyboardInterrupt:
        logging.info("MitM program terminated manually")
    finally:
        mitm_board.close()

"""
Other Main
async def main():
    board = MitMBoard(port="/dev/ttyUSB0")
    
    try:
        # Connect to board
        await board.connect()
        
        # Send a PEV simulation command
        board.send_command(MessageType.PEV_SIM_CP)
        
        # Wait for response
        response = await board.wait_for_response(timeout=5.0)
        if response:
            print(f"Got response: {response.__class__.__name__}")
        
        # Listen for notifications
        notification_task = asyncio.create_task(
            board.wait_for_notification()
        )
        
        # Do other work...
        await asyncio.sleep(10)
        
    finally:
        board.close()
"""


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.debug("MitM program terminated manually")
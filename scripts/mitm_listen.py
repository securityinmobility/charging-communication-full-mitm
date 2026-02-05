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
    

async def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting MitM listen script")
    
    usb = UsbInterface(port="/dev/ttyUSB0", baudrate=9600)

    board = MitMBoard(usb_interface=usb)
    
    try:
        # Connect to board
        await board.connect()
        board.set_pass_through(True)
        
        asyncio.sleep(30) # pause main task
    except:
        logger.error(f"An Exception occured")
    finally:
        board.close()

if __name__ == "__main__":
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    setup_logging(numeric_level)
    logger = logging.getLogger(__name__)

    try:
        logger.info("MITM program Started")
        asyncio.run(main())
        logger.info("MitM program terminated")
    except KeyboardInterrupt:
        logger.debug("MitM program terminated manually")
    finally:
        logging.shutdown()

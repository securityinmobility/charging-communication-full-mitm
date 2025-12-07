import logging
import serial_asyncio
import asyncio
import time
from mitm_board import CommunicationInterface


# get logger for this module
logger = logging.getLogger(__name__)

class UsbInterface(CommunicationInterface):
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate

        self.reader = None
        self.writer = None

    async def connect(self):
        """Establish serial connection to the Arduino board."""
        try:
            self.reader, self.writer = await serial_asyncio.open_serial_connection(
                url=self.port, baudrate=self.baudrate
            )
            logger.info(f"Successfully connected to {self.port}")
            time.sleep(0.2)  # Wait for Arduino

        except serial.SerialException as e:
            logging.error(f"Cannot communicate with Arduino: {e}")
            raise

    def write(self, data):
        if self.writer:
            try:
                self.writer.write(data)
            except serial.SerialException as e:
                logger.error(f"Cannot communicate with Arduino: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
        else:
            logger.error("serial writer is not initialized.")
    
    async def read(self, size):
        if not self.reader:
            logger.error("Serial reader is not initialized.")
            return None

        try:
            data = await self.reader.read(size)
            return data
        except serial.SerialException as e:
            logger.error(f"Cannot communicate with Arduino: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in read loop: {e}")
            return None

    def is_initialized(self):
        if self.reader is None:
            return False
        else:
            return True
        
    def close(self):
        if self.writer:
            self.writer.close()

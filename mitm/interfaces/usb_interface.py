import logging
import serial_asyncio
import asyncio
from mitm.interfaces.abstract_interface import CommunicationInterface
from mitm.messages import MessageLogic

# get logger for this module
logger = logging.getLogger(__name__)
com_logger = logging.getLogger("communication")

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
            await asyncio.sleep(0.2)  # Wait for Arduino
            com_logger.info("UsbInterface initialized")

        except Exception as e:
            logging.error(f"Cannot communicate with Arduino: {e}")
            raise Exception(f"Connection Issue. Use Port: {self.port}")

    async def write(self, data):
        if self.writer:
            try:
                self.writer.write(data)
                await self.writer.drain()
                com_logger.info(f"Sent: {data.hex()} - {MessageLogic.get_message_type(data[0])}")
            except serial.SerialException as e:
                logger.error(f"Cannot communicate with Arduino: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
        else:
            logger.error("Serial writer is not initialized.")
    
    async def read(self, size):
        if not self.reader:
            logger.error("Serial reader is not initialized.")
            return None

        try:
            data = await self.reader.read(size)
            com_logger.info(f"Recieved: {data.hex()}")
            return data
        except Exception as e:
            logger.error(f"Unexpected error in the interface read function: {e}")
            return None

    def is_initialized(self):
        if self.reader is None:
            return False
        else:
            return True
        
    def close(self):
        if self.writer:
            self.writer.close()
            com_logger.info("UsbInterface closed")

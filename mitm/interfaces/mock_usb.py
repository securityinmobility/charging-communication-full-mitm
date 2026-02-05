import logging
import serial_asyncio
import asyncio
import time
from mitm.interfaces.abstract_interface import CommunicationInterface
from mitm.messages import MessageLogic

# get logger for this module
logger = logging.getLogger(__name__)

com_logger = logging.getLogger("communication")

class MockUsbInterface(CommunicationInterface):
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, error_on_first_message=False):
        self.port = port
        self.baudrate = baudrate
        
        self.reader = None
        self.writer = None
        self.error_flag = error_on_first_message
        self.output_buffer = bytearray()

    async def connect(self):
        self.reader = "reader" # make the object not none
        self.writer = "writer" # make the object not none
        await asyncio.sleep(0.2)
        com_logger.info("MockUsbInterface initialized")

    async def write(self, data):
        if isinstance(data, bytes) and len(data) == 3:
            message_type = MessageLogic.get_message_type(data[0])
            if data[2] == 0xFF or message_type != None:
                logger.debug(f"Message sent: {data.hex()}")
                if self.error_flag:    # simulate an error on the first message
                    self.error_flag = False
                    com_logger.info(f"Sent: {data.hex()} - {message_type}")
                    self.output_buffer.extend([0xD1, 0x00, 0xFF])
                    self.output_buffer.extend([0xD2, 0x00, 0xFF])
                elif message_type=="ERROR":
                    logger.debug("Error Message written")
                    # TODO simulate Error behaviour
                    com_logger.info(f"Sent: {data.hex()} - {message_type}")
                else:
                    logger.debug(f"message_type: {message_type}, data: {data.hex()}")
                    self.output_buffer.extend([MessageLogic.message_types[message_type][1], data[1], 0xFF]) # send ACK
                    com_logger.info(f"Sent: {data.hex()} - {message_type}")
            else:
                logger.error(f"Faulty message: {data.hex()}")
        else:
            logger.error(f"Faulty message: {data.hex()}")
        
        await asyncio.sleep(0.005) # simulate time to send

    async def read(self, size):
        await asyncio.sleep(0.005)
        data = self.output_buffer[0:size]
        self.output_buffer = self.output_buffer[size:]
        if data: com_logger.info(f"Recieved: {data.hex()}")
        return data   

    def is_initialized(self):
        if self.reader is None:
            return False
        else:
            return True

    def close(self):
        self.writer = None
        self.reader = None
        com_logger.info("MockUsbInterface closed")

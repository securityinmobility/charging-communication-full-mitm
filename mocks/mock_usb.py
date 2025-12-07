import logging
import serial_asyncio
import asyncio
import time
from mitm_board import CommunicationInterface
from messages import MessageLogic

# get logger for this module
logger = logging.getLogger(__name__)

class MockUsbInterface(CommunicationInterface):
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        
        self.reader = None
        self.writer = None
    
        self.output_buffer = bytearray()

    async def connect(self):
        self.reader = "reader" # make the object not none
        self.writer = "writer" # make the object not none
        time.sleep(0.2)

    def write(self, data):
        time.sleep(0.01)
        if isinstance(data, bytearray) and len(data) == 3:
            message_type = MessageLogic.get_message_type(data[1])
            if data[2] == 0xFF or message_type != None:
                self.output_buffer.extend([MessageLogic.message_types[message_type][1], data[1], 0xFF]) # send ACK
            else:
                logger.error(f"Wrong message sent: {data}")
        else:
            logger.error(f"Wrong message sent: {data}")

    async def read(self, size):
        data = self.output_buffer[0:size]
        self.output_buffer = self.output_buffer[size:]
        return data   

    def is_initialized(self):
        if self.reader is None:
            return False
        else:
            return True

    def close(self):
        self.writer = None
        self.reader = None

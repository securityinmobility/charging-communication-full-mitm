import time
import asyncio
import logging
import serial
import serial_asyncio
from typing import Optional, Dict, Callable, Coroutine, Any
from messages import *

# get logger for this module
logger = logging.getLogger(__name__)

class MitMBoard:
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.reader = None
        self.writer = None

        self.pass_through_enabled = False

        self.EVSE_CP_state = 0 # PWM duty cycle in %
        self.EVSE_PP_state = None
        self.PEV_CP_state = ChargingState.A
        self.PEV_PP_state = None

        self.EVSE_SIM_CP_state = 0 # PWM duty cycle in %
        self.EVSE_SIM_PP_state = PP_State_EVSEsim.NO_PLUG_CONNECTED
        self.PEV_SIM_CP_state = ChargingState.A
        self.PEV_SIM_PP_state = PP_State_PEVsim.NO_CABLE_CONNECTED

        # Queues for different message types
        self.response_queue = asyncio.Queue()
        self.notification_queue = asyncio.Queue()

    def set_pass_through(self, enabled: bool):
        self.pass_through_enabled = enabled

    async def connect(self):
        """Establish serial connection to the Arduino board."""
        try:
            self.reader, self.writer = await serial_asyncio.open_serial_connection(
                url=self.port, baudrate=self.baudrate
            )
            logger.info(f"Successfully connected to {self.port}")
            time.sleep(0.2)  # Wait for Arduino

            # Start the read task
            asyncio.create_task(self.read_message())
            
        except serial.SerialException as e:
            logging.error(f"Cannot communicate with Arduino: {e}")
            raise

    async def send_message(self, message: Message, verbose: bool = False, message_label: str = "message") -> int:
        """
        Send a message to the Arduino.
        
        Args:
            message: Message instance to send

            verbose: If True, log the response checking
            message_label: Label for logging purposes
        Returns:
            status code of the send operation (0: success, 1: error)
        """
        if self.writer:
            try:
                data = MessageLogic.to_bytes(message)
                self.writer.write(data)
                logger.debug(f"Sent message: {data.hex()}")
            except serial.SerialException as e:
                logger.error(f"Cannot communicate with Arduino: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
        else:
            logger.error("Serial writer is not initialized.")

        response = await self.wait_for_response(timeout=1)
        status = MessageLogic.check_response(message, response)
        if verbose:
            if status == 0:
                logger.info(f"'{message_label}' acknowledged (ACK).")
            elif status == 1:
                logger.info(f"'{message_label}' not acknowledged (NACK).")
            elif status == 2:
                logger.info (f"'{message_label}' received no response.")
            elif status == 3:
                logger.info(f"'{message_label}' received unexpected response.")
        else:
            logger.debug(f"'{message_label}' send status: {status}")

        if status == 0:
            return 0
        else:
            return 1

    async def read_message(self):
        """Continuously read and process messages from the Arduino."""
        if not self.reader:
            logger.error("Serial reader is not initialized.")
            return

        message_buffer = bytearray()
        
        while True:
            try:
                # Read available bytes
                data = await self.reader.read(99)  # Read up to 99 bytes
                if not data:
                    continue
                
                message_buffer.extend(data)
                
                # Process complete messages (assuming 3-byte messages)
                # TODO: Add logic for faulty message lengths
                while len(message_buffer) >= 3:
                    # Extract potential message
                    potential_message = bytes(message_buffer[:3])
                    logger.debug(f"Received potential message: {potential_message.hex()}")

                    try:
                        message = MessageLogic.from_bytes(potential_message)
                        logger.debug(f"Parsed message: {message.messageType}")
                        await self._route_message(message)
                        message_buffer = message_buffer[3:]  # Remove processed bytes
                    except ValueError:
                        # Invalid message, skip three bytes and try again
                        logger.warning(f"Invalid message bytes: {potential_message.hex()}")
                        message_buffer = message_buffer[3:]

            except serial.SerialException as e:
                logger.error(f"Cannot communicate with Arduino: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error in read loop: {e}")
                break

    async def _route_message(self, message: Message):
        """
        Route a message to the appropriate handler.
        
        Args:
            message: The parsed message to route
        """
        if message.messageType_byte in [ResponseType.NOTIFY_PEV_SIM_CHANGE,
                                         ResponseType.NOTIFY_EVSE_SIM_CHANGE]:

            await self._handle_notification(message)
        else:
            await self.response_queue.put(message)

    async def _handle_notification(self, message: Message):
        """Handle notification messages."""
        logger.info(f"Received notification: {message.messageType}")

        if message.messageType_byte == ResponseType.NOTIFY_PEV_SIM_CHANGE:
            self.PEV_SIM_CP_state = ChargingState(message.decision_byte)
            if self.pass_through_enabled:
                forward_message = Message(messageType="EVSE_SIM_CP", messageType_byte=MessageType.EVSE_SIM_CP, decision_byte=message.decision_byte)
                await self.send_message(forward_message)
        elif message.messageType_byte == ResponseType.NOTIFY_EVSE_SIM_CHANGE:
            self.EVSE_SIM_CP_state = message.decision_byte
            if self.pass_through_enabled:
                forward_message = Message(messageType="PEV_SIM_CP", messageType_byte=MessageType.PEV_SIM_CP, decision_byte=message.decision_byte)
                await self.send_message(forward_message)
        
        await self.notification_queue.put(message)

    async def _handle_response(self, message: Message):
        """Handle response messages."""
        logger.info(f"Received response: {MessageLogic.to_bytes(message).hex()}")
        await self.response_queue.put(message)

    async def wait_for_response(self, timeout: float = 2.0) -> Optional[Message]:
        """
        Wait for a response message with timeout.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Message or None if timeout
        """
        try:
            return await asyncio.wait_for(
                self.response_queue.get(), 
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Response timeout after {timeout} seconds")
            return None

    async def wait_for_notification(self, timeout: float = None) -> Optional[Message]:
        """
        Wait for a notification message.
        
        Args:
            timeout: Maximum time to wait (None for infinite)
            
        Returns:
            Message or None if timeout
        """
        if timeout:
            try:
                return await asyncio.wait_for(
                    self.notification_queue.get(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                return None
        else:
            return await self.notification_queue.get()

    def close(self):
        if self.writer:
            self.writer.close()
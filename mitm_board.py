import time
import asyncio
import logging
import serial
import serial_asyncio
from typing import Optional, Dict, Callable, Coroutine, Any
from messages import *

# get logger for this modeule
logger = logging.getLogger(__name__)

class MitMBoard:
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.reader = None
        self.writer = None

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

        # Message handlers by type
        self.message_handlers: Dict[type, Callable] = {}

        # Setup default routing
        self._setup_default_routing()

    def _setup_default_routing(self):
        """Setup default message routing based on message types."""
        # Route notification messages to notification queue
        self.register_handler(NotifyPEVSimChange, self._handle_notification)
        self.register_handler(NotifyEVSESimChange, self._handle_notification)

        # Route other messages to response queue
        self.register_handler(Response, self._handle_response)

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

    def send_message(self, message: Message):
        """
        Send a message to the Arduino.
        
        Args:
            message: Message instance to send
        """
        if self.writer:
            try:
                data = message.to_bytes()
                self.writer.write(data)
                logger.debug(f"Sent message: {data.hex()}")
            except serial.SerialException as e:
                logger.error(f"Cannot communicate with Arduino: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
        else:
            logger.error("Serial writer is not initialized.")

    def send_command(self, message_type: MessageType, 
                     decision_byte: int = None):
        """
        Convenience method to send a message by type.
        
        Args:
            message_type: Type of message to send
            start_byte: Optional start byte override
            end_byte: Optional end byte override
        """
        kwargs = {}
        
        if decision_byte is not None:
            kwargs['decision_byte'] = decision_byte
            
        message = MessageFactory.create_by_type(message_type, **kwargs)
        if message:
            self.send_message(message)
        else:
            logging.error(f"Failed to create message of type {message_type}")

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
                while len(message_buffer) >= 3:
                    # Extract potential message
                    potential_message = bytes(message_buffer[:3])
                    logger.debug(f"Received potential message: {potential_message.hex()}")

                    # Try to parse the message
                    message = MessageFactory.create_from_bytes(potential_message)
                    logger.debug(f"Parsed message: {type(message)}")
                    if message:
                        # Valid message found
                        await self._route_message(message)
                        message_buffer = message_buffer[3:]  # Remove processed bytes
                    else:
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
        message_type = type(message)
        handler = self.message_handlers.get(message_type)
        
        if handler:
            await handler(message)
        else:
            logger.warning(f"No handler registered for {message_type.__name__}")
            # Default: put in response queue
            await self.response_queue.put(message)

    async def _handle_notification(self, message: Message):
        """Handle notification messages."""
        logger.info(f"Received notification: {message.__class__.__name__}")
        await self.notification_queue.put(message)

        # Extension point: add setting of the information on the board
        # Extension point: add functionality to automatically "pass through" signals

    async def _handle_response(self, message: Message):
        """Handle response messages."""
        logger.info(f"Received response: {message.__class__.__name__} {message.to_bytes().hex()}")
        await self.response_queue.put(message)

    def register_handler(self, message_class: type, 
                     handler: Callable[[Message], Coroutine[Any, Any, None]]):
        """
        Register a custom handler for a specific message type.
        
        Args:
            message_class: The Message subclass to handle
            handler: Async function to handle the message
        """
        self.message_handlers[message_class] = handler

    async def wait_for_response(self, timeout: float = 5.0) -> Optional[Message]:
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
import time
import asyncio
import logging
import serial
import serial_asyncio
from typing import Optional, Dict, Callable, Coroutine, Any
from messages import *
from base_classes import CommunicationInterface

# get logger for this module
logger = logging.getLogger(__name__)

class MitMBoard:
    def __init__(self, usb_interface:CommunicationInterface):
        self.usb = usb_interface
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
        self.responses = [] # list for the responses
        self.response_queue = asyncio.LifoQueue()
        self.notification_queue = asyncio.Queue()

    def set_pass_through(self, enabled: bool):
        self.pass_through_enabled = enabled
    
    async def connect(self):
        await self.usb.connect()
        # Start the read task
        asyncio.create_task(self.read_message())
    
    async def send_message(self, message: Message, verbose: bool = False, wait_response=0.1, message_label: str = "message") -> int:
        """
        Send a message to the Arduino.
        
        Args:
            message: Message instance to send

            verbose: If True, log the response checking
            message_label: Label for logging purposes
        Returns:
            status code of the send operation (0: success, 1: error)
        """
        
        data = MessageLogic.to_bytes(message)
        self.usb.write(data)

        response = await self.get_response(message=message, timeout=wait_response)
        
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
        if not self.usb.is_initialized():
            logger.error("Serial reader is not initialized.")
            return

        message_buffer = bytearray()
        
        while True:
            try:
                # Read available bytes
                data = await self.usb.read(99)  # Read up to 99 bytes
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

    async def get_response(self, message: Message, timeout: float = 2.0) -> Optional[Message]:
        ACK = MessageLogic.message_types[message.messageType][1] 
        NACK = MessageLogic.message_types[message.messageType][2]
        
        # First check existing responses in the list
        response_msg = next((msg for msg in self.responses 
                            if (msg.messageType_byte == ACK or msg.messageType_byte == NACK) 
                            and msg.decision_byte == message.decision_byte), None)
        if response_msg:
            self.responses.remove(response_msg)
            return response_msg
        
        # Wait time for new responses from queue
        start_time = asyncio.get_event_loop().time()
        end_time = start_time + timeout
        
        #logging.debug(f"Starting wait at {start_time}, will timeout at {end_time}, timeout={timeout}")
        
        try:
            while True:

                current_time = asyncio.get_event_loop().time()
                remaining_time = end_time - current_time

                if remaining_time <= 0:
                    logging.debug("Timeout check:remaining_time <= 0, returning None")
                    return None
                
                #logging.debug(f"About to call wait_for with timeout={remaining_time}")
            
                response_msg = await asyncio.wait_for(
                    self.response_queue.get(), 
                    timeout=remaining_time
                )
                
                # Check if this is the matching message 
                if ((response_msg.messageType_byte == ACK or response_msg.messageType_byte == NACK) 
                    and response_msg.decision_byte == message.decision_byte):
                    logging.debug("Found matching response") 
                    return response_msg
                else:
                    self.responses.append(response_msg)
                    # Continue waiting for more messages
                    
        except asyncio.TimeoutError:
            logging.debug("wait_for timed out")
            return None        
        except Exception as e:
            logging.error(f"Unexpected exeption: {type(e).__name__}: {e}")
            raise

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
        self.usb.close()


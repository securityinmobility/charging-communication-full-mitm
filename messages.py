from enum import IntEnum
from typing import Optional, Type, Dict
import logging
from dataclasses import dataclass

# get logger for this module
logger = logging.getLogger(__name__)

class MessageType(IntEnum):
    """Enumeration for message types based on decision byte."""
    PEV_SIM_CP = 0xC1
    EVSE_SIM_CP = 0xC2
    EVSE_SIM_PP = 0xC3
    PEV_SIM_PP = 0xC4
    ERROR = 0xFE
    
class ResponseType(IntEnum):
    """Enumeration for response types based on decision byte."""
    NOTIFY_PEV_SIM_CHANGE = 0xD1    # Notification for a change of the EVSE, which is connected to the sim PEV
    NOTIFY_EVSE_SIM_CHANGE = 0xD2   # Notification for a change of the PEV, which is connected to the sim EVSE
    ACK_PEV_SIM_CP = 0xB1
    NACK_PEV_SIM_CP = 0xE1
    ACK_EVSE_SIM_CP = 0xB2
    NACK_EVSE_SIM_CP = 0xE2
    ACK_EVSE_SIM_PP = 0xB3
    NACK_EVSE_SIM_PP = 0xE3
    ACK_PEV_SIM_PP = 0xB4
    NACK_PEV_SIM_PP = 0xE4
    ERROR = 0xFE

class ChargingState(IntEnum):
    """
    Charging state as described in DIN EN 61851-1:2012
    For a short summary see: https://evsim.gonium.net/#der-control-pilot-cp
    On the CP line between PEV and EVSE -> PEV Sim CP / EVSE measurement change
    """
    A = 0
    B = 1
    C = 3
    D = 5
    E = 24
    F = 255

class PP_State_EVSEsim(IntEnum): # maybe rework
    """
    Resistance values between PP and PE as defined in DIN EN 61851-1:2012
    For a short summary see: https://evsim.gonium.net/#der-proximity-plug-pp
    """
    NO_PLUG_CONNECTED = 0
    PLUG_CONNECTED = 1
    NO_SIGNAL = 2
    USER_REQUEST_STOP_CHARGING = 3

class PP_State_PEVsim(IntEnum): # maybe rework
    """
    Resistance values between PP and PE as defined in DIN EN 61851-1:2012
    For a short summary see: https://evsim.gonium.net/#der-proximity-plug-pp
    """
    NO_CABLE_CONNECTED = 0
    CHARGE_20A = 1
    CHARGE_32A = 2
    INVALID = 3

@dataclass
class Message:
    """Base message class."""
    messageType_byte: int
    decision_byte: Optional[int]
    end_byte: int = 0xFF # End byte is always 0xFF

class MessageLogic:
    """Base message class."""
    message_types = {
        "PEV_SIM_CP": (MessageType.PEV_SIM_CP, ResponseType.ACK_PEV_SIM_CP, ResponseType.NACK_PEV_SIM_CP),
        "EVSE_SIM_CP": (MessageType.EVSE_SIM_CP, ResponseType.ACK_EVSE_SIM_CP, ResponseType.NACK_EVSE_SIM_CP),
        "EVSE_SIM_PP": (MessageType.EVSE_SIM_PP, ResponseType.ACK_EVSE_SIM_PP, ResponseType.NACK_EVSE_SIM_PP),
        "PEV_SIM_PP": (MessageType.PEV_SIM_PP, ResponseType.ACK_PEV_SIM_PP, ResponseType.NACK_PEV_SIM_PP),
        "ERROR": (MessageType.ERROR, None, None),
        "NOTIFY_PEV_SIM_CHANGE": (ResponseType.NOTIFY_PEV_SIM_CHANGE, None, None),
        "NOTIFY_EVSE_SIM_CHANGE": (ResponseType.NOTIFY_EVSE_SIM_CHANGE, None, None),
        "ACK_PEV_SIM_CP": (ResponseType.ACK_PEV_SIM_CP, None, None),
        "NACK_PEV_SIM_CP": (ResponseType.NACK_PEV_SIM_CP, None, None),
        "ACK_EVSE_SIM_CP": (ResponseType.ACK_EVSE_SIM_CP, None, None),
        "NACK_EVSE_SIM_CP": (ResponseType.NACK_EVSE_SIM_CP, None, None),
        "ACK_EVSE_SIM_PP": (ResponseType.ACK_EVSE_SIM_PP, None, None),
        "NACK_EVSE_SIM_PP": (ResponseType.NACK_EVSE_SIM_PP, None, None),
        "ACK_PEV_SIM_PP": (ResponseType.ACK_PEV_SIM_PP, None, None),
        "NACK_PEV_SIM_PP": (ResponseType.NACK_PEV_SIM_PP, None, None),
    }

    @staticmethod 
    def from_bytes(data: bytes) -> 'Message':
        """Create a message instance from bytes."""
        if len(data) < 3:
            raise ValueError(f"Invalid message length: {len(data)}")
        return Message(data[0], data[1], data[2])
    
    @staticmethod
    def to_bytes(message: 'Message') -> bytes:
        """Convert a message instance to bytes."""
        return bytes([message.messageType_byte, message.decision_byte if message.decision_byte is not None else 0x00, message.end_byte])
    
    @staticmethod
    def check_response(data: bytes) -> bool:
        """Check if the received data is an ACK or NACK for this message."""
        if len(data) < 3:
            return False
        return (data[1] == Message.ACK or data[1] == Message.NACK)

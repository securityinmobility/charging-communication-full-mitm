from enum import IntEnum
from typing import Optional, Type, Dict
import logging

# get logger for this modeule
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

class Message:
    """Base message class."""
    END_BYTE = 0xFF

    def __init__(self, messageType_byte: MessageType, decision_byte: int, 
                 end_byte: int | None = None, ACK: ResponseType | None = None, 
                 NACK: ResponseType | None = None):
        self.messageType_byte = messageType_byte
        self.decision_byte = decision_byte
        self.end_byte = end_byte
        self.ACK = ACK
        self.NACK = NACK

    def to_bytes(self) -> bytes:
        """Serialize the message to bytes for transmission."""
        return bytes([self.messageType_byte, self.decision_byte, self.end_byte])

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Message':
        """Create a message instance from bytes."""
        if len(data) < 3:
            raise ValueError(f"Invalid message length: {len(data)}")
        return cls(data[0], data[1], data[2])

    def check_message(self, data: bytes) -> bool:
        """Check if the received data matches the expected message format."""
        if len(data) < 3:
            return False
        return (data[0] == self.messageType_byte and 
                data[2] == self.end_byte)

    def chekck_response(self, data: bytes) -> bool:
        """Check if the received data is an ACK or NACK for this message."""
        if len(data) < 3:
            return False
        return (data[1] == self.ACK or data[1] == self.NACK)

class PEVSimCPMessage(Message):
    """Message to control the simulated PEV CP Pin."""
    MESSAGE_TYPE = MessageType.PEV_SIM_CP
    ACK_RESPONSE = ResponseType.ACK_PEV_SIM_CP
    NACK_RESPONSE = ResponseType.NACK_PEV_SIM_CP

    protocol_dict = {   # State: (Hex, Description)
        'A': (0x00, "No EV connected"),
        'B': (0x01, "EV connected"),
        'C': (0x03, "EV ready"),
        'D': (0x05, "EV ready + vent. req."),
        'E': (0x18, "Error (short circuit)"),
        'F': (0xFE, "Error (-12V)"),
    }

    def __init__(self, decision_byte: int | None = None, 
                 cp_state: ChargingState = ChargingState.A):

        if decision_byte is None:
            if cp_state not in ChargingState:
                raise ValueError(f"Invalid state: {cp_state}")
            else:
                decision_byte = self.protocol_dict[cp_state.name][0]

        self.cp_state = cp_state

        super().__init__(self.MESSAGE_TYPE, decision_byte, Message.END_BYTE, self.ACK_RESPONSE, self.NACK_RESPONSE)

    def set_state(self, cp_state: ChargingState):
        """Set the state of the simulated PEV CP Pin."""
        if cp_state in ChargingState:
            self.cp_state = cp_state
            self.decision_byte = self.protocol_dict[cp_state.name][0]
        else:
            raise ValueError(f"Invalid state: {cp_state}")

    def get_state(self) -> ChargingState:
        """Get the current state of the simulated PEV CP Pin."""
        return self.cp_state

    @classmethod
    def from_bytes(cls, data: bytes) -> 'PEVSimCPMessage':
        if len(data) != 3:
            raise ValueError(f"Invalid message length: {len(data)}")
        if data[0] != cls.MESSAGE_TYPE or data[2] != cls.END_BYTE:
            raise ValueError("Invalid message format")
        
        decision_byte = data[1]
        return cls(decision_byte=decision_byte)

class EVSESimCPMessage(Message):
    """Message to control the simulated EVSE CP Pin.
    
    duty_cycle | Description                | resulting signal
    -------------------------------------------------
    0          | No signal / not connected  | 0V
    1 - 99     | Command                    | PWM +12V to -12V with duty cycle 1% to 99%
    100        | waiting for EV to connect  | DC +12V
    """
    MESSAGE_TYPE = MessageType.EVSE_SIM_CP
    ACK_RESPONSE = ResponseType.ACK_EVSE_SIM_CP
    NACK_RESPONSE = ResponseType.NACK_EVSE_SIM_CP   

    def __init__(self, decision_byte: int | None = None, 
                 duty_cycle: int | None = None):

        if decision_byte is None:
            if duty_cycle is None:
                decision_byte = 0x00  # Default to no signal
                duty_cycle = 0
            
            if 0 <= duty_cycle <= 100:
                self.duty_cycle = duty_cycle
                decision_byte = duty_cycle
            else:
                raise ValueError("Duty cycle must be between 0 and 100")

            self.duty_cycle = duty_cycle
        super().__init__(self.MESSAGE_TYPE, decision_byte, self.END_BYTE, self.ACK_RESPONSE, self.NACK_RESPONSE)

    def set_duty_cycle(self, duty_cycle: int):
        """Set the duty cycle of the simulated EVSE CP Pin."""

        if 0 <= duty_cycle <= 100:
            self.duty_cycle = duty_cycle
            self.decision_byte = duty_cycle
        else:
            raise ValueError("Duty cycle must be between 0 and 100")

    def get_duty_cycle(self) -> int:
        """Get the current duty cycle of the simulated EVSE CP Pin."""
        return self.duty_cycle

    @classmethod
    def from_bytes(cls, data: bytes) -> 'EVSESimCPMessage':
        if len(data) != 3:
            raise ValueError(f"Invalid message length: {len(data)}")
        if data[0] != cls.MESSAGE_TYPE or data[2] != cls.END_BYTE:
            raise ValueError("Invalid message format")
        
        decision_byte = data[1]
        return cls(decision_byte=decision_byte)

class EVSESimPPMessage(Message):
    """Message to control the simulated EVSE PP Pin."""
    MESSAGE_TYPE = MessageType.EVSE_SIM_PP
    ACK_RESPONSE = ResponseType.ACK_EVSE_SIM_PP
    NACK_RESPONSE = ResponseType.NACK_EVSE_SIM_PP

    def __init__(self, decision_byte: int | None = None,
                pp_state: PP_State_EVSEsim | None = None):

        if decision_byte is None:
            if pp_state is None:
                decision_byte = 0x00  # Default to no plug connected
                pp_state = PP_State_EVSEsim.NO_PLUG_CONNECTED
            else:
                if pp_state not in PP_State_EVSEsim:
                    raise ValueError(f"Invalid PP state: {pp_state}")
                decision_byte = pp_state.value

            self.pp_state = pp_state
        super().__init__(self.MESSAGE_TYPE, decision_byte, Message.END_BYTE, self.ACK_RESPONSE, self.NACK_RESPONSE)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'EVSESimPPMessage':
        if len(data) != 3:
            raise ValueError(f"Invalid message length: {len(data)}")
        if data[0] != cls.MESSAGE_TYPE or data[2] != cls.END_BYTE:
            raise ValueError("Invalid message format")
        
        decision_byte = data[1]
        return cls(decision_byte=decision_byte)

class PEVSimPPMessage(Message):
    """Message to control the simulated PEV PP Pin."""
    MESSAGE_TYPE = MessageType.PEV_SIM_PP
    ACK_RESPONSE = ResponseType.ACK_PEV_SIM_PP
    NACK_RESPONSE = ResponseType.NACK_PEV_SIM_PP

    def __init__(self, decision_byte: int | None = None, 
                 pp_state: PP_State_PEVsim | None = None):

        if decision_byte is None:
            if pp_state is None:
                decision_byte = 0x00  # Default to no cable connected
                pp_state = PP_State_PEVsim.NO_CABLE_CONNECTED
            else:
                if pp_state not in PP_State_PEVsim:
                    raise ValueError(f"Invalid PP state: {pp_state}")
                decision_byte = pp_state.value

            self.pp_state = pp_state
        super().__init__(self.MESSAGE_TYPE, decision_byte, Message.END_BYTE, self.ACK_RESPONSE, self.NACK_RESPONSE)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'PEVSimPPMessage':
        if len(data) != 3:
            raise ValueError(f"Invalid message length: {len(data)}")
        if data[0] != cls.MESSAGE_TYPE or data[2] != cls.END_BYTE:
            raise ValueError("Invalid message format")
        
        decision_byte = data[1]
        return cls(decision_byte=decision_byte)

class NotifyPEVSimChange(Message):
    """Notification for PEV state change."""
    MESSAGE_TYPE = ResponseType.NOTIFY_PEV_SIM_CHANGE

    def __init__(self, decision_byte: int | None = None,
                 duty_cycle: int | None = None):

        super().__init__(self.MESSAGE_TYPE, decision_byte, Message.END_BYTE)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'NotifyPEVSimChange':
        if len(data) != 3:
            raise ValueError(f"Invalid message length: {len(data)}")
        if data[0] != cls.MESSAGE_TYPE or data[2] != cls.END_BYTE:
            raise ValueError("Invalid message format")
        
        decision_byte = data[1]
        return cls(decision_byte=decision_byte)

class NotifyEVSESimChange(Message):
    """Notification for EVSE state change."""
    MESSAGE_TYPE = ResponseType.NOTIFY_EVSE_SIM_CHANGE

    def __init__(self, messageType_byte: MessageType = MESSAGE_TYPE, 
                 decision_byte: int | None = None,
                 end_byte: int | None = None):
        super().__init__(self.MESSAGE_TYPE, decision_byte, end_byte)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'NotifyEVSESimChange':
        if len(data) != 3:
            raise ValueError(f"Invalid message length: {len(data)}")
        if data[0] != cls.MESSAGE_TYPE or data[2] != cls.END_BYTE:
            raise ValueError("Invalid message format")
        
        decision_byte = data[1]
        return cls(decision_byte=decision_byte)

class Response(Message):
    """Response class."""
    def __init__(self, responseType_byte: ResponseType, decision_byte: int | None = None, end_byte: int | None = None):
        super().__init__(responseType_byte, decision_byte, end_byte)

class ErrorMessage(Message):
    """Error message class."""
    MESSAGE_TYPE = MessageType.ERROR

    def __init__(self, decision_byte):
        logger.debug(f"decision_byte unused in ErrorMessage")
        super().__init__(self.MESSAGE_TYPE, 0xFE, Message.END_BYTE)

class MessageFactory:
    """Factory class for creating specific message types from bytes."""
    
    # Registry mapping decision bytes to message classes
    _message_registry: Dict[int, Type[Message]] = {
        MessageType.PEV_SIM_CP: PEVSimCPMessage,
        MessageType.EVSE_SIM_CP: EVSESimCPMessage,
        MessageType.EVSE_SIM_PP: EVSESimPPMessage,
        MessageType.PEV_SIM_PP: PEVSimPPMessage,
        MessageType.ERROR: ErrorMessage,
        ResponseType.NOTIFY_PEV_SIM_CHANGE: NotifyPEVSimChange,
        ResponseType.NOTIFY_EVSE_SIM_CHANGE: NotifyEVSESimChange,
        ResponseType.ACK_PEV_SIM_CP: Response,
        ResponseType.NACK_PEV_SIM_CP: Response,
        ResponseType.ACK_EVSE_SIM_CP: Response,
        ResponseType.NACK_EVSE_SIM_CP: Response,
        ResponseType.ACK_EVSE_SIM_PP: Response,
        ResponseType.NACK_EVSE_SIM_PP: Response,
        ResponseType.ACK_PEV_SIM_PP: Response,
        ResponseType.NACK_PEV_SIM_PP: Response,
    }
    
    @classmethod
    def create_from_bytes(cls, data: bytes) -> Optional[Message]:
        """
        Create the appropriate message type from raw bytes.
        
        Args:
            data: Raw bytes received (minimum 3 bytes expected)
            
        Returns:
            Specific Message subclass instance or None if invalid
        """
        if len(data) != 3:
            return None
            
        message_typeByte = data[0]
        message_class = cls._message_registry.get(message_typeByte)

        if message_class:
            return message_class.from_bytes(data)
        return None
    
    @classmethod
    def create_by_type(cls, messageType_byte: MessageType | ResponseType, 
                      decision_byte: int = 0x00,
                      end_byte: int = Message.END_BYTE) -> Optional[Message]:
        """
        Create a message by its type.
        
        Args:
            messageType_byte: The type of message to create
            decision_byte: Optional decision byte override
            end_byte: Optional end byte override
            
        Returns:
            Specific Message subclass instance or None if invalid type
        """
        message_class = cls._message_registry.get(messageType_byte)
        if message_class:
            return message_class(decision_byte=decision_byte)
        return None
    
    @classmethod
    def register_message_type(cls, messageType_byte: int, 
                             message_class: Type[Message]):
        """
        Register a new message type in the factory.
        
        Args:
            decision_byte: The byte that identifies this message type
            message_class: The Message subclass to instantiate
        """
        cls._message_registry[messageType_byte] = message_class

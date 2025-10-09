from enum import IntEnum
from typing import Optional, Type, Dict

class MessageType(IntEnum):
    """Enumeration for message types based on decision byte."""
    PEV_SIM_CP = 0xC1
    EVSE_SIM_CP = 0xC2
    EVSE_SIM_PP = 0xC3
    PEV_SIM_PP = 0xC4
    Error = 0xFE

    
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

class Message:
    """Base message class."""
    END_BYTE = 0xFF

    def __init__(self, messageType_byte: MessageType, decision_byte: int, end_byte: int, ACK: ResponseType, NACK: ResponseType):
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

    def __init__(self, messageType_byte: MessageType = MESSAGE_TYPE, 
                 decision_byte: int = 0x00, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(messageType_byte, decision_byte, end_byte)

class EVSESimCPMessage(Message):
    """Message to control the simulated EVSE CP Pin."""
    MESSAGE_TYPE = MessageType.EVSE_SIM_CP
    ACK_RESPONSE = ResponseType.ACK_EVSE_SIM_CP
    NACK_RESPONSE = ResponseType.NACK_EVSE_SIM_CP

    def __init__(self, messageType_byte: MessageType = MESSAGE_TYPE, 
                 decision_byte: int = 0x00, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(messageType_byte, decision_byte, end_byte)

class EVSESimPPMessage(Message):
    """Message to control the simulated EVSE PP Pin."""
    MESSAGE_TYPE = MessageType.EVSE_SIM_PP
    ACK_RESPONSE = ResponseType.ACK_EVSE_SIM_PP
    NACK_RESPONSE = ResponseType.NACK_EVSE_SIM_PP

    def __init__(self, messageType_byte: MessageType = MESSAGE_TYPE, 
                 decision_byte: int = 0x00, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(messageType_byte, decision_byte, end_byte)

class PEVSimPPMessage(Message):
    """Message to control the simulated PEV PP Pin."""
    MESSAGE_TYPE = MessageType.PEV_SIM_PP
    ACK_RESPONSE = ResponseType.ACK_PEV_SIM_PP
    NACK_RESPONSE = ResponseType.NACK_PEV_SIM_PP

    def __init__(self, messageType_byte: MessageType = MESSAGE_TYPE, 
                 decision_byte: int = 0x00, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(messageType_byte, decision_byte, end_byte)

class NotifyPEVSimChange(Message):
    """Notification for PEV state change."""
    MESSAGE_TYPE = ResponseType.NOTIFY_PEV_SIM_CHANGE

    def __init__(self, messageType_byte: MessageType = MESSAGE_TYPE, 
                 decision_byte: int = 0x00, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(messageType_byte, decision_byte, end_byte)

class NotifyEVSESimChange(Message):
    """Notification for EVSE state change."""
    MESSAGE_TYPE = ResponseType.NOTIFY_EVSE_SIM_CHANGE

    def __init__(self, messageType_byte: MessageType = MESSAGE_TYPE, 
                 decision_byte: int = 0x00, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(messageType_byte, decision_byte, end_byte)

class Response(Message):
    """Response class."""
    def __init__(self, responseType_byte: ResponseType, decision_byte: int, end_byte: int):
        super().__init__(responseType_byte, decision_byte, end_byte)

class ErrorMessage(Message):
    """Error message class."""
    MESSAGE_TYPE = MessageType.Error

    def __init__(self, messageType_byte: int = MESSAGE_TYPE, 
                 decision_byte: int = 0xFE, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(messageType_byte, decision_byte, end_byte)

class MessageFactory:
    """Factory class for creating specific message types from bytes."""
    
    # Registry mapping decision bytes to message classes
    _message_registry: Dict[int, Type[Message]] = {
        MessageType.PEV_SIM_CP: PEVSimCPMessage,
        MessageType.EVSE_SIM_CP: EVSESimCPMessage,
        MessageType.EVSE_SIM_PP: EVSESimPPMessage,
        MessageType.PEV_SIM_PP: PEVSimPPMessage,
        MessageType.NOTIFY_PEV_SIM_CHANGE: NotifyPEVSimChange,
        MessageType.NOTIFY_EVSE_SIM_CHANGE: NotifyEVSESimChange,
        MessageType.Error: ErrorMessage,
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
            
        decision_byte = data[1]
        message_class = cls._message_registry.get(decision_byte)
        
        if message_class:
            return message_class.from_bytes(data)
        return None
    
    @classmethod
    def create_by_type(cls, message_type: MessageType, 
                      messageType_byte: int = Message.messageType_byte,
                      end_byte: int = Message.END_BYTE) -> Optional[Message]:
        """
        Create a message by its type.
        
        Args:
            message_type: The type of message to create
            messageType_byte: Optional start byte override
            end_byte: Optional end byte override
            
        Returns:
            Specific Message subclass instance or None if invalid type
        """
        message_class = cls._message_registry.get(message_type)
        if message_class:
            return message_class(messageType_byte, message_type, end_byte)
        return None
    
    @classmethod
    def register_message_type(cls, decision_byte: int, 
                             message_class: Type[Message]):
        """
        Register a new message type in the factory.
        
        Args:
            decision_byte: The byte that identifies this message type
            message_class: The Message subclass to instantiate
        """
        cls._message_registry[decision_byte] = message_class

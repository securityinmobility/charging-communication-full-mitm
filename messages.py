from enum import IntEnum
from typing import Optional, Type, Dict

class MessageType(IntEnum):
    """Enumeration for message types based on decision byte."""
    PEV_SIM_CP = 0xC1
    EVSE_SIM_CP = 0xC2
    PLUG_SIM_PP = 0xC3
    CABLE_SIM_PP = 0xC4
    NOTIFY_PEV_CHANGE = 0xD2
    NOTIFY_EVSE_CHANGE = 0xD3

class Message:
    """Base message class."""
    END_BYTE = 0xFF
    
    def __init__(self, start_byte: int, decision_byte: int, end_byte: int):
        self.start_byte = start_byte
        self.decision_byte = decision_byte
        self.end_byte = end_byte
        self.response = bytes([None, None, None])

    def to_bytes(self) -> bytes:
        """Serialize the message to bytes for transmission."""
        return bytes([self.start_byte, self.decision_byte, self.end_byte])

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
        return (data[0] == self.start_byte and 
                data[2] == self.end_byte)

class PEVSimCPMessage(Message):
    """Message to control the simulated PEV CP Pin."""
    MESSAGE_TYPE = MessageType.PEV_SIM_CP
    
    def __init__(self, start_byte: int = MESSAGE_TYPE, 
                 decision_byte: int = None, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(start_byte, decision_byte, end_byte)

class EVSESimCPMessage(Message):
    """Message to control the simulated EVSE CP Pin."""
    MESSAGE_TYPE = MessageType.EVSE_SIM_CP
    
    def __init__(self, start_byte: int = Message.START_BYTE, 
                 decision_byte: int = MESSAGE_TYPE, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(start_byte, decision_byte, end_byte)

class PlugSimPPMessage(Message):
    """Message to control the simulated Plug PP Pin."""
    MESSAGE_TYPE = MessageType.PLUG_SIM_PP
    
    def __init__(self, start_byte: int = Message.START_BYTE, 
                 decision_byte: int = MESSAGE_TYPE, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(start_byte, decision_byte, end_byte)

class CableSimPPMessage(Message):
    """Message to control the simulated Cable PP Pin."""
    MESSAGE_TYPE = MessageType.CABLE_SIM_PP
    
    def __init__(self, start_byte: int = Message.START_BYTE, 
                 decision_byte: int = MESSAGE_TYPE, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(start_byte, decision_byte, end_byte)

class NotifyPEVChange(Message):
    """Notification for PEV state change."""
    MESSAGE_TYPE = MessageType.NOTIFY_PEV_CHANGE
    
    def __init__(self, start_byte: int = Message.START_BYTE, 
                 decision_byte: int = MESSAGE_TYPE, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(start_byte, decision_byte, end_byte)

class NotifyEVSEChange(Message):
    """Notification for EVSE state change."""
    MESSAGE_TYPE = MessageType.NOTIFY_EVSE_CHANGE
    
    def __init__(self, start_byte: int = Message.START_BYTE, 
                 decision_byte: int = MESSAGE_TYPE, 
                 end_byte: int = Message.END_BYTE):
        super().__init__(start_byte, decision_byte, end_byte)

class MessageFactory:
    """Factory class for creating specific message types from bytes."""
    
    # Registry mapping decision bytes to message classes
    _message_registry: Dict[int, Type[Message]] = {
        MessageType.PEV_SIM_CP: PEVSimCPMessage,
        MessageType.EVSE_SIM_CP: EVSESimCPMessage,
        MessageType.PLUG_SIM_PP: PlugSimPPMessage,
        MessageType.CABLE_SIM_PP: CableSimPPMessage,
        MessageType.NOTIFY_PEV_CHANGE: NotifyPEVChange,
        MessageType.NOTIFY_EVSE_CHANGE: NotifyEVSEChange,
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
        if len(data) < 3:
            return None
            
        decision_byte = data[1]
        message_class = cls._message_registry.get(decision_byte)
        
        if message_class:
            return message_class.from_bytes(data)
        return None
    
    @classmethod
    def create_by_type(cls, message_type: MessageType, 
                      start_byte: int = Message.START_BYTE,
                      end_byte: int = Message.END_BYTE) -> Optional[Message]:
        """
        Create a message by its type.
        
        Args:
            message_type: The type of message to create
            start_byte: Optional start byte override
            end_byte: Optional end byte override
            
        Returns:
            Specific Message subclass instance or None if invalid type
        """
        message_class = cls._message_registry.get(message_type)
        if message_class:
            return message_class(start_byte, message_type, end_byte)
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

# Usage examples:
if __name__ == "__main__":
    # Creating messages for sending
    pev_msg = MessageFactory.create_by_type(MessageType.PEV_SIM_CP)
    print(f"Created PEV message: {pev_msg.to_bytes().hex()}")
    
    # Creating messages from received bytes
    received_data = bytes([0xAA, 0x02, 0x55])  # EVSE message
    msg = MessageFactory.create_from_bytes(received_data)
    if msg:
        print(f"Received {msg.__class__.__name__}: {msg.to_bytes().hex()}")
    
    # Direct instantiation still works
    notify_msg = NotifyPEVChange()
    print(f"Direct creation: {notify_msg.to_bytes().hex()}")
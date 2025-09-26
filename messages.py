#from base_classes import ChargingState

class Message():
    def __init__(self, start_byte: int, decision_byte: int, end_byte: int):
        self.start_byte = start_byte
        self.decision_byte = decision_byte
        self.end_byte = end_byte

    def to_bytes(self) -> bytes:
        """
        Serialize the message to bytes for transmission.
        """
        return bytes([self.start_byte, self.decision_byte, self.end_byte])

    def check_message(self, data: bytes) -> bool:
        """
        Check if the received data matches the expected message format.
        """
        pass
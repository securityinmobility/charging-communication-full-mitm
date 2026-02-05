from abc import ABC

class CommunicationInterface(ABC):
    async def connect(self, port, baudrate):
        raise NotImplementedError()

    async def write(self, data):
        raise NotImplementedError()

    async def read(self, size):
        raise NotImplementedError()

    async def close(self):
        raise NotImplementedError()


import pytest
from mitm.interfaces.mock_usb import MockUsbInterface

@pytest.fixture
def mock_usb():
    """Returns a mock USB interface that doesn't need real hardware."""
    return MockUsbInterface()

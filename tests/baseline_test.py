"""
Minimal test setup - tests core message protocol without hardware
"""
import asyncio
import logging
from mitm.interfaces.mock_usb import MockUsbInterface
from mitm.mitm_board import MitMBoard
from mitm.messages import Message, MessageType, ChargingState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_test():
    """Most basic test: send one message, verify ACK"""
    
    # Setup
    usb = MockUsbInterface()
    board = MitMBoard(usb_interface=usb)
    await board.connect()
    
    # Test 1: Send message, expect ACK
    logger.info("Test 1: Send message and verify ACK")
    message = Message(
        messageType="PEV_SIM_CP",
        messageType_byte=MessageType.PEV_SIM_CP,
        decision_byte=ChargingState.B
    )
    
    status = await board.send_message(message, verbose=True)
    
    if status == 0:
        logger.info("✓ Test 1 PASSED: Message acknowledged")
    else:
        logger.error("✗ Test 1 FAILED: Message not acknowledged")
        return False
    
    # Test 2: Verify state changed
    logger.info("Test 2: Verify state change")
    if board.PEV_SIM_CP_state == ChargingState.B:
        logger.info("✓ Test 2 PASSED: State changed correctly")
    else:
        logger.error(f"✗ Test 2 FAILED: State is {board.PEV_SIM_CP_state}, expected {ChargingState.B}")
        return False
    
    board.close()
    logger.info("All tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(basic_test())
    exit(0 if success else 1)

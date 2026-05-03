import os
import logging
import time

from mitm.log import setup_logging
from mitm.interfaces.usb_interface import UsbInterface 
from mitm.interfaces.mock_usb import MockUsbInterface 
from mitm.mitm_board import MitMBoard
from mitm.messages import Message, MessageLogic, MessageType, ResponseType

if __name__ == "__main__":
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    log_file = os.environ.get("LOG_FILE", None)

    setup_logging(numeric_level, log_file)
    logger = logging.getLogger(__name__)

    try:
        logger.info("MITM Started")
        logger.info("Starting MitM program")
        
        usb_impl = os.environ.get("USB", "mock")
        
        if usb_impl == "mock":
            usb = MockUsbInterface(port="/dev/ttyUSB0", baudrate=9600, error_on_first_message=False)
        else:
            usb = UsbInterface(port=usb_impl, baudrate=9600)

        board = MitMBoard(usb_interface=usb)
        
        # Connect to board
        board.connect()
        board.set_pass_through(True)
        
        # set EVSE Sim CP to DC +12V
        base_EVSE_Sim_CP = Message(messageType="EVSE_SIM_CP", messageType_byte=MessageType.EVSE_SIM_CP, decision_byte=100)
        status = board.send_message(base_EVSE_Sim_CP, verbose=True, wait_response=0.3, message_label="base_EVSE_Sim_CP")
        
        # set PEV Sim PP to signal plug connected to EV
        base_EVSE_Sim_PP = Message(messageType="EVSE_SIM_PP", messageType_byte=MessageType.EVSE_SIM_PP, decision_byte=0x01)
        status = board.send_message(base_EVSE_Sim_PP, verbose=True, wait_response=0.3, message_label="base_EVSE_Sim_PP")

        # set PEV Sim to no EV connected - let the EV initialise the communication
        base_PEV_Sim_CP = Message(messageType="PEV_SIM_CP", messageType_byte=MessageType.PEV_SIM_CP, decision_byte=0x00)
        status = board.send_message(base_PEV_Sim_CP, verbose=True, wait_response=0.3, message_label="base_PEV_Sim_CP")

        # set EVSE Sim PP to signal a 20A cable - may be changed
        base_PEV_Sim_PP = Message(messageType="PEV_SIM_PP" , messageType_byte=MessageType.PEV_SIM_PP, decision_byte=0x00)
        status = board.send_message(base_PEV_Sim_PP, verbose=True, wait_response=0.3, message_label="base_PEV_Sim_PP")
        
        time.sleep(30) # pause main task
    except KeyboardInterrupt:
        logger.debug("MitM program terminated manually")
    finally:
        board.close()
        logger.info("MitM program terminated")
        logging.shutdown()

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
        logger.info("Starting testrun")
        
        usb_impl = os.environ.get("USB", "mock")
        
        if usb_impl == "mock":
            usb = MockUsbInterface(port="/dev/ttyUSB0", baudrate=9600, error_on_first_message=True)
        else:
            usb = UsbInterface(port=usb_impl, baudrate=9600)

        board = MitMBoard(usb_interface=usb)
        
        # Connect to board
        board.connect()
        board.set_pass_through(False)
        
        # Default setup messages
        base_PEV_Sim_CP = Message(messageType="PEV_SIM_CP", messageType_byte=MessageType.PEV_SIM_CP, decision_byte=0x00)
        base_PEV_Sim_PP = Message(messageType="PEV_SIM_PP" , messageType_byte=MessageType.PEV_SIM_PP, decision_byte=0x00)
        base_EVSE_Sim_CP = Message(messageType="EVSE_SIM_CP", messageType_byte=MessageType.EVSE_SIM_CP, decision_byte=0x00)
        base_EVSE_Sim_PP = Message(messageType="EVSE_SIM_PP", messageType_byte=MessageType.EVSE_SIM_PP, decision_byte=0x00)

        # Sim PEV messages
        state_B = Message(messageType="PEV_SIM_CP", messageType_byte=MessageType.PEV_SIM_CP, decision_byte=0x01)
        state_C = Message(messageType="PEV_SIM_CP", messageType_byte=MessageType.PEV_SIM_CP, decision_byte=0x03)
        cable_32A = Message(messageType="PEV_SIM_PP", messageType_byte=MessageType.PEV_SIM_PP, decision_byte=0x02)

        # Sim EVSE messages
        pwm_100 = Message(messageType="EVSE_SIM_CP", messageType_byte=MessageType.EVSE_SIM_CP, decision_byte=100)
        pwm_5 = Message(messageType="EVSE_SIM_CP", messageType_byte=MessageType.EVSE_SIM_CP, decision_byte=5)
        pwm_16 = Message(messageType="EVSE_SIM_CP", messageType_byte=MessageType.EVSE_SIM_CP, decision_byte=16)
        plug_connected = Message(messageType="EVSE_SIM_PP", messageType_byte=MessageType.EVSE_SIM_PP, decision_byte=0x01)
        stop_charging_request = Message(messageType="EVSE_SIM_PP", messageType_byte=MessageType.EVSE_SIM_PP, decision_byte=0x03)

        # Send default setup messages (everything disconnected)
        status = board.send_message(base_PEV_Sim_CP, verbose=True, wait_response=0.1, message_label="base_PEV_Sim_CP")
        status = board.send_message(base_PEV_Sim_CP, verbose=True, wait_response=0.15, message_label="base_PEV_Sim_CP") # second time because first on is never received
        status = board.send_message(base_PEV_Sim_PP, verbose=True, wait_response=0.1, message_label="base_PEV_Sim_PP")
        status = board.send_message(base_EVSE_Sim_CP, verbose=True, wait_response=0.1, message_label="base_EVSE_Sim_CP")
        status = board.send_message(base_EVSE_Sim_CP, verbose=True, wait_response=0.1, message_label="base_EVSE_Sim_PP")

        time.sleep(0.4)

        # Simulate PEV
        status = board.send_message(cable_32A, verbose=True, wait_response=0.1, message_label="cable_32A")
        status = board.send_message(state_B, verbose=True, wait_response=0.1, message_label="state_B")
        time.sleep(0.5)
        status = board.send_message(state_C, verbose=True, wait_response=0.1, message_label="state_C")
        time.sleep(0.3)
        # Resetup default setup
        status = board.send_message(base_PEV_Sim_CP, verbose=True, wait_response=0.1, message_label="base_PEV_Sim_CP") # second time because first on is never received
        status = board.send_message(base_PEV_Sim_PP, verbose=True, wait_response=0.1, message_label="base_PEV_Sim_PP")

        time.sleep(5)

        # Simulate EVSE (for high level communication)
        status = board.send_message(pwm_100, verbose=True, wait_response=0.1, message_label="pwm_100")
        status = board.send_message(plug_connected, verbose=True, wait_response=0.1, message_label="plug_connected")
        time.sleep(0.3)
        status = board.send_message(pwm_5, verbose=True, wait_response=0.1, message_label="pwm_5")
        time.sleep(1)
        status = board.send_message(stop_charging_request, verbose=True, wait_response=0.1, message_label="stop_charging_request")
        time.sleep(0.5)
        # Resetup default setup
        status = board.send_message(base_EVSE_Sim_CP, verbose=True, wait_response=0.1, message_label="base_EVSE_Sim_CP")
        status = board.send_message(base_EVSE_Sim_PP, verbose=True, wait_response=0.1, message_label="base_EVSE_Sim_PP")

        time.sleep(5)

        # Simulate EVSE (for low level communication)
        status = board.send_message(pwm_100, verbose=True, wait_response=0.1, message_label="pwm_100")
        status = board.send_message(plug_connected, verbose=True, wait_response=0.1, message_label="plug_connected")
        time.sleep(0.3)
        status = board.send_message(pwm_16, verbose=True, wait_response=0.1, message_label="pwm_16")
        time.sleep(1)
        status = board.send_message(stop_charging_request, verbose=True, wait_response=0.1, message_label="stop_charging_request")
        time.sleep(0.5)
        # Resetup default setup
        status = board.send_message(base_EVSE_Sim_CP, verbose=True, wait_response=0.1, message_label="base_EVSE_Sim_CP")
        status = board.send_message(base_EVSE_Sim_PP, verbose=True, wait_response=0.1, message_label="base_EVSE_Sim_PP")

        time.sleep(5)

    except KeyboardInterrupt:
        logger.debug("MitM program terminated manually")
    finally:
        board.close()
        logger.info("MitM program terminated")
        logging.shutdown()

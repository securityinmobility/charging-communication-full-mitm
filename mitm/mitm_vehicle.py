from base_classes import ElectricVehicle
from mitm_Board import MitMBoard
from messages import Message, MessageLogic, PP_State_PEVsim, ChargingState 
import logging

# get logger for this module
logger = logging.getLogger(__name__)

class MitMVehicle(ElectricVehicle):
    def __init__(self, mitm_board: MitMBoard):
        self.mitm_board = mitm_board

    def get_state(self) -> ChargingState:
        return self.mitm_board.PEV_SIM_CP_state

    def set_state(self, state: ChargingState):
        message = Message(messageType="PEV_SIM_CP", messageType_byte=MessageType.PEV_SIM_CP, decision_byte=state) 
        status = asyncio.run(self.mitm_board.send_message(message))

        if status == 0:
            self.mitm_board.PEV_SIM_CP_state = state
            logger.debug(f"Set PEV sim state to {state}")
        else:
            logger.error("Error setting PEV sim state")

    def set_pp(self, pp_state: PP_State_PEVsim):
        message = Message(messageType="PEV_SIM_PP", messageType_byte=MessageType.PEV_SIM_PP, decision_byte=pp_state)
        status = asyncio.run(self.mitm_board.send_message(message))

        if status == 0:
            self.mitm_board.PEV_SIM_PP_state = message.pp_state
            logger.debug(f"Set PEV sim PP state to {pp_state}")
        else:
            logger.error("Error setting PEV sim PP state")

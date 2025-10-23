from base_classes import ElectricVehicle
from mitm_Board import MitMBoard
from messages import ChargingState, PEVSimCPMessage, PEVSimPPMessage, PP_State_PEVsim
import logging

# get logger for this module
logger = logging.getLogger(__name__)

class MitMVehicle(ElectricVehicle):
    def __init__(self, mitm_board: MitMBoard):
        self.mitm_board = mitm_board

    def get_state(self) -> ChargingState:
        return self.mitm_board.PEV_SIM_CP_state

    def set_state(self, state: ChargingState):
        message = PEVSimCPMessage(state=state)
        self.mitm_board.send_message(message)

        result = asyncio.run(self.mitm_board.wait_for_response(0.5))
        if result.messageType_byte == message.ACK:
            self.mitm_board.PEV_SIM_CP_state = message.state
            logger.debug(f"Set PEV sim state to {state}")
        elif result is None:
            logger.error("No response received")
        elif result.messageType_byte == message.NACK:
            logger.error("Received NACK for setting PEV state")

    def set_pp(self, pp_state: PP_State_PEVsim):
        message = PEVSimPPMessage(pp_state=pp_state)
        self.mitm_board.send_message(message)

        result = asyncio.run(self.mitm_board.wait_for_response(0.5))
        if result.messageType_byte == message.ACK:
            self.mitm_board.PEV_SIM_PP_state = message.pp_state
            logger.debug(f"Set PEV sim PP state to {pp_state}")
        elif result is None:
            logger.error("No response received")
        elif result.messageType_byte == message.NACK:
            logger.error("Received NACK for setting PEV PP state")
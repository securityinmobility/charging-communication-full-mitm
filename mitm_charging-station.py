from base_classes import ChargingStation
from mitm_Board import MitMBoard
from messages import ChargingState, EVSESimCPMessage

import asyncio
import logging

# get logger for this modeule
logger = logging.getLogger(__name__)

class MitMChargingStation(ChargingStation):
    def __init__(self, mitm_board: MitMBoard):
        self.MitMBoard = mitm_board

    def get_state(self) -> ChargingState:
        """Get the current charging state of the PEV SIM."""
        return self.MitMBoard.PEV_SIM_CP_state

    def set_pwm_duty_cycle(self, dutycycle: float):
        message = EVSESimCPMessage(dutycycle=dutycycle)
        self.MitMBoard.send_message(message)
        result = asyncio.run(self.MitMBoard.wait_for_response(0.5))
        if result.messageType_byte == message.ACK:
            self.MitMBoard.EVSE_SIM_CP_state = result.dutycycle
            logger.debug(f"Set PWM duty cycle to {dutycycle}%")
        elif result is None:
            logger.error("No response received")
        elif result.messageType_byte == message.NACK:
            logger.error("Received NACK for setting PWM duty cycle")

    def get_pwm_duty_cycle(self) -> float:
        return self.MitMBoard.EVSE_SIM_CP_state

        

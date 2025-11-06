from base_classes import ChargingStation
from mitm_Board import MitMBoard
from messages import Message, MessageLogic, MessageType

import asyncio
import logging

# get logger for this module
logger = logging.getLogger(__name__)

class MitMChargingStation(ChargingStation):
    def __init__(self, mitm_board: MitMBoard):
        self.MitMBoard = mitm_board

    def get_state(self) -> ChargingState:
        """Get the current charging state of the PEV SIM."""
        return self.MitMBoard.PEV_SIM_CP_state

    def set_pwm_duty_cycle(self, dutycycle: int):
        """Set the PWM duty cycle for the EVSE SIM."""
        if dutycycle < 0 or dutycycle > 100:
            raise ValueError("Duty cycle must be between 0 and 100")

        message = Message(messageType="EVSE_SIM_CP", messageType_byte=MessageType.EVSE_SIM_CP, decision_byte=dutycycle)
        status = asyncio.run(self.MitMBoard.send_message(message))
        
        if status == 0:
            self.MitMBoard.EVSE_SIM_CP_state = result.dutycycle
            logger.debug(f"Set PWM duty cycle to {dutycycle}%")
        else: 
            logger.error("Error setting PWM duty cycle")

    def get_pwm_duty_cycle(self) -> float:
        return self.MitMBoard.EVSE_SIM_CP_state

        

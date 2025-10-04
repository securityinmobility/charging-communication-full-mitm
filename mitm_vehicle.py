from base_classes import ElectricVehicle
from mitm_Board import MitMBoard

class MitMVehicle(ElectricVehicle):
    def __init__(self, mitm_board: MitMBoard):
        self.MitMBoard = mitm_board


class ElectricVehicle(ABC):
    def get_state(self) -> ChargingState:
        """
        Get the current charging state according to the voltage measured between CP and PE
        """
        raise NotImplementedError()

    def set_state(self, state: ChargingState):
        """
        Set the diode/resistor communication (charging state)
        Can raise a NotImplementedError if switching to the given ChargingState is not supported/implemented
        """
        raise NotImplementedError()

    def set_cable_lock(self, locked: bool):
        """
        Lock or release the charging cable
        """
        raise NotImplementedError()

    def get_pwm_duty_cycle(self) -> float:
        """
        Get the current duty cycle of the PWM signal CP and PE in %
        """
        raise NotImplementedError()

    def get_max_charge_current(self) -> int:
        """
        Calculate the maximum charge current communicated by the charging
        station through the dutycycle of the PWM between CP and PE.
        The returned value is in Ampere.
        """
        dutycycle = self.get_pwm_duty_cycle()
        # we give a PWM tolerance based on the rounding error from float to int
        if dutycycle < 5.5 / 0.6 or dutycycle >= 80.5 / 2.5 + 64:
            raise ValueError(f"Unexpected dutycycle value of {dutycycle}%")

        if dutycycle < 85:
            return round(dutycycle * 0.6)
        else:
            return round((dutycycle - 64) * 2.5)

    def set_max_charge_current(self, resistance: Optional[ProximityPilotResitorValue]):
        """
        Set the maximum charge current communicated to the vehicle through the
        resistor between PP and PE.
        Giving None as a parameter shall turn off the resistor.

        This is only used for AC charging and most of the times already included
        in the charging cable.
        """
        raise NotImplementedError()
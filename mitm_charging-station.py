from base_classes import ChargingStation
from mitm_Board import MitMBoard

class MitMChargingStation(ChargingStation):
    def __init__(self, mitm_board: MitMBoard):
        self.MitMBoard = mitm_board

    
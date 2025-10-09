from base_classes import ElectricVehicle
from mitm_Board import MitMBoard

class MitMVehicle(ElectricVehicle):
    def __init__(self, mitm_board: MitMBoard):
        self.mitm_board = mitm_board

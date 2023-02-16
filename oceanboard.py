from board import Board
from ship import Ship

'''
The Ocean Board is the portion of the Battleship Unit that holds
ships that the player had placed and keeps track of hits upon each
ship that the opponent has guessed correctly.
'''
class OceanBoard(Board):

    def __init__(self, rsize: int, csize: int):
        # call parent's __init__
        # TODO
        self.ships = []

    # return False if ship could not be placed at r, c
    #    either r, c are illegal
    #    or ship is too big to be placed there
    #    or another ship is already there
    # Modify 'ship' with the given (r, c) and orientation
    # Add 'ship' to the the OceanBoard's list of 'ships' if placed successfully
    def placeShip(self, ship: Ship, r: int, c: int, orientation: str) -> bool:
        # TODO
        return False

    # are all 'ships' in the OceanBoard sunk?
    def allShipsSunk(self):
        # TODO
        return False

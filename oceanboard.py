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
        super().__init__(rsize, csize)
        self.ships = []

    # return False if ship could not be placed at r, c
    #    either r, c are illegal
    #    or ship is too big to be placed there
    #    or another ship is already there
    # Modify 'ship' with the given (r, c) and orientation
    # Add 'ship' to the the OceanBoard's list of 'ships' if placed successfully
    def placeShip(self, ship: Ship, r: int, c: int, orientation: str) -> bool:
        if r < 0 or r >= self.rowSize() or c < 0 or c >= self.colSize():
            return False
        if orientation == 'h':
            if c + ship.getSize() > self.colSize():
                
                return False
            for i in range(ship.getSize()):
                if self.getPiece(r,c+i) is not None:
                    
                    print(f'{self.getPiece(r,c+i)}')
                    return False
            for i in range(ship.getSize()):
                self.putPiece(ship.getType()[0], r,c+i) 
                ship.setLocation(r+1, c+1) #used to be c+i
        elif orientation == 'v':
            if r + ship.getSize() > self.rowSize():
                
                return False
            for i in range(ship.getSize()):
                if self.getPiece(r+i,c) is not None:
                    
                    return False
            for i in range(ship.getSize()):
                self.putPiece(ship.getType()[0], r+i,c) 
                ship.setLocation(r+1, c+1) # used to be r+i
                ship.setHorizontal(False)
        else:
            
            return False
        self.ships.append(ship)
        return True

    # are all 'ships' in the OceanBoard sunk?
    def allShipsSunk(self):
        for ship in self.ships:
            if not ship.isSunk():
                return False
        return True

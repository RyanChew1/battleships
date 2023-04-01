from board import Board
from ship import Ship


class OceanBoard(Board):

    def __init__(self, rsize: int, csize: int):
        # call parent's __init__
        super().__init__(rsize, csize)
        self.ships = []


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

    def allShipsSunk(self):
        for ship in self.ships:
            if not ship.isSunk():
                return False
        return True

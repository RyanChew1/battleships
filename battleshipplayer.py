from oceanboard import OceanBoard
from targetboard import TargetBoard
from letter import Letter
from ship import Ship
from setting import Setting

class BattleshipPlayer:

    def __init__(self, name: str, rsize=10, csize=10):        
        self.name = name
        self.score = 0

        self.ocean = OceanBoard(rsize, csize)
        self.target = TargetBoard(rsize, csize)

        self.rsize = rsize
        self.csize = csize

    def getName(self) -> str:
        return self.name

    def getOcean(self) -> OceanBoard:
        return self.ocean

    def getTarget(self) -> TargetBoard:
        return self.target

    def getScore(self) -> int:
        return self.score
    

    def shotAt(self, row: int, col: int) -> tuple:
        hit = False
        sunk = False
        
        if self.ocean.getPiece(int(row),int(col)-1) is not None:
                ship = self.ocean.getPiece(int(row), int(col)-1)
                for i in self.ocean.ships:
                            loc = i.getLocation()
                            h = i.isHorizontal()
                            size = i.getSize()
                        
                            squares = []
                            
                            for j in range(size):
                                if h:
                                    squares.append((loc[0],loc[1]+j))
                                else:
                                    squares.append((loc[0]+j,loc[1]))
                        
                            if (int(row)+1,int(col)) in squares:
                                hitShip = i
                    
        print('')
        if hitShip.isHitAt(int(row),int(col)-1):
            # Already Shot
            return (False, False, "shot")
        hitShip.markHitAt(int(row),int(col))
        
        hit = True

        if hitShip.isSunk():
            sunk = True
        
        if hit:
           return (hit, sunk, hitShip.getType()) 
        return (False, False, "")


    def updateScore(self, num: int) -> None:
        self.score += num


    def placeShip(self, ship: Ship, row, col, orientation: str) -> bool:
        # mapping = {
        #     'a':0,
        #     'b':1,
        #     'c':2,
        #     'd':3,
        #     'e':4,
        #     'f':5,
        #     'g':6,
        #     'h':7,
        #     'i':8,
        #     'j':9
        # }
        # letter = loc[0]
        # if type(loc) == str:


        return self.ocean.placeShip(ship, int(row), int(col)-1, orientation)


    def shipAt(self, r: int, c: int) -> Ship:
        return self.ocean.getPiece(r, c)

    def allShipsSunk(self) -> bool:
        return all([i.isSunk() for i in self.ocean.ships])

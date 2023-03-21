from oceanboard import OceanBoard
from targetboard import TargetBoard
from letter import Letter
from ship import Ship
from setting import Setting

class BattleshipPlayer:
    '''
    Models the Battleship Player
      player = BattleshipPlayer("Joe")    # default 10x10 board

    State Variables
      name (str) - the name of the player
      score (int) - the score of the player
      ocean (OceanBoard) - the board which contains all of the ships
      target (TargetBoard) - the board which contains all the shots made
    '''
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
    
    ### DO NOT MODIFY ABOVE METHODS ###

    #### MODIFY BELOW ####
    ### Add the following methods below and any others you may find useful ###

    # '''
    # loc: grid location like 'a1' or 'j10'
    # orientation: 'h' or 'v' for horizontal or vertical
    # return: True if ship was successfully placed
    # '''
    # def placeShip(self, ship: Ship, loc: str, orientation: str) -> bool:
    #     if isinstance(loc, str):
    #         row = ord(loc[0]) - 97
    #         col = int(loc[1:]) - 1
    #     else:
    #         row, col = loc
    #     return self.ocean.placeShip(ship, (row, col), orientation)

    '''
    Returns the ship at the specified (row, col) location on the player's OceanBoard
    '''
    '''
    Process the shot at (r, c) and return (hit, sunk, name)
      - Determine if there is a hit
      - Check if the ship is sunk
      - Get the name of the ship (if there is a hit)
      - Mark the ship as being hit
    '''
    def shotAt(self, row: int, col: int) -> tuple:
        hit = False
        sunk = False
        hitShip = None
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
        if hitShip:
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

    '''
    Registers a hit on the TargetBoard at the specified (row, col) location
    '''
    def markTargetHit(self, r: int, c: int) -> None:
        self.target.markHit(r, c)

    def markTargetMiss(self, r: int, c: int) -> None:
        self.target.markMiss(r, c)

    '''
    Resets both the ocean and target board so that game could
    be restarted
    '''
    def resetUnit(self) -> None:
        self.ocean = OceanBoard(self.rsize, self.csize)
        self.target = TargetBoard(self.rsize, self.csize)

    '''
    Adds num to the score
    '''
    def updateScore(self, num: int) -> None:
        self.score += num

    '''
    loc: grid location like 'a1' or 'j10'
    orientation: 'h' or 'v' for horizontal or vertical
    return: True if ship was successfully placed
    '''
    def placeShip(self, ship: Ship, loc: str, orientation: str) -> bool:
        mapping = {
            'a':0,
            'b':1,
            'c':2,
            'd':3,
            'e':4,
            'f':5,
            'g':6,
            'h':7,
            'i':8,
            'j':9
        }
        letter = loc[0]
        if type(loc) == str:
            try:
                row, col = mapping[letter], loc[1:]
            except:
                return False
        else:
            row, col = loc
        if not col.isnumeric():
            return False
        return self.ocean.placeShip(ship, int(row), int(col)-1, orientation)

    '''
    r, c: integer values for row and column
    return: Ship object at location (r, c) in ocean or None if no ship is located
    '''
    def shipAt(self, r: int, c: int) -> Ship:
        return self.ocean.getPiece(r, c)

    def allShipsSunk(self) -> bool:
        return all([i.isSunk() for i in self.ocean.ships])
from oceanboard import OceanBoard
from targetboard import TargetBoard
from letter import Letter
from ship import Ship

class BattleshipPlayer:

    '''
    Models the Battleship Player
      player = Battleship("Joe")    # default 10x10 board

    State Variables
      name (str) - the name of the player
      score (int) - the score of the player
      ocean (OceanBoard) - the board which contains all of the ships
      target (TargetBoard) - the board whih contains all the shots made
    '''
                             # optional parameters default is 10x10
    def __init__(self, name: str, rsize=10, csize=10):
        self.name = name
        self.score = 0

        self.ocean = OceanBoard(rsize, csize)
        self.target = TargetBoard(rsize, csize)

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

    '''
    loc: grid location like 'a1' or 'j10'
    orientation: 'h' or 'v' for horizontal or vertical
    return: True if ship was successfully placed
    '''
    def placeShip(self, ship: Ship, loc: str, orientation: str) -> bool:
        # TODO
        return False

    '''
    Process the shot at (r, c) and return (hit, sunk, name)
      - Determine if there is a hit
      - Check if the ship is sunk
      - Get the name of the ship (if there is a hit)
      - Mark the ship as being hit
    '''
    def shotAt(self, r: int, c: int) -> bool:
        # TODO
        return (False, False, "")

    def markTargetHit(self, r: int, c: int) -> None:
        # TODO
        pass

    def markTargetMiss(self, r: int, c: int) -> None:
        # TODO
        pass

    '''
    Resets both the ocean and target board so that game could
    be restarted
    '''
    def resetUnit(self) -> None:
        # TODO
        pass

    '''
    Adds num to the score
    '''
    def updateScore(self, num: int) -> None:
        # TODO
        pass

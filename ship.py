#=============================================================================
# Models one of the plastic ships in the Battleship game
# The plastic ships have 2-5 holes in them depending on the size of the ship.
# When a hit is registered, a red peg is placed in the plastic hole.
# 
# The class has the following attributes:
# 
#    type (str) - like "Cruiser"
#    size (int) - 3
#    status (list) - [0, 0, 0] to model the plastic holes that get filled with red pegs
#    loc (int, int) - the row, col location of the ship - ex. (3, 5)
#    horizontal (bool) - boolean if horizontal in orientation - ex. True
# 
#    In the above example, the ship is a "Cruiser" and occupies (3, 5), (3, 6), (3, 7)
#    If it were vertical instead, the ship would occupy (3, 5), (4, 5) and (5, 5)
#
# Methods
#    markHitAt(r, c) - modify the status of the ship to a 'hit' at (r, c) - "fill in the
#                      plastic hole with a red peg"
#    isHitAt(r, c) - is the a "red peg" at (r, c)?
#    isSunk() - the entire ship is sunk - all the status[] are 'hit's (i.e. filled with "red pegs")
#=============================================================================
class Ship:
    def __init__(self, type: str, size: int):
        '''
        Constructor
        type - Name of the ship
        size - how many pegs are in the ship
        '''
        self.type = type
        self.size = size
        self.status = [0 for _ in range(size)]  # models the plastic pegs marking a 'hit'
        self.loc = (0, 0)                       # default initialization
        self.horizontal = True                  # default initialization


    def getType(self) -> str:
        return self.type


    def getSize(self) -> int:
        return self.size


    # r, c valid numbers are 0 - 9 representing rows A - J and columns 1 - 10
    # Assume that r and c are valid
    def setLocation(self, r: int, c: int):
        self.loc = (r, c)

    def getLocation(self):
        return self.loc


    def setHorizontal(self, h: bool) -> None:
        self.horizontal = h


    def isHorizontal(self) -> bool:
        return self.horizontal


    def markHitAt(self, r: int, c: int) -> None:
        """
        Puts a red hit peg into the plastic ship the opponent shot at location (r,c)
        and updates the ship's status to indicate a hit at the corresponding location
        """
        index = c - self.loc[1] if self.horizontal else r - self.loc[0]
        self.status[index] = 1


    def isHitAt(self, r: int, c: int) -> bool:
        """
        Returns a boolean if the ship has been hit at this location already.
        It models if there is already a red peg in the ship at this location
        """
        index = c - self.loc[1] if self.horizontal else r - self.loc[0]
        return self.status[index] == 1


    def isSunk(self) -> bool:
        """
        Returns a boolean if the ship has been hit in all its locations
        """
        return all(status == 1 for status in self.status)

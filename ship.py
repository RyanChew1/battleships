
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

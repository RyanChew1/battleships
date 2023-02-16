from board import Board

#=============================================================================
# Battleship Target Board - this is the vertical board in the Battleship
# game that tracks hits and misses. In the game, when the player guesses and
# hits, a red peg is placed at the coordinate. If it misses, a white peg
# is placed at the coordinate.
# 
# Methods
#    markHit(r, c) - place a "red peg" at (r, c)
#    markMiss(r, c) - place a "white peg" at (r, c)
#    isHit(r, c) - is there a a "red peg" at (r, c)?
#    isEmpty(r, c) - is there any peg at (r, c)?
#=============================================================================
class TargetBoard(Board):

    def __init__(self, rsize: int, csize: int):
        super().__init__(rsize, csize)
        pass

    # place a "red peg" at (r, c)
    # "x" represents red peg
    def markHit(self, r: int, c: int) -> None:
        # put a red peg("x") at this location
        self.putPiece("x", r, c)
        pass

    # place a "white peg" at (r, c)
    # "o" represents white peg
    def markMiss(self, r: int, c: int) -> None:
        # put a white peg("o") at this location
        self.putPiece("o", r , c)
        pass

    # is there a "red peg" (a hit) at (r, c)?
    def isHit(self, r: int, c: int) -> bool:
        # if this location has a red peg("x") then return true
        if self.getPiece(r, c) == "x":
            return True
        pass

    # is there a any peg at (r, c)?
    def isEmpty(self, r: int, c: int) -> bool:
        # checks to see if there is a peg at this location
        if self.getPiece(r, c) == "x" or self.getPiece(r, c) == "o":
            return False
        pass


    
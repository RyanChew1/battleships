from board import Board



class TargetBoard(Board):

    def __init__(self, rsize: int, csize: int):
        super().__init__(rsize, csize)

    # place a "red peg" at (r, c)
    # "x" represents red peg
    def markHit(self, r: int, c: int) -> None:
        # put a red peg("x") at this location
        self.putPiece(u'\u001b[1m\u001b[38;5;196m{}\u001b[0m'.format("x"), r, c)

    # place a "white peg" at (r, c)
    # "o" represents white peg
    def markMiss(self, r: int, c: int) -> None:
        # put a white peg("o") at this location
        self.putPiece("o", r , c)

    # is there a "red peg" (a hit) at (r, c)?
    def isHit(self, r: int, c: int) -> bool:
        # if this location has a red peg("x") then return true
        if self.getPiece(r, c) == "x":
            return True
        return False

    # is there a any peg at (r, c)?
    def isEmpty(self, r: int, c: int) -> bool:
        # checks to see if there is a peg at this location
        if self.getPiece(r, c) is not None:
            return False
        return True


board = TargetBoard(10,10)


class Board:


    def __init__(self, rsize, csize):
        self.board = [ [ None for _ in range(csize) ] for _ in range(rsize) ]

    def putPiece(self, piece, r, c):
        self.board[r][c] = piece

    def getPiece(self, r, c):
        return self.board[r][c]

    def rowSize(self):
        return len(self.board)
    
    def colSize(self):
        return len(self.board[0])

    def resetBoard(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                self.board[r][c] = None

class subBoard(Board):
    def __init__(self, rsize: int, csize: int, db):
        # call parent's __init__
        super().__init__(rsize, csize)
        self.ships = []

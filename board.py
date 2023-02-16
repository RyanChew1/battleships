'''
Board

A generic 2D game board of a given dimension
At each square in the game board, a piece can be placed onto the board
The piece can be ANY type of item - strings, numbers, new GamePiece types...
The board is initialized to None at the very beginning
'''
class Board:

    ###### DO NOT EDIT ANYTHING IN THIS CLASS ######
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
    ###### DO NOT EDIT ANYTHING IN THIS CLASS ######

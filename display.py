from battleshipplayer import BattleshipPlayer
from letter import Letter
import subprocess

'''
Display - a class that handles the display of the Battleship game. It handles
all the printing and inputing for the game. It has some methods that help
move the cursor around for a more pleasant user game experience.
'''
class Display:

    #### DO NOT MODIFY LINES BELOW ####
    # move to 1, 1
    def home(self) -> None:
        print(u'\u001b[H', end='')

    # move cursor to line, col
    def moveTo(self, line, col) -> None:
        print(u'\u001b[' + f"{line};{col}H", end='')

    # move cursor to column col 
    def moveToColumn(self, col) -> None:
        print(u'\u001b[' + f"{col}G", end='')

    # clear to the end of line (keeping cursor at the current position)
    def clearToEndOfLine(self) -> None:
        print(u'\u001b[K', end='')

    # clear to the end of screen (keeping cursor at the current position)
    def clearToEndOfScreen(self) -> None:
        print(u'\u001b[J', end='')

    # clear screen and move to top left (1,1) of screen
    def clearScreen(self) -> None:
        self.home()
        self.clearToEndOfScreen()

    # return the proper column position for player X
    def playerColumn(self, playerNum: int) -> str:
        if playerNum== 2:
            column = 76
        else:
            column = 0
        return column

    # display message for player X
    def message(self, msg: str, playerNum = 1) -> None:
        self.moveToColumn(self.playerColumn(playerNum))
        print(msg)

    # ask for input from player X
    def ask(self, msg: str, playerNum = 1) -> str:
        self.moveToColumn(self.playerColumn(playerNum))
        return input(msg)

    def newLine(self):
        print()
    #### DO NOT MODIFY LINES ABOVE ####

    #### MODIFY BELOW ####
    # display the Ocean board of the player
    def displayOcean(self, player) -> None:
        print("displayOcean() to be implemented")

    # display both player 1 and player 2 ocean & target units
    def displayUnits(self, p1, p2) -> None:
        print("displayUnits() to be implemented")

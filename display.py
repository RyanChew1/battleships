from battleshipplayer import BattleshipPlayer
from letter import Letter
import subprocess
from ship import Ship

class Display:

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
        if playerNum == 2:
            column = 76
        else:
            column = 0
        return column

    # display message for player X
    def message(self, msg: str, playerNum=1) -> None:
        self.moveToColumn(self.playerColumn(playerNum))
        print(msg)

    # ask for input from player X
    def ask(self, msg: str, playerNum=1) -> str:
        self.moveToColumn(self.playerColumn(playerNum))
        return input(msg)

    def newLine(self):
        print()


    # display the Ocean board of the player
    def displayOcean(self, player: BattleshipPlayer) -> None:
        print("   ", end="")
        for i in range(10):
            print(f" {i+1} ", end="")
        print()
        row_header_map = {
            0:'a ',
            1:'b ',
            2:'c ',
            3:'d ',
            4:'e ',
            5:'f ',
            6:'g ',
            7:'h ',
            8:'i ',
            9:'j '
        }
        # print rows
        for row in range(10):
            # print row label
            print(f"{Letter(row_header_map[row],'white')}|", end="")
            for col in range(10):
                if player.ocean.getPiece(row,col) == None:
                    print(" . ", end="")
                else:
                    print(f" {player.ocean.getPiece(row,col)} ", end="")
            print("|")
        print()
    # display both player 1 and player 2 ocean & target units
    def displayUnits(self, player1, player2):
        # print(self.__border + self.__column_headers + "\n" + self.__border, end="")
        print('    Ocean \t \t \t \t       Target')
        print("   ", end="")
        
        for i in range(20):
            if i==9:
                print(f" {(i%10)+1}             ", end="")
            else:
                print(f" {(i%10)+1} ", end="")
            
        # for i in range(10):
        #     print(f" {i+1}  ", end="")
        print()
        row_header_map = {
            0:'a ',
            1:'b ',
            2:'c ',
            3:'d ',
            4:'e ',
            5:'f ',
            6:'g ',
            7:'h ',
            8:'i ',
            9:'j '
        }
        


        for row in range(10):
            # print row label
            #Ocean
            print(f"{Letter(row_header_map[row],'white')}|", end="")
            for col in range(10):
                if player1.ocean.getPiece(row,col) is not None:
                    print(f" {player1.ocean.getPiece(row,col)} ", end="")
                else:
                    print(f" . ", end="")
            print('|         ',end='')

            #target
            print(f"{Letter(row_header_map[row],'white')}|", end="")
            for col in range(10):
                if player1.target.getPiece(row,col) is not None:
                    print(f" {player1.target.getPiece(row,col)} ", end="")
                else:
                    print(f" . ", end="")
            print("|             ")

        self.ask("Press Enter to continue...")



# d = Display()
# p1 = BattleshipPlayer('r',10,10)
# p2 = BattleshipPlayer('c',10,10)

# p1.placeShip(Ship('Carrier',5),'a1','v')
# d.displayOcean(p1)
# p1.placeShip(Ship('Battleship',4),'a2','v')
# d.displayOcean(p1)
# p1.placeShip(Ship('Destroyer',3),'a3','v')
# d.displayOcean(p1)
# p1.placeShip(Ship('Submarine',3),'a4','v')
# d.displayOcean(p1)
# p1.placeShip(Ship('Patrol Boat',2),'a5','v')
# d.displayOcean(p1)

# p2.placeShip(Ship('Carrier',5),'a1','v')
# p2.placeShip(Ship('Battleship',4),'a2','v')
# p2.placeShip(Ship('Destroyer',3),'a3','v')
# p2.placeShip(Ship('Submarine',3),'a4','v')
# p2.placeShip(Ship('Patrol Boat',2),'a5','v')

# d.displayUnits(p1,p2)

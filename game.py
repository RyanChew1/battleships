from battleshipplayer import BattleshipPlayer
from ship import Ship
from display import Display
from setting import Setting
from letter import Letter

'''
Places the 5 ships onto the Ocean board of 'player'
Creates 5 ships, asks player where it wants them placed, and puts them into
the Ocean board.
'''
def initPlayer(d: Display, player: BattleshipPlayer) -> None:
    # TODO
    pass

'''
playerNumber calls a shot and p1/p2 player units are updated appropriately
return - True if all ships are sunk after the player's shot
'''
def turn(d: Display, p1: BattleshipPlayer, p2: BattleshipPlayer, playerNumber: int) -> bool:
    # TODO
    return False

def playBattleship(d: Display, settings: Setting) -> None:

    # ask for each player names
    pass # TODO

    # each player places their 5 ships

    # take turns between player 1 and 2 until one player sinks the other's ships

    # update the score

    # check if they want to play again

def main():
    d = Display()
    d.message(Letter('X', 'red'))  # example of writing a red X  (you can remove this...)
    d.message("Let's play Battleship!")

    settings = Setting()
    settings.setSetting('mode', 'basic')
    settings.setSetting('numplayers', 2)

    playBattleship(d, settings)

if __name__ == "__main__":
    main()
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
    ship_sizes = [5, 4, 3, 3, 2]
    ship_names = ['Carrier', 'Battleship', 'Destroyer', 'Submarine', 'Patrol Boat']
    for i in range(len(ship_sizes)):
        ship_size = ship_sizes[i]
        ship_name = ship_names[i]
        d.clearScreen()
        while True:
            d.displayOcean(player)
            position_str = d.ask(f"Where should the {ship_name} (size {ship_size}) be placed? ")
            orientation_str = d.ask("What orientation (h/v)? ")
            if position_str is None or not player.placeShip(Ship(ship_name, int(ship_size)), position_str, orientation_str ):
                d.message("Illegal placement, please try again")
                continue
            player.placeShip(Ship(ship_name, int(ship_size)), position_str, orientation_str)
            d.clearScreen()
            d.displayOcean(player)
            break



'''
playerNumber calls a shot and p1/p2 player units are updated appropriately
return - True if all ships are sunk after the player's shot
'''
def turn(d: Display, p1: BattleshipPlayer, p2: BattleshipPlayer, playerGuessing: int) -> bool:
    player = p1 if playerGuessing == 1 else p2
    opponent = p2 if playerGuessing == 1 else p1
    d.message(f"{player.getName()} shooting at {opponent.getName()}'s ships")
    d.message(f"\n{player.getName()}'s BOARDS: ")
    d.displayUnits(player,opponent)

    d.message(f"\n{opponent.getName()}'s BOARDS: ")
    d.displayUnits(opponent, player)
    d.message("\n")

    d.clearScreen()
    while True:
        
        guess = d.ask(f"{player.getName()}, which grid are you shooting? ")

        # get row, col of guess
        mapping = {
            'a':0,
            'b':1,
            'c':2,
            'd':3,
            'e':4,
            'f':5,
            'g':6,
            'h':7,
            'i':8,
            'j':9
        }
        if type(guess) == str and len(guess)>1:
            letter = guess[0]
            if not str(guess[1:]).isnumeric():
                return False
            try:
                row, col = mapping[letter], guess[1:]
            except:
                print('Invalid input! Turn lost!')
                return False
        else:
            break    
        if not player.target.isEmpty(int(row),int(col)):
            d.message("You have already shot here! Turn Lost!")
            return False
        else:
            (hit,sunk,shipName) = opponent.shotAt(row,col)
            
            if hit:

                d.message(f"You hit {opponent.getName()}'s {shipName}! \n")
                if sunk:
                    d.message(f"You sunk {opponent.getName()}'s {shipName}! \n")
                if opponent.allShipsSunk():
                    print("YES")
                    d.message(f"You sunk all of {opponent.getName()}'s ships! \n")
                    return True
                player.target.markHit(int(row),int(col)-1)
                opponent.ocean.putPiece(Letter(shipName[0].upper(), 'red'), int(row),int(col)-1)  # FIX THIS
            else:
                if shipName == 'shot':
                    d.message("You have already shot here! Turn Lost! \n")
                    return False
                d.message(f"You missed {opponent.getName()}'s ships.")
                player.target.markMiss(int(row),int(col)-1)
                opponent.ocean.putPiece(Letter('O', 'white'), int(row),int(col)-1) # FIX THIS
            break
    return False


def playBattleship(d: Display, settings: Setting) -> None:
    # Get player names and create BattleshipPlayer objects for each player
    players = []
    for i in range(2):
        name = input(f"Enter player {i+1} name: ")
        players.append(BattleshipPlayer(name))
        
    def battleshipGame():
        # Place ships for each player
        for player in players:
            initPlayer(d, player)
        
        # Play the game until one player sinks all of the opponent's ships
        winner = None
        while winner is None:
            for i in range(2):
                if turn(d, players[0], players[1], i+1):
                    winner = players[i]
                    break
        
        # Add one point to the winner and display the final scores
        winner.updateScore(1)
        d.clearScreen()
        d.message(f"{winner.getName()} wins!")
        for player in players:
            d.message(f"{player.getName()} score: {player.getScore()}")
        
        
        # Ask if players want to play again
        again = input("Play again? (y/n): ")
        if again.lower() == 'y':
            for player in players:
                player.resetUnit()
            battleshipGame()
    battleshipGame()


def main():
    d = Display()
    d.message("Let's play Battleship!")

    settings = Setting()
    settings.setSetting('mode', 'basic')
    settings.setSetting('numplayers', 2)

    playBattleship(d, settings)


if __name__ == "__main__":
    main()
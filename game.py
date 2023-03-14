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
    d.displayUnits(player,opponent)

    d.message(f"{opponent.getName()}'s boards: ")
    d.displayUnits(opponent, player)
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
            try:
                row, col = mapping[letter], guess[1:]
            except:
                print('Invalid input! Turn lost!')
                continue
        else:
            break    
        if not player.target.isEmpty(int(row),int(col)):
            d.message("You have already shot here! Turn Lost!")
        else:
            if opponent.ocean.getPiece(int(row),int(col)-1) is not None:
                ship = opponent.ocean.getPiece(int(row), int(col)-1)
                

                for i in opponent.ocean.ships:
                    loc = i.getLocation()
                    h = i.isHorizontal()
                    size = i.getSize()
                   
                    squares = []
                    
                    for j in range(size):
                        if h:
                            squares.append((loc[0],loc[1]+j))
                        else:
                            squares.append((loc[0]+j,loc[1]))
                
                    if (int(row)+1,int(col)) in squares:
                        hitShip = i
                    
                print('')
                if hitShip.isHitAt(int(row),int(col)-1):
                    d.message("You have already shot here! Turn Lost!")
                    continue
                hitShip.markHitAt(int(row),int(col))
                d.message(f"You hit {opponent.getName()}'s {hitShip.getType()}!")
                if opponent.allShipsSunk():
                    d.message(f"You sunk all of {opponent.getName()}'s ships!")
                    return True
                player.target.markHit(int(row),int(col)-1)
                opponent.ocean.putPiece(Letter(hitShip.getType()[0].upper(), 'red'), int(row),int(col)-1)  # FIX THIS
            else:
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
    winner.addPoint()
    d.clearScreen()
    for player in players:
        d.displayUnits(player.getName(), player.getOceanBoard(), player.getTargetBoard())
        d.message(f"{player.getName()} score: {player.getScore()}")
    d.message(f"{winner.getName()} wins!")
    
    # Ask if players want to play again
    again = input("Play again? (y/n): ")
    if again.lower() == 'y':
        for player in players:
            player.resetBoards()
        playBattleship(d, settings)


def main():
    d = Display()
    d.message("Let's play Battleship!")

    settings = Setting()
    settings.setSetting('mode', 'basic')
    settings.setSetting('numplayers', 2)

    playBattleship(d, settings)

if __name__ == "__main__":
    main()
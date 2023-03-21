from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
import mysql.connector
import random
import string
from battleshipplayer import BattleshipPlayer
from ship import Ship
from display import Display
from setting import Setting
from letter import Letter
import json
from threading import Thread
import time

app = Flask(__name__, template_folder='templates')
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

socketio = SocketIO(app, manage_session=False)

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="1234",
  database="battleship_log"
)
try:
    cur = mydb.cursor()
    query = 'DROP TABLE rooms'
    cur.execute(query)
    mydb.commit()
except:
    pass

try:
    query = '''
    CREATE TABLE rooms (
id INT AUTO_INCREMENT PRIMARY KEY,
roomcode VARCHAR(255) UNIQUE NOT NULL,
numUsers INT,
userOne VARCHAR(255),
userTwo VARCHAR(255),
pOneTarget VARCHAR(1000),
pTwoTarget VARCHAR(1000),
pOneOcean VARCHAR(1000),
pTwoOcean VARCHAR(1000),
turn INT
);

    '''
    cur.execute(query)
    mydb.commit()
except:
    pass



app.secret_key = 'secret_key'


turn = 1

# redirect
@app.route('/', methods=['GET', 'POST'])
def index():
    session['room'] = session.get('room')
    print(session)
    if 'username' in session:
        session['room'] =None
        return render_template('logged_in.html',visibility = 'none', session = session,vis2 = 'none')
    else:
        return render_template('index.html')

# signup and login
@app.route("/signup.html", methods=["GET", "POST"])
def signup():
    
    if request.method == "POST":
        cursor = mydb.cursor()
        username = request.form["username"]
        password = request.form["password"]


        cursor.execute("""
            SELECT * FROM users
            WHERE username = %s
            """, (username,))

        if cursor.fetchone():
            return render_template("signup.html", visibility='block')
            
        else:
            insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(insert_query, (username, password))
            mydb.commit()
            return render_template("logged_in.html", visibility='none')
    return render_template("signup.html", visibility='none')


@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cursor = mydb.cursor()
        # Get the username and password from the form

        username = request.form['username']
        password = request.form['password']
        # Check if the username and password are correct
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        
        if result:
            # If the username and password are correct, redirect to the homepage
            session['username'] = username
            return render_template("logged_in.html", visibility='none',vis2 = 'none')
        elif password!='':
            # If the username and password are incorrect, show an error message
            session.clear()
            return render_template("login.html", visibility = 'block')
    
    return render_template('login.html', visibility = 'none')


# main page
@app.route('/logged_in.html', methods=['GET', 'POST'])
def logout():
    session.clear()
    username = None
    return redirect(url_for('index'))



mapSize = {
    'A':1,
    'B':2,
    'C':3,
    'D':4,
    'E':5,
    'F':6,
    'G':7,
    'H':8,
    'I':9,
    'J':10
}



# # START
def dropEmpty():
    cursor = mydb.cursor()
    query = "DELETE FROM rooms WHERE numUsers = 0"
    cursor.execute(query)
    mydb.commit()

def createNew(room):
    cursor = mydb.cursor()
    query = "INSERT INTO rooms (roomcode,numUsers, userOne, userTwo) VALUE (%s, %s, %s, %s)"
    cursor.execute(query,(room, 1,session['username'],None))
    mydb.commit()
    query = "UPDATE rooms SET turn = %s WHERE roomcode=%s"
    cursor.execute(query,(1,room))
    mydb.commit()
def adduser(room):
    cursor = mydb.cursor()
    queryNum = "SELECT numUsers FROM rooms WHERE roomcode = %s"
    cursor.execute(queryNum, (room,))
    num = cursor.fetchone()[0]
    print(f"num: {num}")
    query = "UPDATE rooms SET numUsers = %s WHERE roomcode=%s"
    cursor.execute(query,(num+1,room))
    query = "UPDATE rooms SET userTwo = %s WHERE roomcode=%s"
    cursor.execute(query,(session['username'], room))

    
    mydb.commit()

def removeuser(room):
    cursor = mydb.cursor()
    session['room'] = None
    queryNum = "SELECT numUsers FROM rooms WHERE roomcode = %s"
    cursor.execute(queryNum, (room,))
    print(f'ROOOM: {room}')
    num = cursor.fetchone()
    if num is not None:
        num = num[0]
        print(f' NUM {num}')
        query = "UPDATE rooms SET numUsers = %s WHERE roomcode=%s"
        cursor.execute(query,(num-1,room))
        mydb.commit()




@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if(request.method=='POST'):
        cursor = mydb.cursor()
        room = request.form['room']
        if session.get('room')==room:
            return render_template('logged_in.html', session = session,visibility = 'none',vis2 = 'none')

        query = "SELECT numUsers FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (room,))
        result = cursor.fetchone()
        if result:
            if result[0]<2:
                session['room'] = room
                adduser(room)
                return render_template('logged_in.html', session = session,visibility = 'none',vis2 = 'block')
            else:
                return render_template('logged_in.html', session = session, visibility='none',vis2 = 'block')
        else:
            return render_template('logged_in.html', session = session,visibility = 'block',vis2 = 'none')

        

@app.route('/create', methods=['GET', 'POST'])
def create():
    session['turn'] = 1
    if(request.method=='POST'):
        cursor = mydb.cursor()
        found = False
        if session.get('room') is not None:
            removeuser(session.get('room'))
            dropEmpty()
            session['room'] = None


        while not found:
            room = ''
            for i in range(8):
                room+=random.choice(string.ascii_uppercase)
            
            query = "SELECT numUsers FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (room,))
            result = cursor.fetchone()


            if result:
                pass
            else:
                found=True
        dropEmpty()
        session['room'] = room

        createNew(room)

        return render_template('logged_in.html', session = session,visibility = 'none',vis2 = 'none')


@socketio.on('join', namespace='/chat')
def join(message):
    session['turn']=1
    room = session.get('room')
    if session.get('username') is not None:
        join_room(room)
        emit('status', {'msg':  session.get('username') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    emit('message', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)



# SUBRTRACT USER
@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    if room:
        removeuser(room)
        leave_room(room)
    

    
    dropEmpty()
    session['room'] = None
    emit('status', {'msg': username + ' has left the room.'}, room=room)



global allPlaced
allPlaced = False
@app.route('/processUserInfo/<string:userInfo>', methods=['POST'])
def processUserInfo(userInfo):
    userInfo = json.loads(userInfo)
    print(type(userInfo))
    print('RECEIVED')
    
    carrier = userInfo['Carrier']
    battleship = userInfo['Battleship']
    destroyer = userInfo['Destroyer']
    submarine = userInfo['Submarine']
    patrol = userInfo['Patrol Boat']

    print(f"CARRIER: {carrier}")
    print(f"BATTLESHIP: {battleship}")
    print(f"DESTROYER: {destroyer}")
    print(f"SUBMARINE: {submarine}")
    print(f"PATROL BOAT: {patrol}")

    player = session['player']
    opponent = session['opponent']


    carrierO = 'h' if carrier[2] else 'v'
    battleshipO = 'h' if battleship[2] else 'v'
    destroyerO = 'h' if destroyer[2] else 'v'
    submarineO = 'h' if submarine[2] else 'v'
    patrolO = 'h' if patrol[2] else 'v'


    player.placeShip(Ship('Carrier',5), carrier[0]-1,carrier[1],carrierO)
    player.placeShip(Ship('Battleship', 4), battleship[0]-1,battleship[1],battleshipO)
    player.placeShip(Ship('Destroyer', 3), destroyer[0]-1,destroyer[1],destroyerO)
    player.placeShip(Ship('Submarine', 3), submarine[0]-1,submarine[1],submarineO)
    player.placeShip(Ship('Patrol Boat', 2), patrol[0]-1,patrol[1],patrolO)

    isP1 = True
    if session['room']:
            cursor = mydb.cursor()
            query = "SELECT * FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (session['room'],))
            results = cursor.fetchone()
            
            isP1= False if results[4]==session['username'] else True

    

    board_str = ','.join(str(item) for row in player.ocean.board for item in row)
    none_board_str = ','.join(str(None) for row in player.ocean.board for item in row)
    global board_dict
    board_dict = {}
    global board_dict2
    board_dict2 = {}
    mapping = {
            0:'a',
            1:'b',
            2:'c',
            3:'d',
            4:'e',
            5:'f',
            6:'g',
            7:'h',
            8:'i',
            9:'j'
        }
    if isP1:
        if session['room']:
                cursor = mydb.cursor()
                query = "UPDATE rooms SET pOneOcean = %s WHERE roomcode=%s"
                cursor.execute(query, (board_str,session['room']))
                mydb.commit()
                cursor = mydb.cursor()
                query = "UPDATE rooms SET pOneTarget = %s WHERE roomcode=%s"
                cursor.execute(query, (none_board_str,session['room']))
                mydb.commit()
                cursor = mydb.cursor()
                query = "UPDATE rooms SET pTwoTarget = %s WHERE roomcode=%s"
                cursor.execute(query, (none_board_str,session['room']))
                mydb.commit()
                for rowI,row in enumerate(player.ocean.board):
                    for colI, col in enumerate(row):
                        ind = str(mapping[rowI])+str(colI+1)
                        board_dict[ind] = col
    else: 
        if session['room']:
            print('P2')
            print(session['room'])
            cursor = mydb.cursor()
            query = "UPDATE rooms SET pTwoOcean = %s WHERE roomcode=%s"
            cursor.execute(query, (board_str,session['room'])) 
            mydb.commit()
            cursor = mydb.cursor()
            query = "UPDATE rooms SET pOneTarget = %s WHERE roomcode=%s"
            cursor.execute(query, (none_board_str,session['room']))
            mydb.commit()
            cursor = mydb.cursor()
            query = "UPDATE rooms SET pTwoTarget = %s WHERE roomcode=%s"
            cursor.execute(query, (none_board_str,session['room']))
            mydb.commit()
            for rowI,row in enumerate(player.ocean.board):
                    for colI, col in enumerate(row):
                        ind = str(mapping[rowI])+str(colI+1)
                        board_dict2[ind] = col
    global allPlaced
    
    allPlaced = True
    return 'SUCCESSs'
    
@app.route('/displayOcean')
def get_text():
    isP1 = True
    if session['room']:
            cursor = mydb.cursor()
            query = "SELECT * FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (session['room'],))
            results = cursor.fetchone()
            
            isP1= False if results[4]==session['username'] else True
    if isP1:
        return jsonify(board_dict)
    else:
        return jsonify(board_dict2)

# game modes
global playerBoard
playerBoard = []
global opponentBoard
opponentBoard = []



@app.route('/gameplay')
def gameplay():
    global playerBoard
    global opponentBoard
    playerBoard = []
    opponentBoard = []
    isP1 = True
    if session['room']:
            cursor = mydb.cursor()
            query = "SELECT * FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (session['room'],))
            results = cursor.fetchone()
            
            isP1= False if results[4]==session['username'] else True

    player = session['player']
    opponent = session['opponent']


    # decrypt sql string
    if session['turn']==1:
        cursor = mydb.cursor()
        query = "SELECT pOneOcean FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]

        resultsLi = results.split(",")


        playerBoard = []
        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            playerBoard.append(sublist)



        cursor = mydb.cursor()
        query = "SELECT pTwoOcean FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]

        resultsLi = results.split(",")


        opponentBoard = []
        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            opponentBoard.append(sublist)

    else:
        cursor = mydb.cursor()
        query = "SELECT pTwoOcean FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]

        resultsLi = results.split(",")

        playerBoard = []
        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            playerBoard.append(sublist)


        cursor = mydb.cursor()
        query = "SELECT pOneOcean FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]
        resultsLi = results.split(",")



        opponentBoard = []
        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            opponentBoard.append(sublist)

    return 'hi'

@app.route('/displayTarget')
def get_target():
    global playerTarget
    global opponentTarget
    global opponentBoard
    global playerBoard
    global opponentBoard2
    global playerBoard2
    playerTarget = []
    opponentTarget = []
    isP1 = True
    if session['room']:
            cursor = mydb.cursor()
            query = "SELECT * FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (session['room'],))
            results = cursor.fetchone()
            
            isP1= False if results[4]==session['username'] else True
    if isP1:
        cursor = mydb.cursor()
        query = "SELECT pOneTarget FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]

        resultsLi = results.split(",")
        playerTarget = []
        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            playerTarget.append(sublist)



        cursor = mydb.cursor()
        query = "SELECT pTwoTarget FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]

        resultsLi = results.split(",")

        opponentTarget = []
        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            opponentTarget.append(sublist)

    else:
        cursor = mydb.cursor()
        query = "SELECT pTwoTarget FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]

        resultsLi = results.split(",")
        playerTarget = []
        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            playerTarget.append(sublist)


        cursor = mydb.cursor()
        query = "SELECT pOneTarget FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]
        resultsLi = results.split(",")

        opponentTarget = []
        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            opponentTarget.append(sublist)




    isP1 = True
    if session['room']:
            cursor = mydb.cursor()
            query = "SELECT * FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (session['room'],))
            results = cursor.fetchone()
            
            isP1= False if results[4]==session['username'] else True

    mapping = {
            0:'a',
            1:'b',
            2:'c',
            3:'d',
            4:'e',
            5:'f',
            6:'g',
            7:'h',
            8:'i',
            9:'j'
        }


    opponentBoard2 = [i for i in playerBoard]

    target_dict = {}
    target_li = session['player'].target.board

    for rowI, row in enumerate(target_li):
        for colI, col in enumerate(row):
            row_str = mapping[rowI]
            col_str = str(colI+1)
            if col == '\x1b[1m\x1b[38;5;196mx\x1b[0m':
                col = opponentBoard2[rowI][colI]

            target_dict[row_str+col_str+'T'] = col
    return jsonify(target_dict)





@app.route('/updateOcean')
def updateOcean():
    global playerTarget
    global opponentTarget
    playerTarget = []
    opponentTarget = []
    isP1 = True
    if session['room']:
            cursor = mydb.cursor()
            query = "SELECT * FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (session['room'],))
            results = cursor.fetchone()
            
            isP1= False if results[4]==session['username'] else True

    if isP1:
        cursor = mydb.cursor()
        query = "SELECT pTwoTarget FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]

        resultsLi = results.split(",")

        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            playerTarget.append(sublist)


        cursor = mydb.cursor()
        query = "SELECT pOneTarget FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]
        resultsLi = results.split(",")


        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            opponentTarget.append(sublist)


        cursor = mydb.cursor()
        query = "SELECT pTwoTarget FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]

        resultsLi = results.split(",")


        opponentBoard = []
        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            opponentBoard.append(sublist)
    else:
        cursor = mydb.cursor()
        query = "SELECT pOneTarget FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]

        resultsLi = results.split(",")

        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            playerTarget.append(sublist)



        cursor = mydb.cursor()
        query = "SELECT pTwoTarget FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()[0]

        resultsLi = results.split(",")


        for i in range(10):
            start = i* len(resultsLi)//10
            end = (i+1) * len(resultsLi)//10
            sublist = resultsLi[start:end]
            opponentTarget.append(sublist)

    mapping = {
            0:'a',
            1:'b',
            2:'c',
            3:'d',
            4:'e',
            5:'f',
            6:'g',
            7:'h',
            8:'i',
            9:'j'
        }

    target_dict = {}


    target_li = playerTarget
    for rowI, row in enumerate(target_li):
        for colI, col in enumerate(row):
            row_str = mapping[rowI]
            col_str = str(colI+1)
            target_dict[row_str+col_str] = col
    return jsonify(target_dict)

@app.route('/updateTurn')
def updateTurn():
    cursor = mydb.cursor()
    query = "SELECT turn FROM rooms WHERE roomcode = %s"
    cursor.execute(query, (session['room'],))
    session['turn'] = cursor.fetchone()[0]
    print(session['turn'])
    return 'FEOHSOIEFHSOI'

@app.route('/processShot/<string:userInfo>', methods=['POST'])
def processShot(userInfo):
    global winner
    
    winner = False
    

    mapping = {
            0:'a',
            1:'b',
            2:'c',
            3:'d',
            4:'e',
            5:'f',
            6:'g',
            7:'h',
            8:'i',
            9:'j'
        }
    isP1 = True
    if session['room']:
            cursor = mydb.cursor()
            query = "SELECT * FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (session['room'],))
            results = cursor.fetchone()
            if results is not None:
                isP1= False if results[4]==session['username'] else True

    turn = session['turn']

    print(f"PLAYER 1: {isP1}")
    print(f'TURN: {turn}')


    if isP1 and turn==1:
        go = True
    elif not isP1 and turn==2:
        go = True
    else:
        go=False
    print(allPlaced and go)

    

    if allPlaced and go:

        if turn==1:
            session['turn'] =2
        else:
            session['turn']=1

        cursor = mydb.cursor()
        query = "UPDATE rooms SET turn = %s WHERE roomcode = %s"
        cursor.execute(query, (session['turn'],session['room']))
        mydb.commit()

        userInfo = json.loads(userInfo)

        print('RECEIVED')
        print(f"ROW: {userInfo['row']}")
        print(f"COL: {userInfo['col']}")
    
        


        row = int(userInfo['row'])
        col = int(userInfo['col'])


        if opponentBoard[row-1][col-1] != 'None':
            session['player'].target.markHit(row-1,col-1)
            
            print(f'HIT SHIP AT {row}, {col}')
            

        else:
            session['player'].target.markMiss(row-1,col-1)

        print(f"IS P1: {isP1}")
        print(f"OPPONENT BOARD: {opponentBoard}")
        print(f"TARGET BOARD: {session['player'].target.board}")

        
        board_str = ','.join(str(item) for row in session['player'].target.board for item in row)
        if isP1 :
            if session['room']:
                    cursor = mydb.cursor()
                    query = "UPDATE rooms SET pOneTarget = %s WHERE roomcode=%s"
                    cursor.execute(query, (board_str,session['room']))
                    mydb.commit()
                    for rowI,row in enumerate(session['player'].ocean.board):
                        for colI, col in enumerate(row):
                            ind = str(mapping[rowI])+str(colI+1)
                            board_dict[ind] = col
        elif not isP1: 
            if session['room']:

                print(session['room'])
                cursor = mydb.cursor()
                query = "UPDATE rooms SET pTwoTarget = %s WHERE roomcode=%s"
                cursor.execute(query, (board_str,session['room'])) 
                mydb.commit()
                for rowI,row in enumerate(session['player'].ocean.board):
                        for colI, col in enumerate(row):
                            ind = str(mapping[rowI])+str(colI+1)
                            board_dict2[ind] = col
    return 'YES'



@app.route('/standard.html', methods=['GET', 'POST'])
def standard():
    turn = 1
    ships = {
        'Carrier':5,
        'Battleship':4,
        'Destroyer':3,
        'Submarine':3,
        'Patrol Boat':2
    }
    isP1 = True
    if session['room']:
            cursor = mydb.cursor()
            query = "SELECT * FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (session['room'],))
            results = cursor.fetchone()
            if results is not None:
                isP1= False if results[4]==session['username'] else True

    
    boardSize = {'a1V': 'table-cell', 'b1V': 'table-cell', 'c1V': 'table-cell', 'd1V': 'table-cell', 'e1V': 'table-cell', 'f1V': 'table-cell', 'g1V': 'table-cell', 'h1V': 'table-cell', 'i1V': 'table-cell', 'j1V': 'table-cell',
                'a2V': 'table-cell', 'b2V': 'table-cell', 'c2V': 'table-cell', 'd2V': 'table-cell', 'e2V': 'table-cell', 'f2V': 'table-cell', 'g2V': 'table-cell', 'h2V': 'table-cell', 'i2V': 'table-cell', 'j2V': 'table-cell',
                'a3V': 'table-cell', 'b3V': 'table-cell', 'c3V': 'table-cell', 'd3V': 'table-cell', 'e3V': 'table-cell', 'f3V': 'table-cell', 'g3V': 'table-cell', 'h3V': 'table-cell', 'i3V': 'table-cell', 'j3V': 'table-cell',
                'a4V': 'table-cell', 'b4V': 'table-cell', 'c4V': 'table-cell', 'd4V': 'table-cell', 'e4V': 'table-cell', 'f4V': 'table-cell', 'g4V': 'table-cell', 'h4V': 'table-cell', 'i4V': 'table-cell', 'j4V': 'table-cell',
                'a5V': 'table-cell', 'b5V': 'table-cell', 'c5V': 'table-cell', 'd5V': 'table-cell', 'e5V': 'table-cell', 'f5V': 'table-cell', 'g5V': 'table-cell', 'h5V': 'table-cell', 'i5V': 'table-cell', 'j5V': 'table-cell',
                'a6V': 'table-cell', 'b6V': 'table-cell', 'c6V': 'table-cell', 'd6V': 'table-cell', 'e6V': 'table-cell', 'f6V': 'table-cell', 'g6V': 'table-cell', 'h6V': 'table-cell', 'i6V': 'table-cell', 'j6V': 'table-cell',
                'a7V': 'table-cell', 'b7V': 'table-cell', 'c7V': 'table-cell', 'd7V': 'table-cell', 'e7V': 'table-cell', 'f7V': 'table-cell', 'g7V': 'table-cell', 'h7V': 'table-cell', 'i7V': 'table-cell', 'j7V': 'table-cell',
                'a8V': 'table-cell', 'b8V': 'table-cell', 'c8V': 'table-cell', 'd8V': 'table-cell', 'e8V': 'table-cell', 'f8V': 'table-cell', 'g8V': 'table-cell', 'h8V': 'table-cell', 'i8V': 'table-cell', 'j8V': 'table-cell',
                'a9V': 'table-cell', 'b9V': 'table-cell', 'c9V': 'table-cell', 'd9V': 'table-cell', 'e9V': 'table-cell', 'f9V': 'table-cell', 'g9V': 'table-cell', 'h9V': 'table-cell', 'i9V': 'table-cell', 'j9V': 'table-cell',
                'a10V': 'table-cell', 'b10V': 'table-cell', 'c10V': 'table-cell', 'd10V': 'table-cell', 'e10V': 'table-cell', 'f10V': 'table-cell', 'g10V': 'table-cell', 'h10V': 'table-cell', 'i10V': 'table-cell', 'j10V': 'table-cell',
                'VA': 'table-row', 'VB': 'table-row', 'VC': 'table-row', 'VD': 'table-row', 'VE': 'table-row', 'VF': 'table-row', 'VG': 'table-row', 'VH': 'table-row', 'VI': 'table-row', 'VJ': 'table-row',
                'V1': 'table-cell','V2': 'table-cell','V3': 'table-cell','V4': 'table-cell','V5': 'table-cell','V6': 'table-cell','V7': 'table-cell','V8': 'table-cell','V9': 'table-cell','V10': 'table-cell'}
    
    p2 = 'NONE'

    if session['room']:
        cursor = mydb.cursor()
        query = "SELECT * FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        results = cursor.fetchone()
        if results is not None:
            p2 = results[4] if results[4] is not None else 'NONE'
            if results[4]==session['username']:
                p2 = results[3]
    

    player = str(session['username'])
    opponent = str(p2)
    global players
    players = [
        BattleshipPlayer(player),
        BattleshipPlayer(opponent)
    ]
    if isP1:
        session['player'] = players[0]
        session['opponent'] = players[1]
    else:
        session['player'] = players[1]
        session['opponent'] = players[0]

    if results is not None:
        p2 = results[4] if results[4] is not None else 'NONE'
        if results[4]==session['username']:
            p2 = results[3]
    return render_template("standard.html",**boardSize, vis3 = 'none', sizeSubmitVis = 'none', p1=session['username'], p2 = p2)


@app.route('/rapid.html', methods=['GET', 'POST'])
def rapid():

    return render_template('rapid.html')

@app.route('/reinforcement.html', methods=['GET', 'POST'])
def reinforcement():
    return render_template("reinforcement.html")

@app.route('/sailing.html', methods=['GET', 'POST'])
def sailing():
    return render_template("sailing.html")

@app.route('/advanced.html', methods=['GET', 'POST'])
def advanced():
    return render_template("advanced.html")




if __name__ == '__main__':
    #app.run(host='10.0.0.31', port=5000, debug=True)
    socketio.run(app=app,host='10.0.0.31', port=5000, debug=True)



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
        turn INT,
        pOneShot VARCHAR(20),
        pTwoShot VARCHAR(20),
        pOneSunk INT,
        pTwoSunk INT,
        pOneWin INT,
        pTwoWin INT,
        haveWinner Int
);

    '''
    cur.execute(query)
    mydb.commit()
except:
    pass

global numShot
numShot = {
    'C':0,
    'B':0,
    'D':0,
    'S':0,
    'P':0
}

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
    query = "INSERT INTO rooms (roomcode,numUsers, userOne, userTwo, pOneShot, pTwoShot, pOneSunk, pTwoSunk, pOneWin, pTwoWin,haveWinner) VALUE (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(query,(room, 1,session['username'],None,'0,0,0,0,0','0,0,0,0,0',0,0,0,0,0))
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
    session['winner'] = False
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

@app.route('/updateInstruct')
def updateInstruct():
    out = "Place down your ships!"
    cursor = mydb.cursor()
    query = "SELECT haveWinner FROM rooms WHERE roomcode = %s"
    cursor.execute(query, (session['room'],))
    session['winner'] = bool(cursor.fetchone()[0])
    if session['winner']:
        if session['turn']==2:
            cursor = mydb.cursor()
            query = "SELECT userOne FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (session['room'],))
            pNum = cursor.fetchone()[0]
        else:
            cursor = mydb.cursor()
            query = "SELECT userTwo FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (session['room'],))
            pNum = cursor.fetchone()[0]
        out = f"GAME OVER! {pNum} wins!"
    elif allPlaced:
        out = "Shoot at opponent!"
    return jsonify(out)

@app.route('/updateScore')
def updateScore():
    isP1 = True
    if session['room']:
            cursor = mydb.cursor()
            query = "SELECT * FROM rooms WHERE roomcode = %s"
            cursor.execute(query, (session['room'],))
            results = cursor.fetchone()
            
            isP1= False if results[4]==session['username'] else True
    
    output  ={}
    cursor = mydb.cursor()
    query = "SELECT pOneWin FROM rooms WHERE roomcode = %s"
    cursor.execute(query, (session['room'],))
    p1score = cursor.fetchone()[0]

    cursor = mydb.cursor()
    query = "SELECT pTwoWin FROM rooms WHERE roomcode = %s"
    cursor.execute(query, (session['room'],))
    p2score = cursor.fetchone()[0]

    if isP1:
        output['P1'] = p1score
        output['P2'] = p2score
    else:
        output['P1'] = p2score
        output['P2'] = p1score
    return jsonify(output)

@app.route('/checkOver')
def checkOver():
    cursor = mydb.cursor()
    query = "SELECT haveWinner FROM rooms WHERE roomcode = %s"
    cursor.execute(query, (session['room'],))
    session['winner'] = bool(cursor.fetchone()[0])
    if session['winner']:
        return jsonify(True)
    return jsonify(False)


@app.route('/resetGame')
def resetGame():
    global board_dict
    global board_dict2
    board_dict = {}
    board_dict2 = {}
    none_board_str = ','.join(str(None) for row in session['player'].ocean.board for item in row)
    cursor = mydb.cursor()
    query = 'UPDATE rooms SET pOneTarget=%s,pTwoTarget=%s, pOneOcean=%s, pTwoOcean=%s, turn=%s, pOneShot=%s, pTwoShot=%s, pOneSunk=%s, pTwoSunk=%s,haveWinner=%s WHERE roomcode = %s'
    cursor.execute(query, (none_board_str,none_board_str,none_board_str,none_board_str,1,'0,0,0,0,0','0,0,0,0,0',0,0,0,session['room']))
    mydb.commit()
    query = 'UPDATE rooms SET pOneTarget = %s WHERE room = %s'
    cursor.execute(query, (none_board_str,session['room']))
    mydb.commit()
    standard()
    return 'eoaihei'

@app.route('/processShot/<string:userInfo>', methods=['POST'])
def processShot(userInfo):

    cursor = mydb.cursor()
    query = "SELECT haveWinner FROM rooms WHERE roomcode = %s"
    cursor.execute(query, (session['room'],))
    haveWinner = bool(cursor.fetchone()[0])
    session['winner'] = haveWinner


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

    if isP1:
        cur = mydb.cursor()
        query  = "SELECT pOneShot FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        session['beenShot'] = cursor.fetchone()[0]
        print(session['beenShot'])
    else:
        cur = mydb.cursor()
        query  = "SELECT pTwoShot FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (session['room'],))
        session['beenShot'] = cursor.fetchone()[0]
        print(session['beenShot'])

    if isP1 and turn==1:
        go = True
    elif not isP1 and turn==2:
        go = True
    else:
        go=False
    print(allPlaced and go)

# START ---------------------------------------------------------------------------------------------


            # END ---------------------------------------------------------------------------------

    if not session['winner']:
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

            global numShot
            if opponentBoard[row-1][col-1] != 'None':
                session['player'].target.markHit(row-1,col-1)
                
                shipMap = {
                    'C':'Carrier',
                    'B':'Battleship',
                    'D':'Destroyer',
                    'S':'Submarine',
                    'P': 'Patrol Boat'
                }

                shipLen = {
                    'C':5,
                    'B':4,
                    'D':3,
                    'S':3,
                    'P': 2
                }

                shipsInd = {
                    'C':0,
                    'B':1,
                    'D':2,
                    'S':3,
                    'P': 4
                }
                sunk = False
                ind = shipsInd[opponentBoard[row-1][col-1]]
                length = shipLen[opponentBoard[row-1][col-1]]
                shipType = shipMap[opponentBoard[row-1][col-1]]

                beenShotList = session['beenShot'].split(',')
                beenShotList[ind] = str(int(beenShotList[ind])+1)
                beenShotStr = ",".join(beenShotList)
                print(f"BEEN SHOT STR: {beenShotStr}")

                print(f'NUM TIMES HIT {beenShotList[ind]}')
                if int(beenShotList[ind]) == length:
                    sunk = True

                if isP1:
                    cursor = mydb.cursor()
                    query = "UPDATE rooms SET pOneShot = %s WHERE roomcode = %s"
                    cursor.execute(query, (beenShotStr,session['room']))
                    mydb.commit()

                else:
                    cursor = mydb.cursor()
                    query = "UPDATE rooms SET pTwoShot = %s WHERE roomcode = %s"
                    cursor.execute(query, (beenShotStr,session['room']))
                    mydb.commit()


                if sunk:
                    if isP1:
                        cursor = mydb.cursor()
                        query = "UPDATE rooms SET pOneSunk = pOneSunk+1 WHERE roomcode = %s"
                        cursor.execute(query, (session['room'],))
                        mydb.commit()

                        cur = mydb.cursor()
                        query  = "SELECT pOneSunk FROM rooms WHERE roomcode = %s"
                        cur.execute(query, (session['room'],))
                        numSunk = cur.fetchone()[0]
                        print(f"NUMBER SUNK: {numSunk}")

                        if numSunk ==5:
                            winner = 1
                            session['winner'] = True
                            print('P1 WINS')
                            print(f"{session['username']} WINS")
                            cursor = mydb.cursor()
                            query = "UPDATE rooms SET pOneWin = pOneWin+1 WHERE roomcode = %s"
                            cursor.execute(query, (session['room'],))
                            mydb.commit()

                            cursor = mydb.cursor()
                            query = "UPDATE rooms SET haveWinner = 1 WHERE roomcode = %s"
                            cursor.execute(query, (session['room'],))
                            mydb.commit()

                    else:
                        cursor = mydb.cursor()
                        query = "UPDATE rooms SET pTwoSunk = pTwoSunk+1 WHERE roomcode = %s"
                        cursor.execute(query, (session['room'],))
                        mydb.commit()

                        cur = mydb.cursor()
                        query  = "SELECT pTwoSunk FROM rooms WHERE roomcode = %s"
                        cur.execute(query, (session['room'],))
                        numSunk = cur.fetchone()[0]
                        print(f"NUMBER SUNK: {numSunk}")
                        if numSunk ==5:
                            winner = 2
                            session['winner'] = True
                            print('P2 WINS')
                            print(f"{session['username']} WINS")
                            cursor = mydb.cursor()
                            query = "UPDATE rooms SET pTwoWin = pTwoWin+1 WHERE roomcode = %s"
                            cursor.execute(query, (session['room'],))
                            mydb.commit()

                            cursor = mydb.cursor()
                            query = "UPDATE rooms SET haveWinner = 1 WHERE roomcode = %s"
                            cursor.execute(query, (session['room'],))
                            mydb.commit()

                    
                
                print(f'HIT {shipType} AT {row}, {col}')
                

            else:
                session['player'].target.markMiss(row-1,col-1)

            
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
    return render_template("standard.html", vis3 = 'none', sizeSubmitVis = 'none', p1=session['username'], p2 = p2)


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



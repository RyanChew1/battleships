from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
import mysql.connector
import random
import string
import game

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

app.secret_key = 'secret_key'

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

# game modes
@app.route('/standard.html', methods=['GET', 'POST'])
def standard():
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

    if request.method == 'POST':
        rowSize = int(request.form['rowSize'])
        colSize = int(request.form['colSize'])
        #set display based on inputs
        for i in boardSize:
            if i[0] != 'V':
                col = int(i[1:-1]) #only number
                row = i[0].upper() #only first letter
                row = mapSize[row] #convert to number
                if row>rowSize or col>colSize:
                    boardSize[i] = 'none'

                
            else:
                if i[1:].isnumeric():
                    if int(i[1:])>colSize:
                        boardSize[i] = 'none'
                else:
                    row = i[1:]
                    if mapSize[row]>rowSize:
                        boardSize[i]= 'none'

        return render_template("standard.html",**boardSize, vis3 = 'none')
    else:
        return render_template('standard.html',**boardSize)

@app.route('/rapid.html', methods=['GET', 'POST'])
def rapid():
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

    if request.method == 'POST':
        rowSize = int(request.form['rowSize'])
        colSize = int(request.form['colSize'])
        #set display based on inputs
        for i in boardSize:
            if i[0] != 'V':
                col = int(i[1:-1]) #only number
                row = i[0].upper() #only first letter
                row = mapSize[row] #convert to number
                if row>rowSize or col>colSize:
                    boardSize[i] = 'none'

                
            else:
                if i[1:].isnumeric():
                    if int(i[1:])>colSize:
                        boardSize[i] = 'none'
                else:
                    row = i[1:]
                    if mapSize[row]>rowSize:
                        boardSize[i]= 'none'
            return render_template("rapid.html", **boardSize)
    return render_template('rapid.html',**boardSize)

@app.route('/reinforcement.html', methods=['GET', 'POST'])
def reinforcement():
    return render_template("reinforcement.html")

@app.route('/sailing.html', methods=['GET', 'POST'])
def sailing():
    return render_template("sailing.html")

@app.route('/advanced.html', methods=['GET', 'POST'])
def advanced():
    return render_template("advanced.html")




# # START
def dropEmpty():
    cursor = mydb.cursor()
    query = "DELETE FROM rooms WHERE numUsers = 0"
    cursor.execute(query)
    mydb.commit()

def createNew(room):
    cursor = mydb.cursor()
    query = "INSERT INTO rooms (roomcode,numUsers) VALUE (%s, 1)"
    cursor.execute(query,(room,))
    mydb.commit()

def adduser(room):
    cursor = mydb.cursor()

    queryNum = "SELECT numUsers FROM rooms WHERE roomcode = %s"
    cursor.execute(queryNum, (room,))
    num = cursor.fetchone()[0]
    print(f"num: {num}")
    query = "UPDATE rooms SET numUsers = %s WHERE roomcode=%s"
    cursor.execute(query,(num+1,room))
    mydb.commit()

def removeuser(room):
    cursor = mydb.cursor()

    queryNum = "SELECT numUsers FROM rooms WHERE roomcode = %s"
    cursor.execute(queryNum, (room,))
    print(f'ROOOM: {room}')
    num = cursor.fetchone()[0]
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



map_row = {
    
}



if __name__ == '__main__':
    #app.run(host='10.0.0.31', port=5000, debug=True)
    socketio.run(app=app,host='localhost', port=5000, debug=True)

#HOME BUTTON LOGS OUT
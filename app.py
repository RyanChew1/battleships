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



boardSize = {'a1V': 'none', 'b1V': 'none', 'c1V': 'none', 'd1V': 'none', 'e1V': 'none', 'f1V': 'none', 'g1V': 'none', 'h1V': 'none', 'i1V': 'none', 'j1V': 'none',
            'a2V': 'none', 'b2V': 'none', 'c2V': 'none', 'd2V': 'none', 'e2V': 'none', 'f2V': 'none', 'g2V': 'none', 'h2V': 'none', 'i2V': 'none', 'j2V': 'none',
            'a3V': 'none', 'b3V': 'none', 'c3V': 'none', 'd3V': 'none', 'e3V': 'none', 'f3V': 'none', 'g3V': 'none', 'h3V': 'none', 'i3V': 'none', 'j3V': 'none',
            'a4V': 'none', 'b4V': 'none', 'c4V': 'none', 'd4V': 'none', 'e4V': 'none', 'f4V': 'none', 'g4V': 'none', 'h4V': 'none', 'i4V': 'none', 'j4V': 'none',
            'a5V': 'none', 'b5V': 'none', 'c5V': 'none', 'd5V': 'none', 'e5V': 'none', 'f5V': 'none', 'g5V': 'none', 'h5V': 'none', 'i5V': 'none', 'j5V': 'none',
            'a6V': 'none', 'b6V': 'none', 'c6V': 'none', 'd6V': 'none', 'e6V': 'none', 'f6V': 'none', 'g6V': 'none', 'h6V': 'none', 'i6V': 'none', 'j6V': 'none',
            'a7V': 'none', 'b7V': 'none', 'c7V': 'none', 'd7V': 'none', 'e7V': 'none', 'f7V': 'none', 'g7V': 'none', 'h7V': 'none', 'i7V': 'none', 'j7V': 'none',
            'a8V': 'none', 'b8V': 'none', 'c8V': 'none', 'd8V': 'none', 'e8V': 'none', 'f8V': 'none', 'g8V': 'none', 'h8V': 'none', 'i8V': 'none', 'j8V': 'none',
            'a9V': 'none', 'b9V': 'none', 'c9V': 'none', 'd9V': 'none', 'e9V': 'none', 'f9V': 'none', 'g9V': 'none', 'h9V': 'none', 'i9V': 'none', 'j9V': 'none', 
            'a10V': 'none', 'b10V': 'none', 'c10V': 'none', 'd10V': 'none', 'e10V': 'none', 'f10V': 'none', 'g10V': 'none', 'h10V': 'none', 'i10V': 'none', 'j10V': 'none',
            'VA': 'none', 'VB': 'none', 'VC': 'none', 'VD': 'none', 'VE': 'none', 'VF': 'none', 'VG': 'none', 'VH': 'none', 'VI': 'none', 'VJ': 'none',
            'V1': 'none', 'V2': 'none', 'V3': 'none', 'V4': 'none', 'V5': 'none', 'V6': 'none', 'V7': 'none', 'V8': 'none', 'V9': 'none', 'V10': 'none'}

mapSize = {
    1:'A',
    2:'B',
    3:'C',
    4:'D',
    5:'E',
    6:'F',
    7:'G',
    8:'H',
    9:'I',
    10:'J'
}

# game modes
@app.route('/standard.html', methods=['GET', 'POST'])
def standard():
    if request.method == 'POST':
        rowSize = int(request.form['rowSize'])
        colSize = int(request.form['colSize'])
        #set display based on inputs
        for i in boardSize:
            pass
        return render_template("standard.html",**boardSize)
    else:
        return render_template('standard.html',**boardSize)

@app.route('/rapid.html', methods=['GET', 'POST'])
def rapid():
    return render_template("rapid.html")

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
        print('#'*20)
        print(session.get('room'))
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
    socketio.run(app=app,host='10.0.0.31', port=5000, debug=True)



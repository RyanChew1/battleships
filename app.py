from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
import mysql.connector
import random
import string

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
    print(session)
    if 'username' in session:
        return render_template('logged_in.html',visibility = 'none')
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
            return render_template("logged_in.html")
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
            return render_template("logged_in.html")
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

# game modes
@app.route('/standard.html', methods=['GET', 'POST'])
def standard():
    return render_template("standard.html",)

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

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if(request.method=='POST'):
        cursor = mydb.cursor()
        room = request.form['room']


        query = "SELECT numUsers FROM rooms WHERE roomcode = %s"
        cursor.execute(query, (room,))
        result = cursor.fetchone()
        if result:
            session['room'] = room
            adduser(room)
            return render_template('logged_in.html', session = session,visibility = 'none')
        else:
            return render_template('logged_in.html', session = session,visibility = 'block')

        

@app.route('/create', methods=['GET', 'POST'])
def create():
    if(request.method=='POST'):
        cursor = mydb.cursor()
        found = False
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

        return render_template('logged_in.html', session = session,visibility = 'none')


@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
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
    leave_room(room)
    session['room'] = None
    emit('status', {'msg': username + ' has left the room.'}, room=room)


# # END



if __name__ == '__main__':
    #app.run(host='10.0.0.31', port=5000, debug=True)
    socketio.run(app=app,host='10.0.0.31', port=5000, debug=True)



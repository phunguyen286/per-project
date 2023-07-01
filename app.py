from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'your-secret-key'
socketio = SocketIO(app)

# Dictionary to store votes
votes = {
    'Location 1 - Time 1': 0,
    'Location 2 - Time 2': 0,
    'Location 3 - Time 3': 0
}

# Dictionary to store user credentials and selections
users = {
    'user1': {
        'password': 'password1',
        'locations': [],
        'dates': [],
        'times': []
    },
    'user2': {
        'password': 'password2',
        'locations': [],
        'dates': [],
        'times': []
    },
    'user3': {
        'password': 'password3',
        'locations': [],
        'dates': [],
        'times': []
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('beer_time'))
        else:
            return "Invalid username or password"
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/beer-time', methods=['GET', 'POST'])
def beer_time():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = session['username']
        location = request.form['location']
        date = request.form['date']
        time = request.form['time']

        users[username]['locations'].append(location)
        users[username]['dates'].append(date)
        users[username]['times'].append(time)

        emit('vote_update', votes, broadcast=True)

    return render_template('beer_time.html', users=users, votes=votes)

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    if 'username' in session:
        username = session['username']
        selected_location = request.form['location']
        selected_time = request.form['time']

        for user in users.values():
            if selected_location in user['locations'] and selected_time in user['times']:
                vote_key = f'{selected_location} - {selected_time}'
                votes[vote_key] += 1

        emit('vote_update', votes, broadcast=True)
        return jsonify(success=True, votes=votes)

    return jsonify(success=False)

@app.route('/get_votes', methods=['GET'])
def get_votes():
    return jsonify(votes)

@app.route('/results')
def results():
    return render_template('results.html', votes=votes)

@app.route('/invite_users', methods=['POST'])
def invite_users():
    invited_users = request.form.getlist('users')
    # Logic to handle inviting users
    # ...

    return redirect(url_for('beer_time'))

if __name__ == '__main__':
    socketio.run(app)

# The get_db() function is used to get a database connection. It checks if a connection exists in the g object and creates one if none is found.
# The @app.teardown_appcontext decorator ensures that the database connection is closed when the request is finished.
# The with app.app_context(): block is used to create a context within which the database operations are performed.

from flask import Flask, request, jsonify, g
import sqlite3
import secrets

app = Flask(__name__)

# Database initialization
DATABASE = 'drone_database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize SQLite database
with app.app_context():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            session_token TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS waypoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            location TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()

# Helper function to generate a session token
def generate_session_token():
    return secrets.token_hex(16)

# API endpoint for user authentication
@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Perform user authentication
    # For simplicity, we just check if the user exists in the database
    with app.app_context():
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()

    if user:
        # Generate and store a session token for the authenticated user
        session_token = generate_session_token()
        with app.app_context():
            cursor = get_db().cursor()
            cursor.execute('UPDATE users SET session_token=? WHERE id=?', (session_token, user[0]))
            get_db().commit()
        return jsonify({'session_token': session_token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
    
# API endpoint for adding a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Insert the new user into the database
    with app.app_context():
        cursor = get_db().cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        get_db().commit()

    return jsonify({'message': 'User added successfully'})


# API endpoint for setting the drone's next waypoint
@app.route('/set_waypoint', methods=['POST'])
def set_waypoint():
    data = request.get_json()
    session_token = data.get('session_token')
    location = data.get('location')

    # Validate session token and get user ID
    with app.app_context():
        cursor = get_db().cursor()
        cursor.execute('SELECT id FROM users WHERE session_token=?', (session_token,))
        user_id = cursor.fetchone()

    if user_id:
        # Store the waypoint for the authenticated user
        with app.app_context():
            cursor = get_db().cursor()
            cursor.execute('INSERT INTO waypoints (user_id, location) VALUES (?, ?)', (user_id[0], location))
            get_db().commit()
        return jsonify({'message': 'Waypoint set successfully'})
    else:
        return jsonify({'error': 'Invalid session token'}), 401

if __name__ == '__main__':
    app.run(debug=True)

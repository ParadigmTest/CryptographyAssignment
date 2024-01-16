from flask import Flask, request, jsonify, g
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
import sqlite3

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

# ChaCha20 initialization
key = get_random_bytes(32)
nonce = get_random_bytes(8)
cipher = ChaCha20.new(key=key, nonce=nonce)

# Function to extract number from ChaCha20 PRNG
def extract_number(cipher):
    return int.from_bytes(cipher.encrypt(b'\x00\x00\x00\x00\x00\x00\x00\x00'), 'big')

# Function to generate session token
def generate_session_token():
    return hex(extract_number(cipher))[2:]

# Function to generate drone's next waypoint
def generate_next_waypoint():
    # Use the ChaCha20 PRNG to generate the next waypoint
    return extract_number(cipher) % MAX_WAYPOINT

# Function to check if the session token is valid 
def is_valid_session_token(session_token):
    # Placeholder implementation; replace with your logic
    return True

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

# API endpoint for setting the drone's next waypoint
@app.route('/set_next_waypoint', methods=['POST'])
def set_next_waypoint():
    # Authenticate the request 
    # For simplicity, we assume a valid session token is provided in the request header
    session_token = request.headers.get('Authorization')

    # Check if the session token is valid 
    if is_valid_session_token(session_token):
        next_waypoint = generate_next_waypoint()
        return jsonify({'next_waypoint': next_waypoint})
    else:
        return jsonify({'error': 'Invalid session token'}), 401
    
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


# Run the server
if __name__ == '__main__':
    MAX_WAYPOINT = 100  # Replace with the maximum value for the drone's next waypoint
    app.run(debug=True)

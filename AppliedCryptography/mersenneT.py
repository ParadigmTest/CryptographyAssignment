from flask import Flask, request, jsonify, g
import sqlite3
import os

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

# Initialize Mersenne Twister 2
(w, n, m, r) = (32, 624, 397, 31)
a = 0x9908B0DF
(u, d) = (11, 0xFFFFFFFF)
(s, b) = (7, 0x9D2C5680)
(t, c) = (15, 0xEFC60000)
l = 18
f = 1812433253

MT = [0 for _ in range(n)]
index = n + 1
lower_mask = 0x7FFFFFFF  # (1 << r) - 1 // That is, the binary number of r 1's
upper_mask = 0x80000000  # lowest w bits of (not lower_mask)

def mt_seed(seed):
    global index
    MT[0] = seed
    for i in range(1, n):
        temp = f * (MT[i - 1] ^ (MT[i - 1] >> (w - 2))) + i
        MT[i] = temp & 0xffffffff

def extract_number():
    global index
    if index >= n:
        twist()
        index = 0

    y = MT[index]
    y = y ^ ((y >> u) & d)
    y = y ^ ((y << s) & b)
    y = y ^ ((y << t) & c)
    y = y ^ (y >> l)

    index += 1
    return y & 0xffffffff

def twist():
    for i in range(0, n):
        x = (MT[i] & upper_mask) + (MT[(i + 1) % n] & lower_mask)
        xA = x >> 1
        if (x % 2) != 0:
            xA = xA ^ a
        MT[i] = MT[(i + m) % n] ^ xA

# def generate_session_token():
#     return os.urandom(16).hex()

# Replace os.urandom with Mersenne Twister for random number generation
def generate_session_token():
    return hex(extract_number())[2:]  # Convert the extracted number to hexadecimal



# API endpoint for user authentication
@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Perform user authentication (replace with your authentication logic)
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


# Run the Mersenne Twister 2 initialization
if __name__ == '__main__':
    mt_seed(0)
    app.run(debug=True)

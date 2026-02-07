from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            photo_path TEXT,
            marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username')
    user_id = session.get('user_id')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as total FROM attendance WHERE user_id = ?
    ''', (user_id,))
    attendance_count = cursor.fetchone()['total']
    conn.close()
    
    return render_template('dashboard.html', username=username, attendance_count=attendance_count)

@app.route('/attendance')
@login_required
def attendance():
    username = session.get('username')
    return render_template('attendance.html', username=username)

@app.route('/capture', methods=['POST'])
@login_required
def capture():
    """Handle photo capture for attendance marking"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        
        if 'photo' not in request.files:
            return jsonify({'success': False, 'message': 'No photo provided'}), 400
        
        photo = request.files['photo']
        if photo.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Create uploads directory if it doesn't exist
        os.makedirs('uploads', exist_ok=True)
        
        # Save photo
        filename = f'{username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        filepath = os.path.join('uploads', filename)
        photo.save(filepath)
        
        # Record attendance in database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attendance (user_id, attendance_date, photo_path)
            VALUES (?, ?, ?)
        ''', (user_id, datetime.now().strftime('%Y-%m-%d'), filepath))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Attendance marked successfully'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
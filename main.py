from flask import Flask, flash, redirect, render_template, request, url_for, session
from sqlite3 import *
from bcrypt import hashpw, gensalt, checkpw

app = Flask(__name__)

# __Database__

# Secret Key
app.secret_key = 'secret'

# Connect Database
def connect_db():
    conn = connect('database.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (name TEXT, password TEXT, email TEXT)')
    return conn

# Insert Data
def insert_db(name, password):
    conn = connect_db()
    conn.execute('INSERT INTO users (name, password) VALUES (?, ?)', (name, password))
    conn.commit()
    conn.close()

# Select Data
def select_db(name):
    conn = connect_db()
    cursor = conn.execute('SELECT * FROM users WHERE name = ?', (name,))
    data = cursor.fetchone()
    conn.close()
    return data


# __Routes__

# Index
@app.route('/')
def index():
    return render_template('index.html')

# Register
@app.route('/register' , methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        hash_pw = hashpw(password.encode('utf-8'), gensalt())
        insert_db(name, hash_pw)
        flash('Registered Successfully', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login
@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        user = select_db(name)
        if user and checkpw(password.encode('utf-8'), user[1]):
            session['username'] = name
            session['email'] = user[2]
            flash('Logged in', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
        
    return render_template('login.html')

# Logout
@app.route('/logout', methods= ['GET', 'POST'])
def logout():
    session.pop('username', None)
    flash('Logged out', 'success')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        email = request.form['email']
        conn = connect_db()
        conn.execute('UPDATE users SET email = ? WHERE name = ?', (email, session['username']))
        conn.commit()
        conn.close()
        flash('Email updated', 'success')
        session['email'] = email
        return redirect(url_for('profile'))
    if 'username' in session:
        return render_template('profile.html')
    else:
        flash('Login to view profile', 'danger')
        return redirect(url_for('login'))
    
# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
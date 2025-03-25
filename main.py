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
    conn.execute('CREATE TABLE IF NOT EXISTS users (name TEXT, password TEXT, email TEXT, address TEXT)')
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

# Create a new table for bookings (only needed once)
def create_bookings_table():
    conn = connect_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            fullname TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            address TEXT NOT NULL,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()



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
            session['address'] = user[3]
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

# Profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        if email and password and address:
            hash_pw = hashpw(password.encode('utf-8'), gensalt())
            conn = connect_db()
            conn.execute('UPDATE users SET email = ?, password = ?, address = ? WHERE name = ?', (email, hash_pw, address, session['username']))
            conn.commit()
            conn.close()
            flash('Email, password, and address updated', 'success')
            session['email'] = email
            session['address'] = address
            return redirect(url_for('profile'))
        elif email and address:
            conn = connect_db()
            conn.execute('UPDATE users SET email = ?, address = ? WHERE name = ?', (email, address, session['username']))
            conn.commit()
            conn.close()
            flash('Email and address updated', 'success')
            session['email'] = email
            session['address'] = address
            return redirect(url_for('profile'))
        elif password and address:
            hash_pw = hashpw(password.encode('utf-8'), gensalt())
            conn = connect_db()
            conn.execute('UPDATE users SET password = ?, address = ? WHERE name = ?', (hash_pw, address, session['username']))
            conn.commit()
            conn.close()
            flash('Password and address updated', 'success')
            session['address'] = address
            return redirect(url_for('profile'))
        elif email:
            conn = connect_db()
            conn.execute('UPDATE users SET email = ? WHERE name = ?', (email, session['username']))
            conn.commit()
            conn.close()
            flash('Email updated', 'success')
            session['email'] = email
            return redirect(url_for('profile'))
        elif password:
            hash_pw = hashpw(password.encode('utf-8'), gensalt())
            conn = connect_db()
            conn.execute('UPDATE users SET password = ? WHERE name = ?', (hash_pw, session['username']))
            conn.commit()
            conn.close()
            flash('Password updated', 'success')
            return redirect(url_for('profile'))
        elif address:
            conn = connect_db()
            conn.execute('UPDATE users SET address = ? WHERE name = ?', (address, session['username']))
            conn.commit()
            conn.close()
            flash('Address updated', 'success')
            session['address'] = address
            return redirect(url_for('profile'))
        return redirect(url_for('profile'))
    if 'username' in session:
        return render_template('profile.html')
    else:
        flash('Login to view profile', 'danger')
        return redirect(url_for('login'))

# Bookings
@app.route("/bookings", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        if 'username' in session:
            # Check if the user already has a booking
            conn = connect_db()
            cursor = conn.execute('SELECT * FROM bookings WHERE name = ?', (session['username'],))
            existing_booking = cursor.fetchone()
            conn.close()

            if existing_booking:
                flash('You already have a booking. Please delete it before creating a new one.', 'danger')
                return redirect(url_for('booking'))
            # Get form data
            name = session['username']
            fullname = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            date = request.form['date']
            time = request.form['time']
            address = request.form['address']
            message = request.form.get('message', '')  # Optional field

            # Save data to the database
            conn = connect_db()
            conn.execute('''
                INSERT INTO bookings (name, fullname, email, phone, date, time, address, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, fullname, email, phone, date, time, address, message))
            conn.commit()
            conn.close()

            flash('Booking submitted successfully!', 'success')
            return redirect(url_for('booking'))
        else:
            flash('You must be logged in to make a booking.', 'danger')
            return redirect(url_for('login'))

    elif request.method == "GET":
        if 'username' in session:
            # Retrieve booking details for the logged-in user
            conn = connect_db()
            cursor = conn.execute('SELECT * FROM bookings WHERE name = ?', (session['username'],))
            booking = cursor.fetchone()
            conn.close()

            # Pass booking details to the template
            if booking:
                booking_data = {
                    'name': booking[1],
                    'email': booking[3],
                    'phone': booking[4],
                    'date': booking[5],
                    'time': booking[6],
                    'address': booking[7],
                    'message': booking[8]
                }
                return render_template('booking.html', booking=booking_data)
            else:
                #flash('No bookings found.', 'danger')
                return render_template('booking.html', booking=None)
        else:
            flash('You must be logged in to view bookings.', 'danger')
            return redirect(url_for('login'))


# Delete Booking
@app.route("/delete-booking", methods=["POST"])
def deletebooking():
    if 'username' in session:
        name = session['username']
        conn = connect_db()
        # Check if the user has a booking
        cursor = conn.execute('SELECT * FROM bookings WHERE name = ?', (name,))
        booking = cursor.fetchone()
        # If they do not, tell them they don't have one
        if not booking:
            flash('No booking found to delete.', 'danger')
            conn.close()
            return redirect(url_for('booking'))
        else: # However if they do, then delete it from the database using their username to identify
            conn.execute('DELETE FROM bookings WHERE name = ?', (name,))
            conn.commit()
            conn.close()
            flash('Your booking has been deleted successfully!', 'success')
            return redirect(url_for('booking'))
    else:
        flash('You must be logged in to delete a booking.', 'danger')
        return redirect(url_for('login'))

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    result = None
    if request.method == 'POST':
        # Get form data
        electricity = float(request.form['electricity'])  # kWh per month
        gas = float(request.form['gas'])  # therms per month
        miles = float(request.form['miles'])  # miles driven per month
        flights = int(request.form['flights'])  # number of flights per year

        # Carbon footprint calculations (approximate values)
        electricity_emissions = electricity * 0.453  # kg CO2 per kWh
        gas_emissions = gas * 5.3  # kg CO2 per therm
        miles_emissions = miles * 0.404  # kg CO2 per mile
        flights_emissions = flights * 1100  # kg CO2 per flight

        # Total annual emissions
        result = round((electricity_emissions + gas_emissions + miles_emissions) * 12 + flights_emissions, 2)

    return render_template('calculator.html', result=result)
    
# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)

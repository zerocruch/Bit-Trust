import sqlite3
import hashlib

def createDatabase(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            idUser INTEGER PRIMARY KEY,
            fullName TEXT NOT NULL,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            passphrase TEXT NOT NULL,
            publicKey TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def check_username_exists(database, username):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))

    # Fetch the result
    user = cursor.fetchone()

    # Close the connection
    conn.close()

    # Check if the user exists

    return user if user is not None else None

def check_email_exists(database, email):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM users WHERE email = ? ', (email,))

    # Fetch the result
    user = cursor.fetchone()

    # Close the connection
    conn.close()

    # Check if the user exists

    return user if user is not None else None

def check_passphrase_exists(database, passphrase):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM users WHERE passphrase = ?', (passphrase,))

    # Fetch the result
    user = cursor.fetchone()

    # Close the connection
    conn.close()

    # Check if the user exists

    return user if user is not None else None

def insert_user(database, fullName, username, email, passphrase):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    publicKey = hashlib.sha256(str(passphrase).encode('utf-8')).hexdigest()

    # Insert a new user into the 'users' table
    cursor.execute('''
        INSERT INTO users (fullName, username, email, passphrase, publicKey)
        VALUES (?, ?, ?, ?, ?)
    ''', (fullName, username, email, passphrase, publicKey))

    # Commit the changes to the database
    conn.commit()

    # Close the connection
    conn.close()

    return publicKey

def check_user_exists(database, usernameORemail, passphrase):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute a SELECT query to check if the user exists
    cursor.execute('SELECT * FROM users WHERE username = ? or email = ? and passphrase = ?', (usernameORemail, usernameORemail, passphrase))

    # Fetch the result
    user = cursor.fetchone()

    # Close the connection
    conn.close()

    # Check if the user exists

    return user if user is not None else None
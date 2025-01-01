import sqlite3

DB_PATH = "database.db"

def initiate_db(db_path=DB_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            balance INTEGER NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

def add_user(username, email, age, db_path=DB_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    balance = 1000
    cursor.execute('''
        INSERT INTO Users (username, email, age, balance)
        VALUES (?, ?, ?, ?)
    ''', (username, email, age, balance))

    connection.commit()
    connection.close()

def is_included(username, db_path=DB_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute('''
        SELECT COUNT(*) FROM Users WHERE username = ?
    ''', (username,))
    exists = cursor.fetchone()[0] > 0

    connection.close()
    return exists


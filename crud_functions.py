import sqlite3

def initiate_db(db_path="database.db"):
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
    connection.commit()
    connection.close()

def get_all_products(db_path="database.db"):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute('SELECT id, title, description, price FROM Products')
    products = cursor.fetchall()

    connection.close()
    return products


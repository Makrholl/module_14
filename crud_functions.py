import sqlite3

# Инициализация базы данных
def initiate_db(db_path="database.db"):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Создаем таблицу Products, если она еще не создана
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

# Получить все продукты
def get_all_products(db_path="database.db"):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Получаем все записи из таблицы Products
    cursor.execute('SELECT id, title, description, price FROM Products')
    products = cursor.fetchall()

    connection.close()
    return products


import sqlite3

connection = sqlite3.Connection('not_telegram.db')
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER,
    balance INTEGER NOT NULL
)
""")

users_data = [(f"User{i}", f"example{i}@gmail.com", i * 10, 1000) for i in range(1, 11)]

cursor.executemany("""
INSERT INTO Users (username, email, age, balance)
VALUES (?, ?, ?, ?)
""", users_data)
connection.commit()

cursor.execute("""
UPDATE Users
SET balance = 500
WHERE id % 2 = 1
""")
connection.commit()

cursor.execute("""
DELETE FROM Users
WHERE id % 3 = 0
""")
connection.commit()

cursor.execute("""
SELECT username, email, age, balance
FROM Users
WHERE age != 60
""")
results = cursor.fetchall()

for username, email, age, balance in results:
    print(f"Имя: {username} | Почта: {email} | Возраст: {age} | Баланс: {balance}")

connection.close()


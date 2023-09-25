import sqlite3

conn = sqlite3.connect('my_database.db')

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS my_table (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER
    )
''')

conn.commit()


cursor.close()
conn.close()
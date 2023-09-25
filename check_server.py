import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# Execute a SELECT query to retrieve data from the table
cursor.execute("SELECT * FROM my_table")

# Fetch all rows from the result set
rows = cursor.fetchall()

# Check if there are rows returned
if len(rows) > 0:
    # Loop through the rows and print the data
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")
else:
    print("No data found in the database.")

# Close the database connection
conn.close()

import sqlite3
import random
import datetime

conn = sqlite3.connect('my_slack_bot.db')
cursor = conn.cursor()

# set up some fake data
def insert_fake_dm(message, sender):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO my_slack_bot (message, sender) VALUES (?, ?)",
        (message, sender)
        )
    conn.commit()
    
fake_users = ['randy', 'super hans', 'james', 'bob', 'ted']
for _ in range(10): # number of fake dms
    sender = random.choice(fake_users)
    message = f"Fake message from {sender}: {random.choice(['testing again', 'this is some new messages', 'i wanna be in that girls club?', 'bing bong','lots more fake messages', '100 years rick and morty','nintendo give me free stuff'])}"
    insert_fake_dm(message, sender)

# Retrieve and print the fake DMs
cursor.execute("SELECT message, sender FROM my_slack_bot")
fake_dms = cursor.fetchall()

for dm in fake_dms:
    message, sender = dm
    print(f"Sender: {sender}\nMessage: {message}\n")
    
conn.close()

    

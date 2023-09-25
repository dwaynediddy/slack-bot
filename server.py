import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import sqlite3
import datetime
import time

load_dotenv()

slack_bot_token = os.environ['SLACK_BOT_TOKEN']
client = WebClient(token=slack_bot_token)

conn = sqlite3.connect('my_database.db')
print(conn.total_changes)

cursor = conn.cursor()

# conversation_id = 'D05SVH4BXDK'

print(conn.total_changes)

cursor = conn.cursor()
cursor.execute("CREATE TABLE my_slack_bot (message TEXT, sender TEXT)")

cursor.execute("INSERT INTO my_slack_bot VALUES ('hello world', 'diddy')")
cursor.execute("INSERT INTO my_slack_bot VALUES ('just to wet the whistle?', 'Super Hans')")

rows = cursor.execute("SELECT message, sender FROM my_slack_bot").fetchall()
print(rows)

# cursor.execute("INSERT INTO my_table VALUES ('Hello World!', 'Super Hans')")

# row = cursor.execute("SELECT message, sender FROM my_table").fetchall()

# conn.commit()

# def get_dm():
#     try:
#         # Use the conversations history method to retrieve messages
#         response = client.conversations_history(
#             channel=conversation_id,
#             limit=1
#         )
        
#         if response['ok']:
#             messages = response['messages']
#             if messages:
#                 latest_dm = messages[0]['text']
#                 print(f"Received DM: {latest_dm}")  # Debug print
#                 return latest_dm
#             else:
#                 return None
#                 print('no DM recieved')
        
#     except SlackApiError as e:
#         print(f"Error: {e.response['error']}")
#         return None
    
# def store_dm(dm):
#     # Implement logic to store DMs in the database
#     latest_dm = get_dm(dm)
#     if latest_dm is not None:
#         cursor.execute("INSERT INTO my_table (name) VALUES (?)", (latest_dm,))
#         conn.commit()
#         print(f"Stored DM: {latest_dm}")  

# def post_stored_dms():
#     # Implement logic to post stored DMs
#     cursor.execute("SELECT name FROM my_table")
#     stored_dms = cursor.fetchall()
    
#     if stored_dms:
#         message_to_post = "\n".join([f"DM: {dm[0]}" for dm in stored_dms])
        
#         try:
#             response = client.chat_post_message(
#                 channel='#test', # replace with channel of choice
#                 text=message_to_post
#             )
            
#             if response['ok']:
#                 print('Stored DMs posted successfully')
#             else:
#                 print('Failed to post DMs')
#         except SlackApiError as e:
#             print(f"Error: (e.response['error'])")
#     else:
#         print("No DMs in the database")

# # schedule for DM posts
# # while True:
# #     current_time = datetime.datetime.now()
    
# #     if current_time.minute == 0:
# #         store_dm()
    
# #     if current_time.hour == 9 and current_time.minute == 0:
# #         post_stored_dms()
# #         time.sleep(5)

# # Print stored DMs if any
# cursor.execute("SELECT name FROM my_table")
# stored_dms = cursor.fetchall()

# if stored_dms:
#     print("Stored DMs:")
#     for dm in stored_dms:
#         print(f"DM: {dm[0]}")
# else:
#     print("No DMs retrieved from the database")

# cursor.close()
# conn.close()

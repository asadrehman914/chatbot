import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent/"Chatbot.db"
print("Database location:", DB_PATH)
def create_database():
    with sqlite3.connect("DB_PATH") as conn:

        conn.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_reply TEXT
        )
    """)

    


def save_chat(user_message,bot_reply):
    with sqlite3.connect("DB_PATH") as conn:

        conn.execute(
        "INSERT INTO chats (user_message, bot_reply) VALUES (?, ?)",
        (user_message, bot_reply)
    )

    


create_database()



def save_chat(user_message, bot_reply):
    print("Database file:", DB_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO chats (user_message, bot_reply) VALUES (?, ?)",
            (user_message, bot_reply)
        )

        count = conn.execute(
            "SELECT COUNT(*) FROM chats"
        ).fetchone()[0]

        print("Total saved chats:", count)

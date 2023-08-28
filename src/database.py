import sqlite3

class Database:
    def __init__(self, db_name="empathai.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS moods (
                user_id INTEGER,
                mood TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                user_id INTEGER,
                reminder_text TEXT,
                remind_me INTEGER,
                remind_me_at DATETIME,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS convo_hist (
                user_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def insert_mood(self, user_id, mood):
        self.cursor.execute("INSERT INTO moods (user_id, mood) VALUES (?, ?)", (user_id, mood))
        self.conn.commit()

    def get_moods(self, user_id):
        self.cursor.execute("SELECT mood, timestamp FROM moods WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        return self.cursor.fetchall()

    def insert_reminder(self, user_id, reminder_text, remind_me, remind_me_at):
        self.cursor.execute("INSERT INTO reminders (user_id, reminder_text, remind_me, remind_me_at) VALUES (?, ?, ?, ?)", (user_id, reminder_text, remind_me, remind_me_at))
        self.conn.commit()

    def get_reminders(self, user_id):
        self.cursor.execute("SELECT reminder_text, remind_me, remind_me_at, timestamp FROM reminders WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        return self.cursor.fetchall()

    def delete_reminder(self, user_id, timestamp):
        self.cursor.execute("DELETE FROM reminders WHERE user_id = ? AND timestamp = ?", (user_id, timestamp))
        self.conn.commit()

    def insert_convo(self, user_id, role, content):
        self.cursor.execute("INSERT INTO convo_hist (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
        self.conn.commit()

    def get_convo(self, user_id):
        self.cursor.execute("SELECT role, content, timestamp FROM convo_hist WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        return self.cursor.fetchall()
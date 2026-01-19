import sqlite3

db_name = "game_data.db"

def create_tables():
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                score INTEGER DEFAULT 0,
                daily_attempt INTEGER DEFAULT 0
            )
        """)
        connect.commit()

def check_player_status(user_id):
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()

        cursor.execute("SELECT daily_attempt FROM players WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        if result is None:
            cursor.execute("INSERT INTO players (user_id, score, daily_attempt) VALUES (?, 0, 0)", (user_id,))
            connect.commit()
            return False

        return result[0] == 1

def mark_as_played(user_id):
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        cursor.execute("UPDATE players SET daily_attempt = 1 WHERE user_id = ?", (user_id,))
        connect.commit()

def add_score(user_id, points):
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        cursor.execute("UPDATE players SET score = score + ? WHERE user_id = ?", (points, user_id))
        connect.commit()

def reset_daily_attempts():
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        cursor.execute("UPDATE players SET daily_attempt = 0")
        connect.commit()

def get_leaderboard():
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT user_id, score FROM players ORDER BY score DESC LIMIT 20")
        return cursor.fetchall()

def count_remaining_players():
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        cursor.execute("SELECT COUNT(*) FROM players WHERE daily_attempt = 0")
        return cursor.fetchone()[0]

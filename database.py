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

def register_player(user_id):
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        sql = "INSERT OR IGNORE INTO players (user_id) VALUES (?)"
        cursor.execute(sql, (user_id,))
        connect.commit()

def is_player_registered(user_id):
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        sql = "SELECT user_id FROM players WHERE user_id = ?"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result is not None

def has_played_today(user_id):
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        sql = "SELECT daily_attempt FROM players WHERE user_id = ?"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        if result is None:
            return True
        if result[0] == 1:
            return True
        return False

def mark_as_played(user_id):
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        sql = "UPDATE players SET daily_attempt = 1 where user_id = ?"
        cursor.execute(sql, (user_id,))
        connect.commit()

def add_score(user_id, points):
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        sql = "UPDATE players SET score = score + ? WHERE user_id = ?"
        cursor.execute(sql, (user_id, points))
        connect.commit()

def reset_daily_attempts():
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        sql = "UPDATE players SET daily_attempt = 0"
        cursor.execute(sql)
        connect.commit()

def get_leaderboard():
    with sqlite3.connect(db_name) as connect:
        cursor = connect.cursor()
        sql = "SELECT user_id, score FROM players ORDER BY score DESC LIMIT 20"
        cursor.execute(sql)
        return cursor.fetchall()

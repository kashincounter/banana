import psycopg2
from psycopg2.extras import Json

DB_HOST = "localhost"
DB_NAME = "user_info"
DB_USER = "postgres"
DB_PASS = "54885488"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
cur = conn.cursor()


def get_user_favorites(username):
    try:
        cur.execute("SELECT favorites FROM user_favorites WHERE username = %s", (username,))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            return []
    except Exception as e:
        print(f"Error fetching user favorites: {e}")
        return []


def add_to_favorites(username, cryptocurrency):
    try:
        cur.execute("SELECT favorites FROM user_favorites WHERE username = %s", (username,))
        result = cur.fetchone()
        if result:
            favorites = result[0]
            if cryptocurrency not in favorites:
                favorites.append(cryptocurrency)
                cur.execute("UPDATE user_favorites SET favorites = %s WHERE username = %s", (favorites, username))
        else:
            favorites = [cryptocurrency]
            cur.execute("INSERT INTO user_favorites (username, favorites) VALUES (%s, %s)", (username, favorites))
        conn.commit()
    except Exception as e:
        print(f"Error adding to favorites: {e}")
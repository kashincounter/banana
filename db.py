import psycopg2
from psycopg2.extras import Json

DB_HOST = "localhost"
DB_NAME = "userdata"
DB_USER = "postgres"
DB_PASS = "54885488"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
cur = conn.cursor()


def add_user_if_not_exists(username):
    try:
        cur.execute("SELECT 1 FROM favourite_info WHERE username = %s", (username,))
        result = cur.fetchone()
        if not result:
            cur.execute("INSERT INTO favourite_info (username, favourite_list) VALUES (%s, %s)", (username, []))
            conn.commit()
            print(f"User {username} added to database.")
        else:
            print(f"User {username} already exists in database.")
    except Exception as e:
        print(f"Error adding user: {e}")



def get_user_favorites(username):
    try:
        cur.execute("SELECT favourite_list FROM favourite_info WHERE username = %s", (username,))
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
        cur.execute("SELECT favourite_list FROM favourite_info WHERE username = %s", (username,))
        result = cur.fetchone()
        if result:
            favorites = result[0] if result[0] else []
            if cryptocurrency not in favorites:
                favorites.append(cryptocurrency)
                cur.execute("UPDATE favourite_info SET favourite_list = %s WHERE username = %s", (favorites, username))
        else:
            favorites = [cryptocurrency]
            cur.execute("INSERT INTO favourite_info (username, favourite_list) VALUES (%s, %s)", (username, favorites))
        conn.commit()
    except Exception as e:
        print(f"Error adding to favorites: {e}")

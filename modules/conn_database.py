import sqlite3

def connect_database(database_name):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    return conn, cursor

def create_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        image_name TEXT,
        date_processed TEXT
    )
    """)

def delete_image(cursor, image_name):
    try:
        cursor.execute("DELETE FROM images WHERE image_name=?", (image_name,))
    except sqlite3.Error as e:
        print(f"Error deleting image {image_name}: {e}")
    else:
        print(f"Deleted image: {image_name}")

def close_database(conn):
    conn.close()

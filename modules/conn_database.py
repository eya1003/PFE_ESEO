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

def close_database(conn):
    conn.close()

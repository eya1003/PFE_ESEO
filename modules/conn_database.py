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

def create_test_data(cursor):
    cursor.execute("""
    INSERT INTO images (image_name, date_processed) VALUES
    ('image1.png', '2023-10-23'),
    ('image2.png', '2023-10-24')
    """)

def close_database(conn):
    conn.close()

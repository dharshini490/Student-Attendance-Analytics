
import sqlite3

def connect_db():
    conn = sqlite3.connect("attendance.db")
    return conn

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT UNIQUE,
            name TEXT,
            class_name TEXT,
            department TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT,
            date TEXT,
            status TEXT,
            UNIQUE(register_no, date)
        )
    """)

    conn.commit()
    conn.close()

create_tables()

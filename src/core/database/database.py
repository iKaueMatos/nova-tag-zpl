import sqlite3
import os

class Database:
    DB_NAME = "nova.db"

    @staticmethod
    def connect():
        return sqlite3.connect(Database.DB_NAME)

    @staticmethod
    def create_tables():
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS printers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                option_printer TEXT NOT NULL        
            );
        """)

        conn.commit()
        conn.close()
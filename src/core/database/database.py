import sqlite3

class Database:
    DB_NAME = "nova-tag.db"

    @staticmethod
    def connect():
        return sqlite3.connect(Database.DB_NAME)

    @staticmethod
    def create_tables():
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS api_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT UNIQUE NOT NULL,
                app_key TEXT NOT NULL,
                app_secret TEXT NOT NULL,
                client_tax TEXT,
                tax_scenario TEXT,
                stock_location TEXT
            );
    
            CREATE TABLE IF NOT EXISTS printers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                option_printer TEXT NOT NULL        
            );
        """)

        conn.commit()
        conn.close()

Database.create_tables()
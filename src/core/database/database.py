import sqlite3

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

            CREATE TABLE IF NOT EXISTS products (
                product_code TEXT PRIMARY KEY,
                product_description TEXT,
                product_ean TEXT,
                product_sku TEXT,
                product_price REAL
            );
        """)

        conn.commit()
        conn.close()

Database.create_tables()
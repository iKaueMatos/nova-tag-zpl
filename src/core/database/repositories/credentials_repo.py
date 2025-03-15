from src.core.database.database import Database


class CredentialsRepository:
    @staticmethod
    def insert_credentials(company, app_key, app_secret, client_tax, tax_scenario, stock_location):
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO api_credentials (company, app_key, app_secret, client_tax, tax_scenario, stock_location)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (company, app_key, app_secret, client_tax, tax_scenario, stock_location))

        conn.commit()
        conn.close()

    @staticmethod
    def get_credentials(company):
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT app_key, app_secret, client_tax, tax_scenario, stock_location 
        FROM api_credentials WHERE company = ?
        """, (company,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "app_key": result[0],
                "app_secret": result[1],
                "client_tax": result[2],
                "tax_scenario": result[3],
                "stock_location": result[4]
            }
        return None

    @staticmethod
    def update_credentials(company, app_key=None, app_secret=None, client_tax=None, tax_scenario=None, stock_location=None):
        conn = Database.connect()
        cursor = conn.cursor()

        updates = []
        params = []

        if app_key:
            updates.append("app_key = ?")
            params.append(app_key)
        if app_secret:
            updates.append("app_secret = ?")
            params.append(app_secret)
        if client_tax:
            updates.append("client_tax = ?")
            params.append(client_tax)
        if tax_scenario:
            updates.append("tax_scenario = ?")
            params.append(tax_scenario)
        if stock_location:
            updates.append("stock_location = ?")
            params.append(stock_location)

        if updates:
            params.append(company)
            query = f"UPDATE api_credentials SET {', '.join(updates)} WHERE company = ?"
            cursor.execute(query, params)
            conn.commit()

        conn.close()

    @staticmethod
    def delete_credentials(company):
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM api_credentials WHERE company = ?", (company,))
        conn.commit()
        conn.close()

    @staticmethod
    def list_all_credentials():
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM api_credentials")
        result = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "company": row[1],
                "app_key": row[2],
                "app_secret": row[3],
                "client_tax": row[4],
                "tax_scenario": row[5],
                "stock_location": row[6],
            }
            for row in result
        ]

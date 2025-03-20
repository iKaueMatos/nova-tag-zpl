# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from src.core.database.database import Database

class ProductRepository:
    @staticmethod
    def insert_product(product_code, product_description, product_ean, product_sku, product_price):
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO products (product_code, product_description, product_ean, product_sku, product_price)
        VALUES (?, ?, ?, ?, ?)
        """, (product_code, product_description, product_ean, product_sku, product_price))

        conn.commit()
        conn.close()

    @staticmethod
    def list_all_products():
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM products")
        result = cursor.fetchall()
        conn.close()

        return [
            {
                "product_code": row[0],
                "product_description": row[1],
                "product_ean": row[2],
                "product_sku": row[3],
                "product_price": row[4]
            }
            for row in result
        ]

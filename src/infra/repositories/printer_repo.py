# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from src.core.database.database import Database

class PrinterRepository:
    @staticmethod
    def insert_printer(option_printer):
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO printers (option_printer)
        VALUES (?)
        """, (option_printer,))

        conn.commit()
        print("concluido!")
        conn.close()

    @staticmethod
    def get_printer(printer_id):
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT option_printer
        FROM printers
        WHERE id = ?
        """, (printer_id,))

        result = cursor.fetchone()
        conn.close()

        print("impressora retornada")

        if result:
            return result[0]
        return None

    @staticmethod
    def list_all_printers():
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM printers")
        result = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "option_printer": row[1]
            }
            for row in result
        ]
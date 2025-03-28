# ----------------------------------------------------------------------------
# Autor: Kaue de Matos
# Empresa: Nova Software
# Propriedade da Empresa: Todos os direitos reservados
# ----------------------------------------------------------------------------
from src.core.database.database import Database

class PrinterRepository:
    @staticmethod
    def insert_or_update_printer(option_printer):
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM printers WHERE option_printer = ?", (option_printer,))
        existing_printer = cursor.fetchone()

        if existing_printer:
            cursor.execute("""
                    UPDATE printers
                    SET option_printer = ?
                    WHERE id = ?
                """, (option_printer, existing_printer[0]))
        else:
            cursor.execute("""
                    INSERT INTO printers (option_printer)
                    VALUES (?)
                """, (option_printer,))

        conn.commit()
        conn.close()

    @staticmethod
    def get_printer(printer_id):
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT option_printer
            FROM printers
            WHERE id = ?
            """, (printer_id))

        result = cursor.fetchone()
        conn.close()

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
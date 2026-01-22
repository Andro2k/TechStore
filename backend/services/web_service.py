from backend.connection import get_db_connection

class WebService:
    def get_catalog(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT P.Id_producto, P.nombre, P.marca, P.precio, I.cantidad 
            FROM PRODUCTO P
            INNER JOIN INVENTARIO I ON P.Id_producto = I.Id_producto
            WHERE I.cantidad > 0
        """
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                {"id": r[0], "nombre": r[1], "marca": r[2], "precio": float(r[3]), "stock": int(r[4])}
                for r in rows
            ]
        except Exception as e:
            print(f"Error web catalog: {e}")
            return []
        finally:
            conn.close()
            
    def process_purchase(self, product_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Verificar stock
            cursor.execute("SELECT cantidad FROM INVENTARIO WHERE Id_producto = ?", (product_id,))
            row = cursor.fetchone()
            
            if row and row[0] > 0:
                cursor.execute("UPDATE INVENTARIO SET cantidad = cantidad - 1 WHERE Id_producto = ?", (product_id,))
                conn.commit()
                return True, "Compra exitosa"
            else:
                return False, "Agotado"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
from backend.generic_dao import GenericDAO
from backend.connection import get_db_connection
from backend.config import CURRENT_NODE

class InventoryService(GenericDAO):
    
    def create_product_with_inventory(self, product_data, initial_qty):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 1. Insertar Producto
            cols = ", ".join(product_data.keys())
            placeholders = ", ".join(["?"] * len(product_data))
            vals = list(product_data.values())
            
            query_prod = f"INSERT INTO PRODUCTO ({cols}) VALUES ({placeholders})"
            cursor.execute(query_prod, vals)

            # 2. Insertar Inventario
            prod_id = product_data["Id_producto"]
            current_branch_id = CURRENT_NODE["id_sucursal"]
            
            query_inv = """
                INSERT INTO INVENTARIO (Id_sucursal, Id_producto, cantidad) 
                VALUES (?, ?, ?)
            """
            cursor.execute(query_inv, (current_branch_id, prod_id, initial_qty))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error transaccional crear prod+inv: {e}")
            raise e
        finally:
            conn.close()

    def update_inventory_quantity(self, product_id, new_quantity):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sucursal_id = CURRENT_NODE["id_sucursal"]
            
            # Intentar actualizar
            query_update = """
                UPDATE INVENTARIO SET cantidad = ? 
                WHERE Id_producto = ? AND Id_sucursal = ?
            """
            cursor.execute(query_update, (new_quantity, product_id, sucursal_id))
            
            # Si no existía, crear
            if cursor.rowcount == 0:
                query_insert = """
                    INSERT INTO INVENTARIO (Id_sucursal, Id_producto, cantidad)
                    VALUES (?, ?, ?)
                """
                cursor.execute(query_insert, (sucursal_id, product_id, new_quantity))

            conn.commit()
            return True
        except Exception as e:
            raise e
        finally:
            conn.close()
            
    def delete_product_secure(self, product_id):
        """Sobrescribe el borrado genérico para manejar cascada manual"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Borrar dependencias primero
            cursor.execute("DELETE FROM INVENTARIO WHERE Id_producto = ?", (product_id,))
            # Borrar producto
            cursor.execute("DELETE FROM PRODUCTO WHERE Id_producto = ?", (product_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_product_stock(self, product_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Asumiendo que tu tabla es INVENTARIO
            query = "SELECT cantidad FROM INVENTARIO WHERE Id_producto = ?"
            cursor.execute(query, (product_id,))
            row = cursor.fetchone()
            return row[0] if row else 0
        except Exception:
            return 0
        finally:
            conn.close()
from datetime import datetime
from backend.connection import get_db_connection
from backend.config import CURRENT_NODE  # <--- Importante para saber quién soy

class WebService:
    def get_catalog(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Filtramos por Id_sucursal para mostrar SOLO lo que tengo en mi tienda física local
        query = """
            SELECT P.Id_producto, P.nombre, P.marca, P.precio, I.cantidad 
            FROM PRODUCTO P
            INNER JOIN INVENTARIO I ON P.Id_producto = I.Id_producto
            WHERE I.cantidad > 0 AND I.Id_sucursal = ?
        """
        try:
            # Pasamos el ID de la sucursal actual
            cursor.execute(query, (CURRENT_NODE["id_sucursal"],))
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
            
    def process_purchase(self, product_id, client_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        sucursal_id = CURRENT_NODE["id_sucursal"]
        
        try:
            # 1. Verificar Stock y obtener Precio
            query_check = """
                SELECT I.cantidad, P.precio 
                FROM INVENTARIO I
                JOIN PRODUCTO P ON I.Id_producto = P.Id_producto
                WHERE I.Id_producto = ? AND I.Id_sucursal = ?
            """
            cursor.execute(query_check, (product_id, sucursal_id))
            row = cursor.fetchone()
            
            if not row or row[0] < 1:
                return False, "Producto agotado o no disponible en esta sucursal."
            
            precio_unitario = float(row[1])
            
            # --- INICIO TRANSACCIÓN ---

            # 2. Generar ID FACTURA (Específico para esta sucursal)
            # Como la PK es compuesta (id_factura + id_sucursal), buscamos el MAX solo de esta sucursal
            cursor.execute("SELECT MAX(id_factura) FROM FACTURA WHERE id_sucursal = ?", (sucursal_id,))
            row_max = cursor.fetchone()
            new_factura_id = (row_max[0] + 1) if row_max and row_max[0] else 1
            
            # 3. Insertar FACTURA
            fecha_actual = datetime.now()
            query_factura = """
                INSERT INTO FACTURA (id_factura, fecha, total, id_cliente, id_sucursal)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query_factura, (new_factura_id, fecha_actual, precio_unitario, client_id, sucursal_id))
            
            # 4. Insertar DETALLE_FACTURA
            # Nota: No usamos id_detalle. La PK es (id_factura, id_producto, id_sucursal)
            query_detalle = """
                INSERT INTO DETALLE_FACTURA 
                (id_factura, id_producto, id_sucursal, cantidad, precio_unidad, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            # El subtotal es igual al precio_unidad porque cantidad es 1
            cursor.execute(query_detalle, (new_factura_id, product_id, sucursal_id, 1, precio_unitario, precio_unitario))

            # 5. Actualizar Stock
            query_update = """
                UPDATE INVENTARIO 
                SET cantidad = cantidad - 1 
                WHERE Id_producto = ? AND Id_sucursal = ?
            """
            cursor.execute(query_update, (product_id, sucursal_id))
            
            conn.commit()
            return True, f"Factura #{new_factura_id} generada correctamente."
            
        except Exception as e:
            conn.rollback()
            print(f"Error en compra: {e}")
            return False, f"Error del sistema: {str(e)}"
        finally:
            conn.close()

    def register_client(self, data):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 1. Verificar si ya existe por correo
            check_query = "SELECT id_cliente FROM CLIENTE WHERE correo = ?"
            cursor.execute(check_query, (data['correo'],))
            row = cursor.fetchone()
            
            if row:
                return row[0]  # Ya existe, retornamos su ID

            # 2. NUEVO: Calcular el siguiente ID manualmente
            # Buscamos el ID más alto que exista en la tabla
            cursor.execute("SELECT MAX(id_cliente) FROM CLIENTE")
            row_max = cursor.fetchone()
            
            # Si row_max[0] es None (tabla vacía), empezamos con el 1
            # Si tiene un número, le sumamos 1
            new_id = (row_max[0] + 1) if row_max and row_max[0] is not None else 1

            # 3. Preparar datos (concatenamos nombre y apellido)
            nombre_completo = f"{data['nombre']} {data['apellido']}"
            sucursal_id = CURRENT_NODE["id_sucursal"]

            # 4. Insertar incluyendo el ID CALCULADO MANUALMENTE
            query = """
                INSERT INTO CLIENTE (id_cliente, nombre, direccion, telefono, correo, id_sucursal)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            values = (new_id, nombre_completo, data['direccion'], data['telefono'], data['correo'], sucursal_id)
            
            cursor.execute(query, values)
            conn.commit()
            
            return new_id
            
        except Exception as e:
            conn.rollback()
            print(f"Error registrando cliente: {e}")
            return None
        finally:
            conn.close()
# backend/data_manager.py
import pyodbc
import socket  # <--- Importante: Importamos librería para detectar el PC

class TechStoreDB:
    def __init__(self):
        self.driver = "{ODBC Driver 17 for SQL Server}"
        
        # --- AUTO-DETECCIÓN DE SERVIDOR ---
        # 1. Obtenemos el nombre real de la máquina
        self.hostname = socket.gethostname()
        
        # 2. Configuración inteligente
        # Si tus máquinas se llaman exactamente "LAPTOP" y "MiniPC" a nivel de sistema,
        # esto funcionará directo. Si tienen nombres como "DESKTOP-8293", 
        # puedes mapearlos en este diccionario:
        server_mapping = {
            # "NombreRealDeTuPC": "NombreInstanciaSQL"
            "LAPTOP": "LAPTOP",
            "MiniPC": "MiniPC"
        }
        
        # Usamos el mapeo si existe, si no, intentamos conectar al hostname tal cual
        self.server = server_mapping.get(self.hostname, self.hostname)
        
        print(f"[TechStoreDB] Equipo detectado: {self.hostname} -> Servidor SQL: {self.server}")

        # Mapeo de Nombres amigables a Bases de Datos reales
        self.nodos = {
            "Sede Guayaquil (02)": {"db": "TechStore_Guayaquil", "id": 2},
            "Matriz Quito (01)":   {"db": "TechStore_Quito", "id": 1}
        }

    def get_current_node_default(self):
        """
        Retorna el nombre de la sede sugerida según la PC en la que estás.
        Útil para pre-seleccionar el ComboBox en el Frontend.
        """
        if self.server == "LAPTOP":
            return "Matriz Quito (01)"
        elif self.server == "MiniPC":
            return "Sede Guayaquil (02)"
        
        # Si no coincide, retornamos la primera opción disponible
        return list(self.nodos.keys())[0]

    def get_connection(self, nombre_nodo):
        """Crea la conexión según el nodo seleccionado"""
        db_info = self.nodos.get(nombre_nodo)
        if not db_info:
            raise ValueError("Nodo no válido")

        conn_str = f'DRIVER={self.driver};SERVER={self.server};DATABASE={db_info["db"]};Trusted_Connection=yes;'
        return pyodbc.connect(conn_str)

    def get_sucursal_id(self, nombre_nodo):
        """Retorna el ID numérico (1 o 2) según el nombre"""
        return self.nodos[nombre_nodo]["id"]

    def obtener_inventario(self, nombre_nodo):
        """Consulta el stock unificado"""
        conn = self.get_connection(nombre_nodo)
        sucursal_id = self.get_sucursal_id(nombre_nodo)
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT P.Id_producto, P.nombre, P.marca, P.precio, I.cantidad 
                FROM PRODUCTO P
                LEFT JOIN INVENTARIO I ON P.Id_producto = I.Id_producto
                WHERE I.Id_sucursal = ?
            """
            cursor.execute(query, (sucursal_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    def registrar_venta(self, nombre_nodo, id_cliente, id_producto, cantidad):
        """Maneja la transacción de venta completa"""
        conn = self.get_connection(nombre_nodo)
        sucursal_id = self.get_sucursal_id(nombre_nodo)
        
        try:
            cursor = conn.cursor()
            
            # 1. Validar Precio
            cursor.execute("SELECT precio FROM PRODUCTO WHERE Id_producto = ?", (id_producto,))
            row_prod = cursor.fetchone()
            if not row_prod:
                raise Exception("Producto no encontrado en catálogo global.")
            precio_unit = row_prod[0]
            total = precio_unit * cantidad

            # 2. Validar Stock
            cursor.execute("SELECT cantidad FROM INVENTARIO WHERE Id_producto = ? AND Id_sucursal = ?", (id_producto, sucursal_id))
            row_stock = cursor.fetchone()
            if not row_stock or row_stock[0] < cantidad:
                raise Exception(f"Stock insuficiente. Disponible: {row_stock[0] if row_stock else 0}")

            # 3. Transacción (Factura -> Detalle -> Update Stock)
            cursor.execute("SELECT ISNULL(MAX(Id_factura), 0) + 1 FROM FACTURA")
            new_id_factura = cursor.fetchone()[0]

            cursor.execute("INSERT INTO FACTURA (Id_factura, total, Id_cliente, Id_sucursal, fecha) VALUES (?, ?, ?, ?, GETDATE())", 
                           (new_id_factura, total, id_cliente, sucursal_id))

            cursor.execute("INSERT INTO DETALLE_FACTURA (Id_factura, Id_producto, Id_sucursal, cantidad, precio_unidad, subtotal) VALUES (?, ?, ?, ?, ?, ?)", 
                           (new_id_factura, id_producto, sucursal_id, cantidad, precio_unit, total))

            cursor.execute("UPDATE INVENTARIO SET cantidad = cantidad - ? WHERE Id_producto = ? AND Id_sucursal = ?", 
                           (cantidad, id_producto, sucursal_id))

            conn.commit()
            return f"Venta exitosa. Factura #{new_id_factura} | Total: ${total:.2f}"
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def obtener_clientes(self, nombre_nodo):
        conn = self.get_connection(nombre_nodo)
        sucursal_id = self.get_sucursal_id(nombre_nodo)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Id_cliente, nombre, correo, telefono FROM CLIENTE WHERE Id_sucursal = ?", (sucursal_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_empleados(self, nombre_nodo):
        conn = self.get_connection(nombre_nodo)
        sucursal_id = self.get_sucursal_id(nombre_nodo)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Id_empleado, nombre, correo, telefono FROM EMPLEADO WHERE Id_sucursal = ?", (sucursal_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    def registrar_cliente(self, nombre_nodo, nombre, direccion, telefono, correo):
        conn = self.get_connection(nombre_nodo)
        sucursal_id = self.get_sucursal_id(nombre_nodo)
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ISNULL(MAX(Id_cliente), 0) + 1 FROM CLIENTE")
            new_id = cursor.fetchone()[0]
            
            query = """
                INSERT INTO CLIENTE (Id_cliente, nombre, direccion, telefono, correo, Id_sucursal)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (new_id, nombre, direccion, telefono, correo, sucursal_id))
            conn.commit()
            
            return f"Cliente registrado con éxito.\nID Asignado: {new_id}"
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def registrar_producto(self, nombre_nodo, nombre, marca, precio, stock_inicial):
        conn = self.get_connection(nombre_nodo)
        sucursal_id = self.get_sucursal_id(nombre_nodo)
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ISNULL(MAX(Id_producto), 0) + 1 FROM PRODUCTO")
            new_id_prod = cursor.fetchone()[0]
            
            query_prod = "INSERT INTO PRODUCTO (Id_producto, nombre, marca, precio) VALUES (?, ?, ?, ?)"
            cursor.execute(query_prod, (new_id_prod, nombre, marca, float(precio)))
            
            query_inv = "INSERT INTO INVENTARIO (Id_sucursal, Id_producto, cantidad) VALUES (?, ?, ?)"
            cursor.execute(query_inv, (sucursal_id, new_id_prod, int(stock_inicial)))
            
            conn.commit()
            return f"Producto creado correctamente.\nID: {new_id_prod} | Stock Inicial: {stock_inicial}"
            
        except ValueError:
            raise Exception("El precio y el stock deben ser números válidos.")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
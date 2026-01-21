# backend/data_manager.py

import socket
import pyodbc

class DataManager:
    def __init__(self):
        # 1. LISTA MAESTRA: Todas las tablas que tu App es capaz de gestionar.
        #    Si creas una tabla nueva en SQL pero no está aquí, la app la ignorará 
        #    (por seguridad y porque no tendría formularios asociados).
        self.SUPPORTED_TABLES = [
            "SUCURSAL", "PRODUCTO", "INVENTARIO", 
            "CLIENTE", "EMPLEADO", "FACTURA", "DETALLE_FACTURA"
        ]

        # 2. CONFIGURACIÓN DE NODOS (Ya no ponemos 'tables' aquí)
        self.NODES = {
            "GUAYAQUIL": {
                "hostnames": ["MiniPC"],
                "db_name": "TechStore_Guayaquil",
                "role": "Publicador (Matriz)",
                "id_sucursal": 1  # <--- AGREGAR ESTO (Verifica que sea el ID 1 en tu BD)
            },
            "QUITO": {
                "hostnames": ["LAPTOP"], # <--- Tu hostname actual
                "db_name": "TechStore_Quito",
                "role": "Suscriptor (Sucursal)",
                "id_sucursal": 2  # <--- AGREGAR ESTO (Verifica que sea el ID 2 en tu BD)
            }
        }
        
        self.SERVER_ADDR = "localhost"
        self.DB_USER = "sa"
        self.DB_PASS = "P@ssw0rd"
        
        # Detectamos quién soy y configuramos la conexión básica
        self.current_node = self._detect_node()
        
        # --- AQUÍ ESTÁ LA MAGIA ---
        # Actualizamos la lista de tablas preguntándole a la Base de Datos real
        self.current_node["tables"] = self._get_available_tables_from_db()

    def _detect_node(self):
        """Método interno para saber quién soy"""
        pc_name = socket.gethostname()
        print(f"DEBUG: Nombre de tu PC detectado: '{pc_name}'") # Esto saldrá en la consola negra
        
        for node_key, config in self.NODES.items():
            # Buscamos si el nombre actual está en la lista de hostnames
            # Usamos .upper() para evitar problemas de mayúsculas/minúsculas
            if pc_name.upper() in [h.upper() for h in config["hostnames"]]:
                print(f"DEBUG: Configuración cargada para {node_key}")
                return {"key": node_key, **config}
        
        # Si no encuentra el nombre, avisa y usa Guayaquil por defecto
        print(f"ALERTA: PC '{pc_name}' no reconocida en la lista. Usando GUAYAQUIL por defecto.")
        return {"key": "GUAYAQUIL", **self.NODES["GUAYAQUIL"]}

    def get_connection(self):
        """Genera la conexión ODBC"""
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.SERVER_ADDR};"
            f"DATABASE={self.current_node['db_name']};"
        )
        if self.DB_USER and self.DB_PASS:
            conn_str += f"UID={self.DB_USER};PWD={self.DB_PASS};"
        else:
            conn_str += "Trusted_Connection=yes;"
        return pyodbc.connect(conn_str)

    def _get_available_tables_from_db(self):
        """
        Consulta a SQL Server qué tablas existen realmente en la DB actual
        y las cruza con las que la App sabe manejar.
        """
        existing_tables = []
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Consultamos el esquema de información de SQL Server
            # Filtramos solo TABLE_TYPE = 'BASE TABLE' para evitar vistas o diagramas
            query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
            cursor.execute(query)
            
            # Obtenemos todos los nombres de tablas que existen en la BD
            db_tables = [row[0] for row in cursor.fetchall()]
            
            # FILTRO DE INTERSECCIÓN:
            # Solo habilitamos las tablas que existen en la BD Y que están en nuestra lista soportada.
            # Esto evita que aparezcan tablas del sistema como 'sysdiagrams' o tablas de replicación 'MS...'
            for table in self.SUPPORTED_TABLES:
                if table in db_tables:
                    existing_tables.append(table)
            
            conn.close()
            print(f"DEBUG: Tablas detectadas dinámicamente: {existing_tables}")
            
        except Exception as e:
            print(f"ALERTA: No se pudo conectar para detectar tablas: {e}")
            # Si falla la conexión, devolvemos una lista vacía o una por defecto
            return []

        return existing_tables 

    def fetch_table_data(self, table_name):
        """
        Trae los datos de una tabla.
        Retorna: (columnas, filas) o lanza una excepción si falla.
        """
        conn = self.get_connection() # Puede lanzar error, lo capturamos en el frontend
        cursor = conn.cursor()
        
        # OJO: Validar que table_name esté en la lista permitida para seguridad
        if table_name not in self.current_node["tables"]:
            raise ValueError(f"Acceso denegado a la tabla {table_name}")

        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        return columns, rows
    
    def insert_data(self, table_name, data_dict):
        """
        Inserta datos en la tabla.
        data_dict: Diccionario {'columna': 'valor'}
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        columns = ", ".join(data_dict.keys())
        placeholders = ", ".join(["?"] * len(data_dict))
        values = list(data_dict.values())
        
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        try:
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error insertando: {e}")
            conn.close()
            raise e
        
    def get_next_id(self, table_name, id_column):
        """
        Obtiene el siguiente ID disponible (MAX + 1).
        Si la tabla está vacía, devuelve 1.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Consultamos el valor máximo actual
            query = f"SELECT MAX({id_column}) FROM {table_name}"
            cursor.execute(query)
            row = cursor.fetchone()
            
            max_id = row[0]
            
            # Si devuelve None (tabla vacía), el siguiente es 1.
            # Si devuelve un número, el siguiente es n + 1.
            next_id = (max_id + 1) if max_id is not None else 1
            
            return next_id
        except Exception as e:
            print(f"Error calculando next_id: {e}")
            return 1 # Fallback seguro
        finally:
            conn.close()
    
    def delete_data(self, table_name, id_column, id_value):
        """Elimina un registro y limpia dependencias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # --- CORRECCIÓN 1: Limpieza de huérfanos ---
            # Si estamos borrando un PRODUCTO, primero borramos su INVENTARIO
            if table_name == "PRODUCTO":
                print(f"DEBUG: Borrando inventario asociado al producto {id_value}")
                cursor.execute("DELETE FROM INVENTARIO WHERE Id_producto = ?", (id_value,))
            
            # --- CORRECCIÓN 2: Borrado normal ---
            query = f"DELETE FROM {table_name} WHERE {id_column} = ?"
            cursor.execute(query, (id_value,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error borrando: {e}")
            conn.rollback() # Importante rollback si falla
            raise e
        finally:
            conn.close()

    def update_data(self, table_name, data_dict, id_column, id_value):
        """Actualiza un registro existente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Generar SQL: "UPDATE tabla SET col1=?, col2=? WHERE id=?"
        set_clause = ", ".join([f"{k} = ?" for k in data_dict.keys()])
        values = list(data_dict.values())
        values.append(id_value) # El ID va al final para el WHERE
        
        query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = ?"
        
        try:
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando: {e}")
            raise e
        finally:
            conn.close()

    def get_web_catalog(self):
        """
        Obtiene productos uniendo la tabla PRODUCTO con INVENTARIO
        para mostrar precio y stock disponible.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Asumiendo que INVENTARIO tiene 'Id_producto' y 'Cantidad'
        # Ajusta los nombres de columnas si tu tabla INVENTARIO es diferente.
        query = """
            SELECT 
                P.Id_producto, 
                P.nombre, 
                P.marca, 
                P.precio, 
                I.cantidad 
            FROM PRODUCTO P
            INNER JOIN INVENTARIO I ON P.Id_producto = I.Id_producto
            WHERE I.cantidad > 0
        """
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Convertimos a una lista de diccionarios para facilitar el uso en HTML
            catalog = []
            for r in rows:
                catalog.append({
                    "id": r[0],
                    "nombre": r[1],
                    "marca": r[2],
                    "precio": float(r[3]),
                    "stock": int(r[4])
                })
            return catalog
        except Exception as e:
            print(f"Error cargando catálogo web: {e}")
            return []
        finally:
            conn.close()

    def process_web_purchase(self, product_id):
        """
        Simula una compra: Resta 1 al stock del inventario.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Verificar stock actual
            check_query = "SELECT cantidad FROM INVENTARIO WHERE Id_producto = ?"
            cursor.execute(check_query, (product_id,))
            row = cursor.fetchone()
            
            if row and row[0] > 0:
                # 2. Restar 1
                update_query = "UPDATE INVENTARIO SET cantidad = cantidad - 1 WHERE Id_producto = ?"
                cursor.execute(update_query, (product_id,))
                conn.commit()
                return True, "Compra realizada con éxito"
            else:
                return False, "Producto agotado"
                
        except Exception as e:
            print(f"Error procesando compra: {e}")
            return False, str(e)
        finally:
            conn.close()

    def create_product_with_inventory(self, product_data, initial_qty):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. INSERTAR EN PRODUCTO (Esto se queda igual)
            cols = ", ".join(product_data.keys())
            placeholders = ", ".join(["?"] * len(product_data))
            vals = list(product_data.values())
            
            query_prod = f"INSERT INTO PRODUCTO ({cols}) VALUES ({placeholders})"
            cursor.execute(query_prod, vals)

            # 2. INSERTAR EN INVENTARIO (Aquí está el cambio)
            prod_id = product_data["Id_producto"]
            
            # Obtenemos el ID de la sucursal actual desde la configuración que hicimos en el Paso 1
            current_branch_id = self.current_node["id_sucursal"]
            
            # Ahora enviamos 3 datos: Sucursal, Producto y Cantidad
            query_inv = """
                INSERT INTO INVENTARIO (Id_sucursal, Id_producto, cantidad) 
                VALUES (?, ?, ?)
            """
            cursor.execute(query_inv, (current_branch_id, prod_id, initial_qty))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error creando producto+inventario: {e}")
            raise e
        finally:
            conn.close()

    def update_inventory_quantity(self, product_id, new_quantity):
        """
        Actualiza la cantidad. Si el registro no existe en inventario, LO CREA.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            sucursal_id = self.current_node["id_sucursal"]

            # 1. Intentamos ACTUALIZAR
            query_update = """
                UPDATE INVENTARIO 
                SET cantidad = ? 
                WHERE Id_producto = ? AND Id_sucursal = ?
            """
            cursor.execute(query_update, (new_quantity, product_id, sucursal_id))
            
            # 2. Verificamos si alguien fue actualizado
            if cursor.rowcount == 0:
                print(f"ALERTA: Producto {product_id} no tenía inventario. Creándolo ahora...")
                
                # Si rowcount es 0, significa que no existía. Hacemos INSERT.
                query_insert = """
                    INSERT INTO INVENTARIO (Id_sucursal, Id_producto, cantidad)
                    VALUES (?, ?, ?)
                """
                cursor.execute(query_insert, (sucursal_id, product_id, new_quantity))

            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error actualizando inventario: {e}")
            raise e
        finally:
            conn.close()

    def get_product_stock(self, product_id):
        """
        Obtiene el stock actual de un producto para mostrarlo al editar.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            query = "SELECT cantidad FROM INVENTARIO WHERE id_producto = ?"
            cursor.execute(query, (product_id,))
            row = cursor.fetchone()
            return row[0] if row else 0
        except Exception:
            return 0
        finally:
            conn.close()
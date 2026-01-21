# backend/data_manager.py

import socket
import pyodbc

class DataManager:
    def __init__(self):
        # --- 1. CONFIGURACIÓN DE NODOS ---
        # Aquí ponemos los nombres REALES de tus computadoras
        self.NODES = {
            "GUAYAQUIL": {
                "hostnames": ["MiniPC"],  # <--- Nombre exacto de la PC Matriz
                "db_name": "TechStore_Guayaquil",
                "role": "Publicador (Matriz)",
                "tables": ["SUCURSAL", "PRODUCTO", "INVENTARIO", "CLIENTE", "EMPLEADO", "FACTURA", "DETALLE_FACTURA"]
            },
            "QUITO": {
                "hostnames": ["LAPTOP"],  # <--- Nombre exacto de la Laptop Sucursal
                "db_name": "TechStore_Quito",
                "role": "Suscriptor (Sucursal)",
                "tables": ["CLIENTE", "INVENTARIO", "FACTURA", "DETALLE_FACTURA", "SUCURSAL"]
            }
        }
        
        # --- 2. CREDENCIALES SQL SERVER ---
        self.SERVER_ADDR = "localhost"
        self.DB_USER = "sa"          # <--- Usuario
        self.DB_PASS = "P@ssw0rd"    # <--- Contraseña
        
        # Detectar nodo al iniciar
        self.current_node = self._detect_node()

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
    
    
from backend.connection import get_db_connection
from backend.config import SUPPORTED_TABLES, CURRENT_NODE

class GenericDAO:
    def _check_table_security(self, table_name):
        """Valida que la tabla esté permitida."""
        if table_name not in SUPPORTED_TABLES:
             # Ojo: Aquí podrías implementar la validación contra la BD real si quieres mantener esa "Magia"
             # Por simplicidad, validamos contra la lista estática primero.
            raise ValueError(f"Acceso denegado o tabla no soportada: {table_name}")

    def fetch_table_data(self, table_name):
        self._check_table_security(table_name)
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return columns, rows
        finally:
            conn.close()

    def insert_data(self, table_name, data_dict):
        self._check_table_security(table_name)
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            columns = ", ".join(data_dict.keys())
            placeholders = ", ".join(["?"] * len(data_dict))
            values = list(data_dict.values())
            
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error insertando en {table_name}: {e}")
            raise e
        finally:
            conn.close()

    def update_data(self, table_name, data_dict, id_column, id_value):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # --- CORRECCIÓN: Quitamos el ID del diccionario de datos a actualizar ---
        # Hacemos una copia para no afectar el diccionario original
        data_to_update = data_dict.copy()
        
        # Si el ID viene en los datos (ej: 'Id_sucursal': 1), lo quitamos.
        # El ID se usa en el WHERE, nunca en el SET.
        if id_column in data_to_update:
            del data_to_update[id_column]

        # Ahora generamos el SQL solo con los campos permitidos
        set_clause = ", ".join([f"{k} = ?" for k in data_to_update.keys()])
        values = list(data_to_update.values())
        values.append(id_value) # El ID va al final para el WHERE
        
        query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = ?"
        
        try:
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando {table_name}: {e}")
            raise e
        finally:
            conn.close()

    def delete_data(self, table_name, id_column, id_value):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = f"DELETE FROM {table_name} WHERE {id_column} = ?"
            cursor.execute(query, (id_value,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    def get_next_id(self, table_name, id_column):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = f"SELECT MAX({id_column}) FROM {table_name}"
            cursor.execute(query)
            row = cursor.fetchone()
            max_id = row[0]
            return (max_id + 1) if max_id is not None else 1
        except Exception:
            return 1
        finally:
            conn.close()
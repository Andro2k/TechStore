# backend/data_manager.py

from backend.config import CURRENT_NODE, SUPPORTED_TABLES
from backend.generic_dao import GenericDAO
from backend.services.inventory_service import InventoryService
from backend.connection import get_db_connection

class DataManager:
    def __init__(self):
        # 1. Instanciamos los servicios especializados
        self.dao = GenericDAO()
        self.inventory_service = InventoryService()
        
        # 2. Exponemos la configuración del nodo (Frontend lo necesita para el título y Sidebar)
        self.current_node = CURRENT_NODE
        
        # 3. Detectar tablas dinámicamente (Lógica portada del antiguo backend)
        self.current_node["tables"] = self._get_available_tables_from_db()

    def _get_available_tables_from_db(self):
        """Método interno para filtrar qué tablas mostrar en el Sidebar"""
        existing_tables = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
            cursor.execute(query)
            db_tables = [row[0] for row in cursor.fetchall()]
            conn.close()

            # Intersección: Tablas en BD y Tablas Soportadas
            for table in SUPPORTED_TABLES:
                if table in db_tables:
                    existing_tables.append(table)
            
            print(f"DEBUG: Tablas habilitadas: {existing_tables}")
            return existing_tables
        except Exception as e:
            print(f"ALERTA: Error detectando tablas: {e}")
            return []

    # ==========================================
    # DELEGACIÓN A GENERIC DAO (CRUD Básico)
    # ==========================================
    
    def fetch_table_data(self, table_name):
        return self.dao.fetch_table_data(table_name)

    def insert_data(self, table_name, data_dict):
        return self.dao.insert_data(table_name, data_dict)

    def update_data(self, table_name, data_dict, id_column, id_value):
        return self.dao.update_data(table_name, data_dict, id_column, id_value)
    
    def delete_data(self, table_name, id_column, id_value):
        # Si es un producto, usamos el borrado seguro del servicio de inventario
        if table_name == "PRODUCTO":
            return self.inventory_service.delete_product_secure(id_value)
        return self.dao.delete_data(table_name, id_column, id_value)

    def get_next_id(self, table_name, id_column):
        return self.dao.get_next_id(table_name, id_column)

    # ==========================================
    # DELEGACIÓN A INVENTORY SERVICE (Lógica Compleja)
    # ==========================================

    def create_product_with_inventory(self, product_data, initial_qty):
        return self.inventory_service.create_product_with_inventory(product_data, initial_qty)

    def update_inventory_quantity(self, product_id, new_quantity):
        return self.inventory_service.update_inventory_quantity(product_id, new_quantity)

    def get_product_stock(self, product_id):
        return self.inventory_service.get_product_stock(product_id)
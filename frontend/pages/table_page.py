# frontend/pages/table_page.py

from .base_page import BasePage

class TablePage(BasePage):
    def __init__(self, manager, table_name):
        super().__init__(manager)
        self.table_name = table_name
        
        # Configuramos el título automáticamente
        self.set_title(f"Gestión de {table_name.capitalize()}")
        
    def refresh(self):
        """Método público para recargar los datos"""
        self.load_data(self.table_name)
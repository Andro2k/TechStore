from frontend.pages.base_page import BaseTablePage
from PyQt6.QtWidgets import QMessageBox

class EmployeesPage(BaseTablePage):
    def __init__(self, db_manager):
        # CORRECCIÓN: Quitamos "Cargo" y ponemos "Teléfono"
        headers = ["ID", "Nombre", "Correo", "Teléfono"] 
        super().__init__("Nómina Operativa", headers, db_manager)

    def refresh_data(self):
        nodo = self.get_current_node()
        try:
            data = self.db_manager.obtener_empleados(nodo)
            self.fill_table(data)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
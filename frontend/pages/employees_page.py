# frontend/pages/employees_page.py

from PyQt6.QtWidgets import QMessageBox, QDialog
from .table_page import TablePage
from frontend.forms import EmployeeForm

class EmployeesPage(TablePage):
    def __init__(self, manager):
        super().__init__(manager, "EMPLEADO", enable_actions=True)
        self.btn_add.setText("Contratar Empleado")

    def _get_sucursales_options(self):
        """Helper para obtener lista de sucursales (Nombre, ID)"""
        cols, rows = self.manager.fetch_table_data("SUCURSAL")
        return [(row[1], row[0]) for row in rows]

    def on_add_click(self):
        # Pasamos la lista de sucursales al form
        dialog = EmployeeForm(self, sucursales_list=self._get_sucursales_options())
        
        next_id = self.manager.get_next_id("EMPLEADO", "Id_empleado")
        dialog.set_input_value("Id_empleado", next_id, readonly=True)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_standard_insert(dialog.get_data(), next_id)

    def on_edit_click(self, id_col_name, row_id, row_data, columns):
        dialog = EmployeeForm(self, sucursales_list=self._get_sucursales_options())
        
        # Llenar y bloquear ID
        current_data = dict(zip(columns, row_data))
        dialog.populate_data(current_data)
        dialog.set_input_value("Id_empleado", row_id, readonly=True)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_standard_update(dialog.get_data(), id_col_name, row_id)

    # Helpers simples para no repetir try/except
    def _save_standard_insert(self, data, new_id):
        try:
            self.manager.insert_data("EMPLEADO", data)
            self.refresh()
            QMessageBox.information(self, "Éxito", "Empleado registrado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _save_standard_update(self, data, col_id, val_id):
        try:
            self.manager.update_data("EMPLEADO", data, col_id, val_id)
            self.refresh()
            QMessageBox.information(self, "Éxito", "Empleado actualizado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
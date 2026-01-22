# frontend/pages/sucursales_page.py

from PyQt6.QtWidgets import QMessageBox, QDialog
from .table_page import TablePage
from frontend.forms import SucursalForm

class SucursalesPage(TablePage):
    def __init__(self, manager):
        super().__init__(manager, "SUCURSAL", enable_actions=False)
        self.btn_add.setText("Nueva Sucursal")

    def on_add_click(self):
        """Lógica para el botón Nuevo"""
        dialog = SucursalForm(self)
        
        # 1. Calcular siguiente ID
        next_id = self.manager.get_next_id("SUCURSAL", "Id_sucursal")
        dialog.set_input_value("id_sucursal", next_id, readonly=True)

        # 2. Mostrar formulario
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                self.manager.insert_data("SUCURSAL", data)
                self.refresh()
                QMessageBox.information(self, "Éxito", "Sucursal creada correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear: {e}")

    def on_edit_click(self, id_col_name, row_id, row_data, columns):
        """Lógica para Editar (Sobreescribimos para asegurar que use SucursalForm)"""
        dialog = SucursalForm(self)
        dialog.setWindowTitle(f"Editar Sucursal #{row_id}")
        
        # Llenar datos actuales
        current_data = dict(zip(columns, row_data))
        dialog.populate_data(current_data)
        
        # Bloquear ID
        dialog.set_input_value("id_sucursal", row_id, readonly=True)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            try:
                self.manager.update_data("SUCURSAL", new_data, id_col_name, row_id)
                self.refresh()
                QMessageBox.information(self, "Éxito", "Sucursal actualizada.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Fallo al actualizar: {e}")
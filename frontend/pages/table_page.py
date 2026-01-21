# frontend/pages/table_page.py

from PyQt6.QtWidgets import QMessageBox, QDialog
from .base_page import BasePage
# Importamos los formularios nuevos
from frontend.forms import EmployeeForm, ProductForm 

class TablePage(BasePage):
    def __init__(self, manager, table_name):
        super().__init__(manager)
        self.table_name = table_name
        
        self.set_title(f"Gestión de {table_name.capitalize()}")
        
        # Configuración específica por tabla
        # Solo mostramos el botón "Nuevo" si es EMPLEADO o PRODUCTO
        if self.table_name in ["EMPLEADO", "PRODUCTO"]:
            self.btn_add.show()
            self.btn_add.setText(f"Nuevo {table_name.capitalize()[:-1]}") # "Nuevo Producto"
            
    def refresh(self):
        self.load_data(self.table_name)

    # Sobrescribimos el método del botón Agregar
    def on_add_click(self):
        dialog = None
        
        # 1. Seleccionar el formulario correcto
        if self.table_name == "EMPLEADO":
            dialog = EmployeeForm(self)
        elif self.table_name == "PRODUCTO":
            dialog = ProductForm(self)
            
        # 2. Ejecutar y Guardar
        if dialog:
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                
                try:
                    # Enviar al backend
                    self.manager.insert_data(self.table_name, data)
                    self.refresh() # Recargar tabla para ver el cambio
                    QMessageBox.information(self, "Éxito", "Registro agregado correctamente.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{str(e)}")
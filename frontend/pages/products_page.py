# frontend/pages/products_page.py

from PyQt6.QtWidgets import QMessageBox, QDialog
from .table_page import TablePage  # Heredamos de la página genérica
from frontend.forms import ProductForm

class ProductsPage(TablePage):
    def __init__(self, manager):
        # Inicializamos como la tabla "PRODUCTO" y activamos acciones (True)
        super().__init__(manager, "PRODUCTO", enable_actions=True)
        self.set_title("Gestión de Inventario y Productos")
        self.btn_add.setText("Nuevo Producto")

    def on_add_click(self):
        """Lógica exclusiva para CREAR producto + inventario"""
        # 1. Calculamos ID
        next_id = self.manager.get_next_id("PRODUCTO", "Id_producto")
        
        # 2. Abrimos form
        dialog = ProductForm(self)
        dialog.set_input_value("Id_producto", next_id, readonly=True)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                # Separamos la cantidad (inventario) de los datos del producto
                qty = data.pop("cantidad_inicial", 0) 
                
                # Usamos el método transaccional del manager
                self.manager.create_product_with_inventory(data, qty)
                
                self.refresh()
                QMessageBox.information(self, "Éxito", f"Producto #{next_id} creado con {qty} unidades.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def on_edit_click(self, id_col_name, row_id, row_data, columns):
        """Lógica exclusiva para EDITAR producto + inventario"""
        # 1. Obtener stock actual para mostrarlo
        current_stock = self.manager.get_product_stock(row_id)
        
        dialog = ProductForm(self)
        dialog.setWindowTitle(f"Editar Producto #{row_id}")
        
        # 2. Llenar datos
        current_data = dict(zip(columns, row_data))
        dialog.populate_data(current_data)
        dialog.set_input_value("Id_producto", row_id, readonly=True)
        dialog.set_input_value("cantidad_inicial", current_stock) # Mostramos stock real

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            try:
                # Separar cantidad
                qty = new_data.pop("cantidad_inicial", None)
                
                # Actualizar Producto
                self.manager.update_data("PRODUCTO", new_data, id_col_name, row_id)
                
                # Actualizar Inventario
                if qty is not None:
                    self.manager.update_inventory_quantity(row_id, qty)
                
                self.refresh()
                QMessageBox.information(self, "Actualizado", "Producto y stock actualizados.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Fallo al actualizar: {e}")
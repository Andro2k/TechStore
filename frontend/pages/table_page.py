# frontend/pages/table_page.py

from PyQt6.QtWidgets import (QMessageBox, QDialog, QTableWidgetItem, QWidget, QHBoxLayout, QPushButton)
from PyQt6.QtCore import QSize, Qt
from .base_page import BasePage
from frontend.forms import EmployeeForm, ProductForm, SucursalForm
from frontend.utils import get_icon

class TablePage(BasePage):
    def __init__(self, manager, table_name, enable_actions=False):
        super().__init__(manager)
        self.table_name = table_name
        self.enable_actions = enable_actions

        self.set_title(f"Gestión de {table_name.capitalize()}")

        if self.enable_actions and self.table_name in ["EMPLEADO", "PRODUCTO", "SUCURSAL"]:
            self.btn_add.show()
            self.btn_add.setText(f"Nuevo {table_name.capitalize()[:-1]}")
        else:
            self.btn_add.hide()
            
    def refresh(self):
        self.load_data(self.table_name)

    def load_data(self, table_name):
        self.current_table = table_name
        self.txt_search.clear()
        
        try:
            columns, rows = self.manager.fetch_table_data(table_name)

            display_columns = columns
            if self.enable_actions:
                display_columns = columns + ["Acciones"]
            
            self.table.setColumnCount(len(display_columns))
            self.table.setHorizontalHeaderLabels(display_columns)
            self.table.verticalHeader().setDefaultSectionSize(40)
            self.table.setRowCount(0)

            # Asumimos que ID es la primera columna
            if columns:
                id_col_name = columns[0] 

            for row_idx, row_data in enumerate(rows):
                self.table.insertRow(row_idx)
                
                row_id = row_data[0] 
                
                # 1. Llenar datos normales
                for col_idx, data in enumerate(row_data):
                    val = str(data) if data is not None else ""
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

                # 2. Agregar botones SOLO si está activado
                if self.enable_actions:
                    self._add_action_buttons(row_idx, len(columns), id_col_name, row_id, row_data, columns)

            self.lbl_status.setText(f"{len(rows)} registros cargados.")
            
            self.combo_columns.clear()
            self.combo_columns.addItem("Todo")
            self.combo_columns.addItems(columns)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando tabla: {e}")

    def _add_action_buttons(self, row_idx, col_idx, id_col_name, row_id, row_data, columns):
        """
        Crea un contenedor con botones pequeños y centrados para Editar y Borrar.
        """
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Estilo base para que los botones sean limpios y pequeños ---
        icon_btn_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 0px;
            }
        """

        # --- Botón Editar ---
        btn_edit = QPushButton()
        btn_edit.setIcon(get_icon("edit.svg"))
        btn_edit.setFixedSize(20, 20)
        btn_edit.setIconSize(QSize(18, 18))
        btn_edit.setToolTip("Editar registro")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Estilo específico con efecto hover azul
        btn_edit.setStyleSheet(icon_btn_style + """
            QPushButton:hover { background-color: rgba(33, 150, 243, 0.4); }
        """)
        btn_edit.clicked.connect(lambda: self.on_edit_click(id_col_name, row_id, row_data, columns))

        # --- Botón Eliminar ---
        btn_delete = QPushButton()
        btn_delete.setIcon(get_icon("trash.svg"))
        btn_delete.setFixedSize(20, 20)
        btn_delete.setIconSize(QSize(18, 18))
        btn_delete.setToolTip("Eliminar registro")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Estilo específico con efecto hover rojo
        btn_delete.setStyleSheet(icon_btn_style + """
            QPushButton:hover { background-color: rgba(244, 67, 54, 0.4); }
        """)
        btn_delete.clicked.connect(lambda: self.on_delete_click(id_col_name, row_id))

        # Agregamos los botones al layout horizontal
        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        
        # Insertamos el contenedor en la celda de la tabla
        self.table.setCellWidget(row_idx, col_idx, container)

    # --- LÓGICA DE ELIMINAR ---
    def on_delete_click(self, id_col_name, row_id):
        reply = QMessageBox.question(
            self, "Confirmar eliminación", 
            f"¿Estás seguro de eliminar el registro #{row_id}?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.manager.delete_data(self.table_name, id_col_name, row_id)
                self.refresh() # Recargar tabla
                QMessageBox.information(self, "Eliminado", "Registro eliminado correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")

    # --- LÓGICA DE EDITAR ---
    def on_edit_click(self, id_col_name, row_id, row_data, columns):
        dialog = None
        
        # 1. Configurar formulario según tabla
        if self.table_name == "EMPLEADO":
            # (Copiar lógica de sucursales del on_add_click anterior)
            cols, rows = self.manager.fetch_table_data("SUCURSAL")
            sucursal_options = [(row[1], row[0]) for row in rows]
            dialog = EmployeeForm(self, sucursales_list=sucursal_options)
            
        elif self.table_name == "PRODUCTO":
            dialog = ProductForm(self)

        elif self.table_name == "SUCURSAL":
            dialog = SucursalForm(self)

        if dialog:
            dialog.setWindowTitle(f"Editar {self.table_name.capitalize()} #{row_id}")
            
            # 2. Empaquetar los datos actuales en un diccionario
            # row_data es una tupla, columns es una lista de nombres. Los unimos.
            current_data = dict(zip(columns, row_data))
            
            # 3. Pre-llenar formulario
            dialog.populate_data(current_data)
            
            # 4. Bloquear el ID (No se debe editar la clave primaria)
            dialog.set_input_value(id_col_name, row_id, readonly=True)

            # 5. Guardar Cambios (UPDATE en vez de INSERT)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                try:
                    self.manager.update_data(self.table_name, new_data, id_col_name, row_id)
                    self.refresh()
                    QMessageBox.information(self, "Éxito", "Registro actualizado.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")
    
    def on_edit_click(self, id_col_name, row_id, row_data, columns):
        dialog = None
        
        # 1. Configuración de formularios
        if self.table_name == "EMPLEADO":
            cols, rows = self.manager.fetch_table_data("SUCURSAL")
            sucursal_options = [(row[1], row[0]) for row in rows]
            dialog = EmployeeForm(self, sucursales_list=sucursal_options)
            
        elif self.table_name == "PRODUCTO":
            dialog = ProductForm(self)
            # --- CORRECCIÓN VISUAL: Cargar el stock actual ---
            current_stock = self.manager.get_product_stock(row_id)
            # Le pasamos el stock al formulario para que no salga vacío
            # Asegúrate que en forms.py el campo se llame "cantidad_inicial" o "cantidad"
            # Aquí asumo que en tu ProductForm el campo se llama "cantidad_inicial"
            dialog.set_input_value("cantidad_inicial", current_stock)

        elif self.table_name == "SUCURSAL":
            dialog = SucursalForm(self)

        if dialog:
            dialog.setWindowTitle(f"Editar {self.table_name.capitalize()} #{row_id}")
            
            # 2. Pre-llenar datos del producto (Nombre, Marca, Precio)
            current_data = dict(zip(columns, row_data))
            dialog.populate_data(current_data)
            
            # 3. Bloquear ID
            dialog.set_input_value(id_col_name, row_id, readonly=True)

            # 4. Guardar Cambios
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                
                # --- AGREGA ESTAS LÍNEAS DE DEPURACIÓN ---
                print("DEBUG: Datos recibidos del formulario:", new_data) 
                # -----------------------------------------

                try:
                    if self.table_name == "PRODUCTO":
                        # Intenta sacar el valor. Si la clave no existe, qty será None.
                        # Asegúrate que "cantidad_inicial" COINCIDA con forms.py
                        qty = new_data.pop("cantidad_inicial", None) 
                        
                        print(f"DEBUG: Cantidad extraída: {qty}")  # <-- Veremos si captura el número

                        # Actualizar Producto
                        self.manager.update_data(self.table_name, new_data, id_col_name, row_id)
                        
                        # Actualizar Inventario (Solo si qty se encontró)
                        if qty is not None:
                            print(f"DEBUG: Actualizando inventario ID {row_id} a {qty}")
                            self.manager.update_inventory_quantity(row_id, qty)
                        else:
                            print("ALERTA: No se encontró 'cantidad_inicial' en el formulario.")

                    else:
                        self.manager.update_data(self.table_name, new_data, id_col_name, row_id)
                    
                    self.refresh()
                    QMessageBox.information(self, "Éxito", "Registro actualizado correctamente.")

                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")
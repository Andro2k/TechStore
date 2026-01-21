# frontend/pages/base_page.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
from frontend.theme import Palette

class BasePage(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        # Layout Vertical
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # 1. Título de la Página
        self.lbl_title = QLabel("Título de Página")
        self.lbl_title.setObjectName("Title") # Para que tome el estilo CSS
        self.layout.addWidget(self.lbl_title)

        # 2. Tabla (El corazón de la página)
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Solo lectura
        self.layout.addWidget(self.table)

        # 3. Barra de estado inferior (dentro de la página)
        self.lbl_status = QLabel("Listo")
        self.lbl_status.setObjectName("Badge")
        self.lbl_status.setStyleSheet(f"color: {Palette.Text_Tertiary};")
        self.layout.addWidget(self.lbl_status)

    def set_title(self, title):
        self.lbl_title.setText(title)

    def load_data(self, table_name):
        """Lógica genérica para llenar la tabla"""
        try:
            columns, rows = self.manager.fetch_table_data(table_name)
            
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)
            self.table.setRowCount(0)

            for row_idx, row_data in enumerate(rows):
                self.table.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.table.setItem(row_idx, col_idx, item)
            
            self.lbl_status.setText(f"{len(rows)} registros encontrados.")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar {table_name}: {e}")
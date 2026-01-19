# frontend/pages/base_page.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt

# from frontend.theme import STYLES

class BaseTablePage(QWidget):
    def __init__(self, title, headers, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 20px; color: #0078d7; font-weight: bold;")
        
        btn_refresh = QPushButton("Actualizar Datos")
        btn_refresh.setFixedWidth(150)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(self.refresh_data) # Llama al método que las hijas sobrescribirán

        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(btn_refresh)
        self.layout.addLayout(header_layout)

        # Tabla
        self.table = QTableWidget()
        # self.table.setStyleSheet(STYLES["table"])
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

    def refresh_data(self):
        """Este método debe ser sobrescrito por las clases hijas"""
        pass
        
    def fill_table(self, data):
        """Método utilitario para llenar la tabla"""
        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(data):
            self.table.insertRow(row_idx)
            for col_idx, val in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))
                
    def get_current_node(self):
        main_window = self.window()
        if hasattr(main_window, 'combo_sede'):
            return main_window.combo_sede.currentText()
        return None
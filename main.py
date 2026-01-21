import sys
import socket
import pyodbc
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt

# 1. CORRECCIÓN EN IMPORTS:
from frontend.components import Sidebar
from frontend.theme import get_main_stylesheet  # <--- Asegúrate de que sea esta función

class TechStoreViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- CONFIGURACIÓN DE NODOS ---
        self.NODES = {
            "GUAYAQUIL": {
                "hostnames": ["DESKTOP-GUAYAQUIL", "PC-MAIN"], 
                "db_name": "TechStore_Guayaquil",
                "role": "Publicador (Matriz)",
                "tables": ["SUCURSAL", "PRODUCTO", "INVENTARIO", "CLIENTE", "EMPLEADO", "FACTURA", "DETALLE_FACTURA"]
            },
            "QUITO": {
                "hostnames": ["DESKTOP-QUITO", "LAPTOP-SUCURSAL"],
                "db_name": "TechStore_Quito",
                "role": "Suscriptor (Sucursal)",
                "tables": ["CLIENTE", "INVENTARIO", "FACTURA", "DETALLE_FACTURA", "SUCURSAL"]
            }
        }

        # Configuración SQL
        self.SERVER_ADDR = "localhost"
        self.DB_USER = ""
        self.DB_PASS = ""

        self.current_node = self.detect_node()
        self.init_ui()

    def detect_node(self):
        pc_name = socket.gethostname()
        for node_key, config in self.NODES.items():
            if pc_name in config["hostnames"]:
                return {"key": node_key, **config}
        return {"key": "GUAYAQUIL", **self.NODES["GUAYAQUIL"]}

    def get_connection(self):
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.SERVER_ADDR};"
            f"DATABASE={self.current_node['db_name']};"
        )
        if self.DB_USER and self.DB_PASS:
            conn_str += f"UID={self.DB_USER};PWD={self.DB_PASS};"
        else:
            conn_str += "Trusted_Connection=yes;"

        try:
            return pyodbc.connect(conn_str)
        except Exception as e:
            QMessageBox.critical(self, "Error de Conexión", f"Error: {str(e)}")
            return None

    def init_ui(self):
        self.setWindowTitle(f"TechStore - {self.current_node['key']}")
        self.resize(1100, 700)
        
        # 2. CORRECCIÓN EN LA LLAMADA:
        # Usa la función correcta y SIN argumentos (borra el 'True' o 'get_ident')
        self.setStyleSheet(get_main_stylesheet()) 

        # Widget Central Contenedor
        main_container = QWidget()
        self.setCentralWidget(main_container)
        
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(self.current_node["tables"], self.current_node)
        self.sidebar.table_selected.connect(self.load_data)
        main_layout.addWidget(self.sidebar)

        # Área de Contenido
        content_area = QWidget()
        content_area.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_table_title = QLabel("Seleccione una tabla")
        self.lbl_table_title.setObjectName("Title")
        content_layout.addWidget(self.lbl_table_title)

        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(False)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        content_layout.addWidget(self.table_widget)

        self.lbl_status = QLabel(f"Conectado a: {self.current_node['db_name']}")
        self.lbl_status.setObjectName("Badge")
        content_layout.addWidget(self.lbl_status)

        main_layout.addWidget(content_area)

    def load_data(self, table_name):
        self.lbl_table_title.setText(f"Vista: {table_name}")
        
        conn = self.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)
            self.table_widget.setRowCount(0)

            for row_idx, row_data in enumerate(rows):
                self.table_widget.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                    self.table_widget.setItem(row_idx, col_idx, item)
            
            self.lbl_status.setText(f"{len(rows)} registros cargados desde {table_name}")
            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "Error SQL", f"Error al cargar datos:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TechStoreViewer()
    window.show()
    sys.exit(app.exec())
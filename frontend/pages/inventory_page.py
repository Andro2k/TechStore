# frontend/pages/inventory_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from frontend.theme import STYLES, asset_url

class InventoryPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        # Layout Principal (Horizontal: Formulario | Tabla)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # --- IZQUIERDA: FORMULARIO DE ALTA ---
        form_card = QFrame()
        form_card.setStyleSheet(STYLES["card"]) # Reutilizamos estilo de tarjeta
        form_card.setFixedWidth(320)
        
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        # Título del Form
        header_form = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(QIcon(asset_url("inventory.svg")).pixmap(24, 24))
        title_form = QLabel("Nuevo Producto")
        title_form.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        
        header_form.addWidget(icon_lbl)
        header_form.addWidget(title_form)
        header_form.addStretch()
        form_layout.addLayout(header_form)

        # Campos de Texto
        self.inp_prod = self.create_input("Nombre del Producto")
        self.inp_marca = self.create_input("Marca / Fabricante")
        self.inp_precio = self.create_input("Precio Unitario ($)")
        self.inp_stock = self.create_input("Stock Inicial")

        # Etiquetas y Campos
        form_layout.addWidget(QLabel("Producto:"))
        form_layout.addWidget(self.inp_prod)
        form_layout.addWidget(QLabel("Marca:"))
        form_layout.addWidget(self.inp_marca)
        
        # Fila doble para Precio y Stock
        row_price_stock = QHBoxLayout()
        vbox_p = QVBoxLayout()
        vbox_p.addWidget(QLabel("Precio:"))
        vbox_p.addWidget(self.inp_precio)
        
        vbox_s = QVBoxLayout()
        vbox_s.addWidget(QLabel("Stock:"))
        vbox_s.addWidget(self.inp_stock)
        
        row_price_stock.addLayout(vbox_p)
        row_price_stock.addLayout(vbox_s)
        form_layout.addLayout(row_price_stock)

        form_layout.addStretch()

        # Botón Guardar (Usando estilo del theme)
        self.btn_save = QPushButton("Registrar Item")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(STYLES["btn_primary"]) 
        self.btn_save.clicked.connect(self.save_product)
        form_layout.addWidget(self.btn_save)

        # --- DERECHA: TABLA DE STOCK ---
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        # Header Tabla
        header_table = QHBoxLayout()
        title_table = QLabel("Inventario en Bodega")
        title_table.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.btn_refresh = QPushButton(" Actualizar")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setStyleSheet(STYLES["btn_outline"]) # Estilo bordeado
        self.btn_refresh.setIcon(QIcon(asset_url("refresh.svg")))
        self.btn_refresh.clicked.connect(self.refresh_data)

        header_table.addWidget(title_table)
        header_table.addStretch()
        header_table.addWidget(self.btn_refresh)
        table_layout.addLayout(header_table)

        # Tabla
        self.table = QTableWidget()
        self.table.setStyleSheet(STYLES["table"]) # Estilo unificado
        headers = ["ID", "Producto", "Marca", "Precio", "Stock Local"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Ajuste de columnas
        self.table.setColumnWidth(0, 50) # ID pequeño
        self.table.setColumnWidth(4, 80) # Stock pequeño
        
        table_layout.addWidget(self.table)

        # Añadir paneles al layout principal
        main_layout.addWidget(form_card)
        main_layout.addWidget(table_container)

    def create_input(self, placeholder):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setStyleSheet(STYLES["input"])
        return inp

    def get_current_node(self):
        main_window = self.window()
        if hasattr(main_window, 'combo_sede'):
            return main_window.combo_sede.currentText()
        return None

    def save_product(self):
        nodo = self.get_current_node()
        nombre = self.inp_prod.text()
        marca = self.inp_marca.text()
        precio = self.inp_precio.text()
        stock = self.inp_stock.text()

        if not all([nombre, marca, precio, stock]):
            QMessageBox.warning(self, "Atención", "Todos los campos son obligatorios.")
            return

        try:
            msg = self.db_manager.registrar_producto(nodo, nombre, marca, precio, stock)
            QMessageBox.information(self, "Éxito", msg)
            
            # Limpiar y recargar
            self.inp_prod.clear()
            self.inp_marca.clear()
            self.inp_precio.clear()
            self.inp_stock.clear()
            self.refresh_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{str(e)}")

    def refresh_data(self):
        nodo = self.get_current_node()
        if not nodo: return
        try:
            data = self.db_manager.obtener_inventario(nodo)
            self.table.setRowCount(0)
            for row_idx, row_data in enumerate(data):
                self.table.insertRow(row_idx)
                for col_idx, val in enumerate(row_data):
                    # Formato de dinero para columna Precio (índice 3)
                    if col_idx == 3:
                        val = f"${float(val):.2f}"
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))
        except Exception as e:
            print(f"Error cargando inventario: {e}")
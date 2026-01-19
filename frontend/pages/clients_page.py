# frontend/pages/clients_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from frontend.theme import STYLES, asset_url # Importamos el helper de iconos

class ClientsPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        # Layout Principal Horizontal (Izquierda: Form, Derecha: Tabla)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # --- SECCIÓN IZQUIERDA: FORMULARIO ---
        form_container = QFrame()
        form_container.setStyleSheet(STYLES["card"]) # Estilo de tarjeta blanca/oscura
        form_container.setFixedWidth(320) # Ancho fijo para el formulario
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        # Título del Formulario con Icono
        header_form = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(QIcon(asset_url("clients.svg")).pixmap(24, 24)) # Icono SVG
        title_form = QLabel("Nuevo Cliente")
        title_form.setStyleSheet(STYLES["h2"])
        header_form.addWidget(icon_lbl)
        header_form.addWidget(title_form)
        header_form.addStretch()
        form_layout.addLayout(header_form)

        # Campos
        self.inp_nombre = self.create_input("Nombre Completo")
        self.inp_direccion = self.create_input("Dirección")
        self.inp_telefono = self.create_input("Teléfono")
        self.inp_correo = self.create_input("Correo Electrónico")

        form_layout.addWidget(QLabel("Nombre:"))
        form_layout.addWidget(self.inp_nombre)
        form_layout.addWidget(QLabel("Dirección:"))
        form_layout.addWidget(self.inp_direccion)
        form_layout.addWidget(QLabel("Teléfono:"))
        form_layout.addWidget(self.inp_telefono)
        form_layout.addWidget(QLabel("Correo:"))
        form_layout.addWidget(self.inp_correo)

        form_layout.addStretch()

        # Botón Guardar
        self.btn_save = QPushButton("Guardar Cliente")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        # Usamos el estilo btn_primary definido en theme.py (si existe) o inline
        self.btn_save.setStyleSheet(STYLES["btn_primary"])
        self.btn_save.clicked.connect(self.save_client)
        form_layout.addWidget(self.btn_save)

        # --- SECCIÓN DERECHA: TABLA ---
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        # Header de Tabla
        header_table = QHBoxLayout()
        title_table = QLabel("Directorio Registrado")
        title_table.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.btn_refresh = QPushButton(" Actualizar Lista")
        self.btn_refresh.setIcon(QIcon(asset_url("refresh.svg"))) # Icono de refrescar (necesitas este svg o quita la linea)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setStyleSheet(STYLES["sidebar_btn"]) # Reutilizamos estilo o creamos uno "outline"
        self.btn_refresh.clicked.connect(self.refresh_data)

        header_table.addWidget(title_table)
        header_table.addStretch()
        header_table.addWidget(self.btn_refresh)
        table_layout.addLayout(header_table)

        # Tabla
        self.table = QTableWidget()
        self.table.setStyleSheet(STYLES["table"])
        columns = ["ID", "Nombre", "Dirección", "Teléfono", "Correo"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Ocultar columna de ID si quieres que sea mas limpio (Opcional)
        self.table.setColumnWidth(0, 50) 
        
        table_layout.addWidget(self.table)

        # Añadir al layout principal
        main_layout.addWidget(form_container)
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

    def save_client(self):
        nodo = self.get_current_node()
        nombre = self.inp_nombre.text()
        direccion = self.inp_direccion.text()
        telf = self.inp_telefono.text()
        correo = self.inp_correo.text()

        if not all([nombre, direccion, telf, correo]):
            QMessageBox.warning(self, "Campos Vacíos", "Por favor llena toda la información.")
            return

        try:
            msg = self.db_manager.registrar_cliente(nodo, nombre, direccion, telf, correo)
            QMessageBox.information(self, "Éxito", msg)
            
            # Limpiar campos y recargar tabla
            self.inp_nombre.clear()
            self.inp_direccion.clear()
            self.inp_telefono.clear()
            self.inp_correo.clear()
            self.refresh_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error al Guardar", f"No se pudo registrar:\n{str(e)}")

    def refresh_data(self):
        nodo = self.get_current_node()
        if not nodo: return
        
        try:
            # Reutilizamos la función del backend
            data = self.db_manager.obtener_clientes(nodo)
            
            self.table.setRowCount(0)
            for row_idx, row_data in enumerate(data):
                self.table.insertRow(row_idx)
                for col_idx, val in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))
                    
        except Exception as e:
            print(f"Error cargando tabla: {e}")
# frontend/pages/base_page.py

from PyQt6.QtWidgets import (
    QDoubleSpinBox, QSpinBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit, 
    QComboBox, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from frontend.theme import Palette, STYLES
from frontend.utils import get_icon

class BasePage(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        # Layout Principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10,10,10,10)
        self.layout.setSpacing(8)

        # 1. HEADER (Título + Buscador)
        self._setup_top_bar()

        # 2. TABLA
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Estilo de tabla integrado aquí para asegurar que se vea bien
        self.table.setStyleSheet(f"""
            QTableWidget {{ background-color: {Palette.Bg_Surface}; border: none; gridline-color: {Palette.Border_Light}; }}
            QHeaderView::section {{ background-color: {Palette.Bg_Main}; color: {Palette.Text_Secondary}; padding: 8px; border: none; font-weight: bold; }}
        """)
        
        self.layout.addWidget(self.table)

        # 3. FOOTER (Status)
        self.lbl_status = QLabel("Listo")
        self.lbl_status.setObjectName("Badge")
        self.layout.addWidget(self.lbl_status)

    def _setup_top_bar(self):
        # ... (Tu código anterior del frame y layout) ...
        top_frame = QFrame()
        top_frame.setFixedHeight(48)
        top_frame.setStyleSheet(STYLES["top_bar"])
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(10,5,10,5)

        # A. Título
        self.lbl_title = QLabel("Título")
        self.lbl_title.setObjectName("Title")
        
        # B. Controles
        self.combo_columns = QComboBox()
        self.combo_columns.setStyleSheet(STYLES["combo_box"])
        self.combo_columns.setPlaceholderText("Columna...")
        
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Buscar...")
        self.txt_search.setStyleSheet(STYLES["input_box"])
        self.txt_search.setFixedWidth(210)
        self.txt_search.textChanged.connect(self.filter_data)

        # --- NUEVO BOTÓN AGREGAR ---
        self.btn_add = QPushButton("Nuevo")
        self.btn_add.setIcon(get_icon("plus.svg"))
        self.btn_add.setStyleSheet(STYLES["btn_primary"]) 
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.on_add_click)
        self.btn_add.hide()

        # Botón Refresh
        btn_refresh = QPushButton()
        btn_refresh.setIcon(get_icon("refresh.svg"))
        btn_refresh.setFixedSize(32, 32)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(STYLES["btn_outlined"])
        btn_refresh.clicked.connect(lambda: self.load_data(self.current_table))

        top_layout.addWidget(self.lbl_title)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_add)
        top_layout.addWidget(QLabel("Filtrar:"))
        top_layout.addWidget(self.combo_columns)
        top_layout.addWidget(self.txt_search)
        top_layout.addWidget(btn_refresh)

        self.layout.addWidget(top_frame)

    # Método placeholder para ser sobrescrito
    def on_add_click(self):
        pass

    def set_title(self, title):
        self.lbl_title.setText(title)

    def load_data(self, table_name):
        """Carga datos y configura los filtros automáticamente"""
        self.current_table = table_name
        self.txt_search.clear()
        
        try:
            columns, rows = self.manager.fetch_table_data(table_name)
            
            # 1. Configurar Tabla
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)
            self.table.setRowCount(0)

            for row_idx, row_data in enumerate(rows):
                self.table.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    val = str(data) if data is not None else ""
                    item = QTableWidgetItem(val)
                    item.setToolTip(val)
                    self.table.setItem(row_idx, col_idx, item)
            
            self.lbl_status.setText(f"{len(rows)} registros cargados.")

            # 2. Configurar el ComboBox con las columnas reales
            self.combo_columns.clear()
            self.combo_columns.addItem("Todo")
            self.combo_columns.addItems(columns)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar {table_name}: {e}")

    def filter_data(self):
        """Lógica de filtrado en tiempo real (Frontend-side)"""
        search_text = self.txt_search.text().lower().strip()
        col_idx = self.combo_columns.currentIndex() # 0 es "Todo", 1 es Columna 1...
        
        row_count = self.table.rowCount()
        hidden_count = 0

        for row in range(row_count):
            match = False
            
            # Caso 1: Buscar en una columna específica
            if col_idx > 0:
                # Restamos 1 porque el índice 0 del combo es "Todo"
                target_col = col_idx - 1 
                item = self.table.item(row, target_col)
                if item and search_text in item.text().lower():
                    match = True
            
            # Caso 2: Buscar en TODAS las columnas (si seleccionó "Todo")
            else:
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break # Si encontramos coincidencia en una celda, mostramos la fila
            
            # Ocultar o Mostrar fila
            self.table.setRowHidden(row, not match)
            if not match:
                hidden_count += 1

        # Actualizar estado
        visible_rows = row_count - hidden_count
        self.lbl_status.setText(f"Mostrando {visible_rows} de {row_count} registros.")
    
    def set_input_value(self, field_name, value, readonly=False):
        """
        Asigna un valor a un campo y opcionalmente lo bloquea
        para que el usuario no pueda editarlo.
        """
        if field_name in self.inputs:
            widget = self.inputs[field_name]
            
            # 1. Asignar valor según el tipo de widget
            if isinstance(widget, QLineEdit):
                widget.setText(str(value))
                if readonly:
                    widget.setReadOnly(True)
            
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(float(value) if isinstance(widget, QDoubleSpinBox) else int(value))
                if readonly:
                    widget.setReadOnly(True) # El usuario puede ver pero no cambiar
                    widget.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons) # Ocultar flechitas

            # 2. Estilo visual para campos "Solo Lectura"
            if readonly:
                widget.setStyleSheet(f"""
                    background-color: {Palette.Bg_Main}; 
                    color: {Palette.Text_Tertiary};
                    border: 1px solid {Palette.Border_Light};
                    font-weight: bold;
                """)
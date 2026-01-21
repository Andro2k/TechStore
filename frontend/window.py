# frontend/window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QStackedWidget)
from .components import Sidebar
from .theme import get_main_stylesheet
from .pages.table_page import TablePage

class TechStoreWindow(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.manager = data_manager
        self.node_info = self.manager.current_node
        self.pages = {} 
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"TechStore - {self.node_info['key']}")
        self.resize(1100, 700)
        self.setStyleSheet(get_main_stylesheet())

        # Contenedor Principal
        main_container = QWidget()
        self.setCentralWidget(main_container)
        
        # Layout Horizontal (Sidebar | Stack)
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. SIDEBAR
        self.sidebar = Sidebar(self.node_info["tables"], self.node_info)
        self.sidebar.table_selected.connect(self.switch_page) 
        main_layout.addWidget(self.sidebar)

        # 2. AREA DE CONTENIDO (QStackedWidget)
        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentArea") 
        
        # --- GENERACIÓN DINÁMICA DE PÁGINAS ---
        for table_name in self.node_info["tables"]:
            page = TablePage(self.manager, table_name)
            
            self.stack.addWidget(page)
            self.pages[table_name] = page

        main_layout.addWidget(self.stack)

        # Cargar la primera página por defecto si existen tablas
        if self.node_info["tables"]:
            first_table = self.node_info["tables"][0]
            self.switch_page(first_table)
            # Opcional: Marcar visualmente el primer botón del sidebar
            self.sidebar.buttons[0].setChecked(True) 

    def switch_page(self, table_name):
        """Cambia la página visible en el stack"""
        if table_name in self.pages:
            target_page = self.pages[table_name]
            
            # 1. Ponemos la página al frente
            self.stack.setCurrentWidget(target_page)
            
            # 2. Le decimos que cargue los datos frescos
            target_page.refresh()
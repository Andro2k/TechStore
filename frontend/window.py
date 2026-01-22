# frontend/window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QStackedWidget)

from frontend.pages.employees_page import EmployeesPage
from frontend.pages.products_page import ProductsPage
from frontend.pages.sucursales_page import SucursalesPage
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
        self.resize(1200, 600)
        self.setStyleSheet(get_main_stylesheet())

        main_container = QWidget()
        self.setCentralWidget(main_container)
        
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0,5,0,5)
        main_layout.setSpacing(0)

        # --- 1. DEFINICIÓN DE GRUPOS ---
        # Definimos la estructura ideal
        full_groups = {
            "Recursos Humanos": ["EMPLEADO", "SUCURSAL"],
            "Logística":        ["PRODUCTO", "INVENTARIO"], # PRODUCTO debe estar aquí
            "Facturación":      ["FACTURA", "DETALLE_FACTURA", "CLIENTE"]
        }

        # --- 2. FILTRADO POR PERMISOS ---
        allowed_tables = self.node_info["tables"]
        final_menu_structure = {}

        for group, tables in full_groups.items():
            valid_tables = [t for t in tables if t in allowed_tables]
            
            if valid_tables:
                final_menu_structure[group] = valid_tables
        
        # Cualquier tabla suelta que no pusimos en grupos (por si acaso)
        grouped_tables = [t for sublist in final_menu_structure.values() for t in sublist]
        orphans = [t for t in allowed_tables if t not in grouped_tables]
        if orphans:
            final_menu_structure["Otros"] = orphans

        # --- 3. CREAR SIDEBAR CON GRUPOS ---
        self.sidebar = Sidebar(final_menu_structure, self.node_info)
        self.sidebar.table_selected.connect(self.switch_page) 
        main_layout.addWidget(self.sidebar)

        # 4. AREA DE CONTENIDO
        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentArea") 
        
        # Mapa: Si la tabla está aquí, usa su clase especial. Si no, usa TablePage.
        PAGE_CLASSES = {
            "PRODUCTO": ProductsPage,
            "EMPLEADO": EmployeesPage,
            "SUCURSAL": SucursalesPage
        }

        for table_name in allowed_tables:
            
            if table_name in PAGE_CLASSES:
                # Instanciamos la clase específica (ej. ProductsPage)
                # Nota: Ya no pasamos 'table_name' porque la clase ya sabe cuál es
                page = PAGE_CLASSES[table_name](self.manager)
            else:
                # Instanciamos la genérica para tablas simples (ej. CLIENTE, FACTURA)
                # Aquí determinamos si debe tener botones genéricos o ser solo lectura
                is_editable = table_name in ["SUCURSAL"] # Agrega aquí otras editables simples
                page = TablePage(self.manager, table_name, enable_actions=is_editable)
            
            self.stack.addWidget(page)
            self.pages[table_name] = page

        main_layout.addWidget(self.stack)

        # Cargar la primera tabla válida por defecto
        if allowed_tables:
            self.switch_page(allowed_tables[0])

    def switch_page(self, table_name):
        """Cambia la página visible en el stack"""
        if table_name in self.pages:
            target_page = self.pages[table_name]
            
            # 1. Ponemos la página al frente
            self.stack.setCurrentWidget(target_page)
            
            # 2. Le decimos que cargue los datos frescos
            target_page.refresh()
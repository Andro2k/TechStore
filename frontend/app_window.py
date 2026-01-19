# frontend/app_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QStackedWidget)
from PyQt6.QtCore import Qt

from backend.data_manager import TechStoreDB
from frontend.theme import STYLES

# IMPORTANTE: Importamos el nuevo componente
from frontend.components.sidebar import Sidebar

# Importamos las páginas
from frontend.pages.inventory_page import InventoryPage
from frontend.pages.clients_page import ClientsPage
from frontend.pages.employees_page import EmployeesPage
from frontend.pages.sales_page import SalesPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TechStore ERP")
        self.resize(1280, 800)
        
        self.db_manager = TechStoreDB()
        
        # Aplicamos estilo global básico
        self.setStyleSheet(STYLES["main_window"])
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. SIDEBAR (Instancia del componente)
        self.sidebar = Sidebar()
        # Conectamos la señal personalizada del sidebar al cambio de página
        self.sidebar.page_changed.connect(self.switch_page)
        main_layout.addWidget(self.sidebar)

        # 2. CONTENIDO
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # --- PASO 1: Creamos el Header ---
        # (Aquí ya NO llamará a la lógica todavía)
        content_layout.addLayout(self.create_header())
        
        # --- PASO 2: Creamos el Stack (Ahora self.stack EXISTE) ---
        self.stack = QStackedWidget()
        
        self.page_inv = InventoryPage(self.db_manager)
        self.page_cli = ClientsPage(self.db_manager)
        self.page_emp = EmployeesPage(self.db_manager)
        self.page_sale = SalesPage(self.db_manager)

        self.stack.addWidget(self.page_inv)
        self.stack.addWidget(self.page_cli)
        self.stack.addWidget(self.page_emp)
        self.stack.addWidget(self.page_sale)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_area)

        # --- PASO 3 (CORRECCIÓN): Llamamos a la lógica AQUÍ ---
        # Ahora que self.stack y self.sidebar existen, podemos configurar 
        # la visibilidad inicial sin que explote.
        self.on_node_changed()

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        current = self.stack.currentWidget()
        if hasattr(current, 'refresh_data'):
            current.refresh_data()

    def create_header(self):
        layout = QHBoxLayout()
        
        lbl = QLabel("Nodo Activo /")
        lbl.setStyleSheet("color: #666; font-weight: bold; font-size: 14px;")
        
        self.combo_sede = QComboBox()
        self.combo_sede.setStyleSheet(STYLES["combobox"])
        self.combo_sede.setFixedWidth(200)
        self.combo_sede.addItems(self.db_manager.nodos.keys())
        
        # Pre-seleccionar Sede
        default_sede = self.db_manager.get_current_node_default()
        self.combo_sede.setCurrentText(default_sede)
        
        self.combo_sede.currentIndexChanged.connect(self.on_node_changed)
        
        layout.addWidget(lbl)
        layout.addWidget(self.combo_sede)
        layout.addStretch()
        
        # ELIMINAR ESTA LÍNEA DE AQUÍ:
        # self.on_node_changed()  <--- ¡BORRAR O COMENTAR ESTO!
        
        return layout

    def on_node_changed(self):
        node_name = self.combo_sede.currentText()
        
        # 1. Actualizar visibilidad del menú
        self.sidebar.update_menu_visibility(node_name)
        
        # 2. Protección de Navegación:
        # Si estamos en la página de Empleados (índice 2) y cambiamos a Quito,
        # nos redirigimos al Dashboard (índice 0) para evitar ver datos prohibidos.
        current_idx = self.stack.currentIndex()
        if "Quito" in node_name and current_idx == 2: # 2 = Page Employees
            self.switch_page(0) # Volver a Dashboard
            # También hay que actualizar visualmente el botón seleccionado en el sidebar
            # (Esto requeriría un método extra en sidebar, pero por ahora el switch_page
            #  visual puede desincronizarse levemente si no lo manejamos. 
            #  Lo ideal es simular un click en el btn dashboard).
            if "dashboard" in self.sidebar.menu_buttons:
                self.sidebar.handle_btn_click(0, "dashboard")

        # 3. Refrescar datos de la página actual
        current_widget = self.stack.currentWidget()
        if hasattr(current_widget, 'refresh_data'):
            # Pequeña protección: Si la página es Empleados y estamos en Quito,
            # no refrescamos porque ya hicimos switch, o fallaría el SQL.
            if not ("Quito" in node_name and isinstance(current_widget, self.page_emp.__class__)):
                 current_widget.refresh_data()
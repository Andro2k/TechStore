# frontend/app_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QPushButton, QStackedWidget, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from backend.data_manager import TechStoreDB
# Importamos STYLES del nuevo theme
from frontend.theme import STYLES, asset_url

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

        # 1. SIDEBAR (Ancho fijo para parecerse a la imagen)
        self.sidebar = self.create_sidebar()
        self.sidebar.setFixedWidth(200) # Fijamos ancho como en el diseño
        main_layout.addWidget(self.sidebar)

        # 2. CONTENIDO
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20,20,20,20) # Márgenes amplios
        
        # Header y contenido
        content_layout.addLayout(self.create_header())
        
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

    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        # Aplicamos el estilo del contenedor
        sidebar.setStyleSheet(STYLES["sidebar_container"])
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(5)

        # --- HEADER DEL SIDEBAR ---
        # Simulamos el "New Project" de la imagen con el nombre de la App
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 0, 20, 20)
        
        # Círculo blanco simple (logo)
        logo_circle = QLabel("TS") 
        logo_circle.setFixedSize(24, 24)
        logo_circle.setStyleSheet("background-color: white; color: black; border-radius: 12px; font-weight: bold; qproperty-alignment: AlignCenter;")
        
        title = QLabel("TechStore")
        title.setObjectName("SidebarTitle")
        
        header_layout.addWidget(logo_circle)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)

        # --- MENU ITEMS ---
        self.btns = []

        # Grupo 1: General
        self.add_sidebar_label(layout, "NAVIGATE")
        self.btns.append(self.add_menu_btn(layout, "Dashboard", "inventory.svg", 0))
        self.btns.append(self.add_menu_btn(layout, "Inventario", "inventory.svg", 0))

        # Grupo 2: Operaciones
        self.add_sidebar_label(layout, "OPERATIONS")
        self.btns.append(self.add_menu_btn(layout, "Clientes", "clients.svg", 1))
        self.btns.append(self.add_menu_btn(layout, "Empleados", "employees.svg", 2))
        self.btns.append(self.add_menu_btn(layout, "Punto de Venta", "sales.svg", 3))

        # Grupo 3: Sistema
        self.add_sidebar_label(layout, "SYSTEM")
        # Botones dummy para rellenar visualmente como en la imagen
        btn_settings = QPushButton("Configuración")
        btn_settings.setStyleSheet(STYLES["sidebar_btn"])
        layout.addWidget(btn_settings)

        layout.addStretch()
        
        # --- FOOTER (Usuario) ---
        user_layout = QHBoxLayout()
        user_layout.setContentsMargins(20, 10, 20, 10)
        
        # Avatar simulado
        avatar = QLabel("JD")
        avatar.setFixedSize(30, 30)
        avatar.setStyleSheet("background-color: #333; color: white; border-radius: 15px; qproperty-alignment: AlignCenter;")
        
        user_lbl = QLabel("Admin User\nadmin@techstore.com")
        user_lbl.setStyleSheet("font-size: 11px; color: #888;")
        
        user_layout.addWidget(avatar)
        user_layout.addWidget(user_lbl)
        user_layout.addStretch()
        
        layout.addLayout(user_layout)

        return sidebar

    def add_sidebar_label(self, parent_layout, text):
        """Añade los títulos pequeños de sección (NAVIGATE, etc)"""
        lbl = QLabel(text)
        lbl.setStyleSheet(STYLES["sidebar_category"])
        parent_layout.addWidget(lbl)

    def add_menu_btn(self, parent_layout, text, icon_file, index):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Aplicamos el estilo de "Píldora"
        btn.setStyleSheet(STYLES["sidebar_btn"])
        
        # Icono (Si tienes los SVGs se verán, si no, solo texto)
        if icon_file:
            btn.setIcon(QIcon(asset_url(icon_file)))
            btn.setIconSize(QSize(18, 18))

        if index == 0 and text == "Dashboard": btn.setChecked(True)
        
        # Solo conectamos si tiene índice válido
        if index is not None:
            btn.clicked.connect(lambda: self.switch_page(index, btn))
            
        parent_layout.addWidget(btn)
        return btn

    def switch_page(self, index, sender_btn):
        self.stack.setCurrentIndex(index)
        for btn in self.btns:
            btn.setChecked(False)
        sender_btn.setChecked(True)
        
        current = self.stack.currentWidget()
        if hasattr(current, 'refresh_data'):
            current.refresh_data()

    def create_header(self):
        # Header simplificado oscuro
        layout = QHBoxLayout()
        
        lbl = QLabel("Nodo Activo /")
        lbl.setStyleSheet("color: #666; font-weight: bold;")
        
        self.combo_sede = QComboBox()
        self.combo_sede.setStyleSheet(STYLES["combobox"])
        self.combo_sede.setFixedWidth(200)
        self.combo_sede.addItems(self.db_manager.nodos.keys())
        self.combo_sede.currentIndexChanged.connect(self.on_node_changed)
        
        layout.addWidget(lbl)
        layout.addWidget(self.combo_sede)
        layout.addStretch()
        return layout

    def on_node_changed(self):
        current = self.stack.currentWidget()
        if hasattr(current, 'refresh_data'):
            current.refresh_data()
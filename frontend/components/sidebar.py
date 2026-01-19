# frontend/components/sidebar.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QIcon
from frontend.theme import STYLES, asset_url

class Sidebar(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setStyleSheet(STYLES["sidebar_container"])
        
        self.width_expanded = 220
        self.width_collapsed = 70
        self.is_expanded = True
        self.setFixedWidth(self.width_expanded)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 10, 0, 10)
        self.layout.setSpacing(10)
        
        self.menu_buttons = {} # <--- CAMBIO 1: Diccionario para identificar botones
        self.labels = [] 

        self.setup_ui()

    def setup_ui(self):
        # ... (Header igual que antes) ...
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 0, 10, 10)
        
        self.logo = QLabel("TS")
        self.logo.setFixedSize(32, 32)
        self.logo.setStyleSheet("background-color: white; color: black; border-radius: 16px; font-weight: bold; qproperty-alignment: AlignCenter;")
        
        self.title_lbl = QLabel("TechStore")
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #E0E0E0; margin-left: 5px;")
        
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet("color: white; font-size: 16px; border: none; background: transparent;")
        self.toggle_btn.clicked.connect(self.toggle_sidebar)

        header_layout.addWidget(self.logo)
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_btn)
        self.layout.addLayout(header_layout)

        # --- MENU ITEMS ---
        # CAMBIO 2: Pasamos un 'key' único a cada botón para poder ocultarlo luego

        # Grupo 1
        self.add_section_label("NAVIGATE")
        self.add_menu_btn("Dashboard", "inventory.svg", 0, key="dashboard", is_active=True)
        self.add_menu_btn("Inventario", "inventory.svg", 0, key="inventory")

        # Grupo 2
        self.add_section_label("OPERATIONS")
        self.add_menu_btn("Clientes", "clients.svg", 1, key="clients")
        
        # Este es el botón crítico que ocultaremos
        self.add_menu_btn("Empleados", "employees.svg", 2, key="employees") 
        
        self.add_menu_btn("Punto de Venta", "sales.svg", 3, key="sales")

        # Grupo 3
        self.add_section_label("SYSTEM")
        self.add_menu_btn("Configuración", "settings.svg", None, key="config")
        
        self.layout.addStretch()
        
        # ... (Footer de usuario igual que antes) ...
        self.user_frame = QFrame()
        user_layout = QHBoxLayout(self.user_frame)
        self.avatar = QLabel("JD")
        self.avatar.setStyleSheet("background-color: #444; color: white; border-radius: 10px;") # simplificado
        self.user_info = QLabel("Admin User")
        self.user_info.setStyleSheet("color: #888;")
        user_layout.addWidget(self.avatar)
        user_layout.addWidget(self.user_info)
        self.layout.addWidget(self.user_frame)

    def add_section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(STYLES["sidebar_category"])
        lbl.setContentsMargins(15, 10, 0, 5)
        self.layout.addWidget(lbl)
        self.labels.append(lbl)

    def add_menu_btn(self, text, icon_name, index, key=None, is_active=False):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(is_active)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(STYLES["sidebar_btn"] + "text-align: left; padding-left: 15px;")
        btn.setFixedHeight(40)
        
        if icon_name:
            btn.setIcon(QIcon(asset_url(icon_name)))
            btn.setIconSize(QSize(20, 20))
            
        # Guardamos el texto original para la animación
        btn.original_text = text 
        
        if index is not None:
            btn.clicked.connect(lambda: self.handle_btn_click(index, key)) # Pasamos key para identificar
            
        self.layout.addWidget(btn)
        
        # Guardamos en el diccionario si tiene key
        if key:
            self.menu_buttons[key] = btn
            
        return btn

    def handle_btn_click(self, index, key):
        # Reset visual de todos
        for k, btn in self.menu_buttons.items():
            btn.setChecked(False)
        
        # Activar el clickeado
        if key and key in self.menu_buttons:
            self.menu_buttons[key].setChecked(True)
            
        self.page_changed.emit(index)

    def toggle_sidebar(self):
        # ... (Misma lógica de animación que te di antes) ...
        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(250)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        if self.is_expanded:
            self.anim.setStartValue(self.width_expanded)
            self.anim.setEndValue(self.width_collapsed)
            self.title_lbl.hide()
            self.user_info.hide()
            for lbl in self.labels: lbl.hide()
            for k, btn in self.menu_buttons.items():
                btn.setText("")
                btn.setStyleSheet(STYLES["sidebar_btn"] + "padding-left: 12px;") 
        else:
            self.anim.setStartValue(self.width_collapsed)
            self.anim.setEndValue(self.width_expanded)
            self.title_lbl.show()
            self.user_info.show()
            for lbl in self.labels: lbl.show()
            for k, btn in self.menu_buttons.items():
                btn.setText(btn.original_text)
                btn.setStyleSheet(STYLES["sidebar_btn"] + "text-align: left; padding-left: 15px;")

        self.anim.start()
        self.setMaximumWidth(self.width_collapsed if self.is_expanded else self.width_expanded)
        self.is_expanded = not self.is_expanded

    # --- NUEVA FUNCIÓN: LÓGICA DE PERMISOS ---
    def update_menu_visibility(self, node_name):
        """
        Oculta o muestra botones según la sede seleccionada.
        Regla: Quito NO tiene tabla EMPLEADO -> Ocultar btn 'employees'.
        """
        # 1. Definir qué sedes tienen acceso completo
        # "Matriz Quito (01)" o "Sede Guayaquil (02)"
        
        # Por defecto mostramos todo
        for btn in self.menu_buttons.values():
            btn.show()
            
        # 2. Aplicar restricciones
        # Si el string contiene "Quito" (detectamos la sede por nombre)
        if "Quito" in node_name:
            if "employees" in self.menu_buttons:
                self.menu_buttons["employees"].hide()
                
        # Si quisieras ocultar configuración en Quito también:
        if "Quito" in node_name and "config" in self.menu_buttons:
            self.menu_buttons["config"].hide()
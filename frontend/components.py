# frontend/components.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, 
    QFrame, QScrollArea, QHBoxLayout
)
# Agregamos QVariantAnimation para mayor control
from PyQt6.QtCore import Qt, pyqtSignal, QVariantAnimation, QEasingCurve, QSize
from .theme import Palette, STYLES
from .utils import get_icon

# --- SidebarButton se mantiene igual ---
class SidebarButton(QPushButton):
    def __init__(self, text, icon_name, table_id, parent=None):
        super().__init__(text, parent)
        self.table_id = table_id
        self.text_original = text
        
        self.setIcon(get_icon(icon_name))
        self.setIconSize(QSize(20, 20))
        
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(STYLES["sidebar_btn"])

class Sidebar(QFrame):
    table_selected = pyqtSignal(str)

    def __init__(self, tables, node_info, parent=None):
        super().__init__(parent)
        self.tables = tables
        self.node_info = node_info
        
        self.setObjectName("SidebarContainer")
        self.setStyleSheet(STYLES["sidebar_container"])
        
        # Dimensiones
        self.full_width = 220
        self.mini_width = 64
        self.is_collapsed = False
        self.buttons = []
        
        # Fijamos ancho inicial
        self.setFixedWidth(self.full_width)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        self._setup_header()
        self._setup_menu()
        self._setup_footer()

        # --- ANIMACIÓN MEJORADA ---
        # Usamos QVariantAnimation para controlar setFixedWidth directamente
        self.anim = QVariantAnimation()
        self.anim.setDuration(400) # Un poco más lento para apreciar la suavidad
        # OutCubic: Empieza rápido y frena muy suavemente (Efecto Premium)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic) 
        self.anim.valueChanged.connect(self.setFixedWidth)
        self.anim.finished.connect(self._on_animation_finished)

    def _setup_header(self):
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet("background: transparent; border: none;")
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(15, 10, 15, 10)
        h_layout.setSpacing(5)

        self.lbl_title = QLabel("TechStore")
        self.lbl_title.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {Palette.Text_Primary}; border:none;")
        
        self.btn_toggle = QPushButton()
        self.btn_toggle.setIcon(get_icon("chevron-left.svg")) 
        self.btn_toggle.setFixedSize(32, 32)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; border-radius: 4px; }}
            QPushButton:hover {{ background: {Palette.Bg_Hover}; }}
        """)
        self.btn_toggle.clicked.connect(self.toggle_sidebar)

        h_layout.addWidget(self.lbl_title)
        h_layout.addStretch()
        h_layout.addWidget(self.btn_toggle)
        self.layout.addWidget(header_frame)

    def _setup_menu(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        
        self.menu_layout = QVBoxLayout(content)
        self.menu_layout.setContentsMargins(10,10,10,10)
        self.menu_layout.setSpacing(2)

        # Mapa de Iconos (Asegúrate de tener estos SVGs o circle.svg)
        ICON_MAP = {
            "SUCURSAL": "home.svg", "PRODUCTO": "box.svg", "INVENTARIO": "archive.svg",
            "CLIENTE": "users.svg", "EMPLEADO": "user.svg", "FACTURA": "file-text.svg",
            "DETALLE_FACTURA": "list.svg"
        }

        self._add_section_label("BASE DE DATOS")
        
        for table in self.tables:
            icon_name = ICON_MAP.get(table, "circle.svg")
            self._add_btn(table.capitalize(), icon_name, table)

        self.menu_layout.addStretch()
        scroll.setWidget(content)
        self.layout.addWidget(scroll)

    def _setup_footer(self):
        self.footer = QFrame()
        self.footer.setFixedHeight(60)
        self.footer.setStyleSheet(f"border: none; border-top: 1px solid {Palette.Border_Light}; background: transparent;")
        
        f_layout = QHBoxLayout(self.footer)
        f_layout.setContentsMargins(15, 10, 15, 10)
        f_layout.setSpacing(10) 
        
        self.lbl_node_icon = QLabel(self.node_info['key'][:2])
        self.lbl_node_icon.setFixedSize(32, 32)
        self.lbl_node_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_node_icon.setStyleSheet(f"background-color: {Palette.Success}; color: {Palette.Bg_Main}; font-weight: bold; border-radius: 16px;")

        self.info_container = QWidget()
        v_layout = QVBoxLayout(self.info_container)
        v_layout.setContentsMargins(0,0,0,0)
        v_layout.setSpacing(0)
        
        lbl_node_name = QLabel(self.node_info['key'])
        lbl_node_name.setStyleSheet(f"border: none; font-size: 12px; font-weight: bold; color: {Palette.Text_Primary};")
        
        lbl_role = QLabel(self.node_info['role'])
        lbl_role.setStyleSheet(f"font-size: 10px; color: {Palette.Text_Secondary};")
        
        v_layout.addWidget(lbl_node_name)
        v_layout.addWidget(lbl_role)

        f_layout.addWidget(self.lbl_node_icon)
        f_layout.addWidget(self.info_container)
        f_layout.addStretch()
        self.layout.addWidget(self.footer)

    def _add_section_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("SectionLabel")
        lbl.setStyleSheet(STYLES["sidebar_section_label"])
        self.menu_layout.addWidget(lbl)

    def _add_btn(self, text, icon, table_id):
        btn = SidebarButton(text, icon, table_id)
        btn.clicked.connect(lambda: self._handle_btn_click(btn))
        self.menu_layout.addWidget(btn)
        self.buttons.append(btn)

    def _handle_btn_click(self, clicked_btn):
        for btn in self.buttons:
            btn.setChecked(btn == clicked_btn)
        self.table_selected.emit(clicked_btn.table_id)

    def toggle_sidebar(self):
        self.anim.stop()
        
        current_width = self.width()
        
        if self.is_collapsed:
            # --- EXPANDIR ---
            self.anim.setStartValue(current_width)
            self.anim.setEndValue(self.full_width)
            self.anim.setDuration(300) # Un poco más rápido para que se sienta ágil
            
            self.btn_toggle.setIcon(get_icon("chevron-left.svg"))
            
            # MOSTRAR TEXTO INMEDIATAMENTE
            # Al poner el texto ahora, aparecerá cortado (Inv...) y se "revelará"
            # conforme la barra crece. Esto elimina la sensación de lag.
            self.lbl_title.show() 
            self.info_container.show()
            for child in self.findChildren(QLabel, "SectionLabel"):
                child.show()
            
            for btn in self.buttons:
                btn.setStyleSheet(STYLES["sidebar_btn"]) 
                btn.setIconSize(QSize(20, 20))           
                btn.setText(btn.text_original) # <--- ¡Aquí está la clave!
            
        else:
            # --- COLAPSAR ---
            self.anim.setStartValue(current_width)
            self.anim.setEndValue(self.mini_width)
            self.anim.setDuration(300)
            
            self.btn_toggle.setIcon(get_icon("menu.svg"))
            
            # Ocultamos todo para que no se vea "aplastado" mientras cierra
            self.lbl_title.hide()
            self.info_container.hide()
            for child in self.findChildren(QLabel, "SectionLabel"):
                child.hide()
                
            for btn in self.buttons:
                btn.setText("") 
                btn.setStyleSheet(STYLES["sidebar_btn"] + "QPushButton { padding: 6px; text-align: center; }")
                btn.setIconSize(QSize(24, 24))

        self.anim.start()
        self.is_collapsed = not self.is_collapsed

    def _on_animation_finished(self):
        # Al terminar la animación, si está expandido, solo nos falta poner el texto.
        pass
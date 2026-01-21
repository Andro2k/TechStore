# frontend/components.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, 
    QFrame, QScrollArea, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QVariantAnimation, QEasingCurve, QSize
from .theme import Palette, STYLES
from .utils import get_icon

# --- Botón del Menú ---
class SidebarButton(QPushButton):
    def __init__(self, text, icon_name, is_parent=False, table_id=None, parent=None):
        super().__init__(text, parent)
        self.table_id = table_id
        self.is_parent = is_parent
        self.text_original = text
        
        self.setIcon(get_icon(icon_name))
        
        if is_parent:
            self.setIconSize(QSize(20, 20))
            self.setStyleSheet(STYLES["sidebar_btn"]) 
        else:
            self.setIconSize(QSize(18, 18)) # Hijos un pelín más pequeños
            # Indentación inicial más marcada (30px)
            self.setStyleSheet(STYLES["sidebar_btn"] + 
                               f"QPushButton {{ padding-left: 30px; color: {Palette.Text_Secondary}; }}")

        self.setCheckable(not is_parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class Sidebar(QFrame):
    table_selected = pyqtSignal(str)

    # 1. ACTUALIZADO: Agregamos 'node_info' al constructor
    def __init__(self, menu_structure, node_info, parent=None):
        super().__init__(parent)
        self.menu_structure = menu_structure
        self.node_info = node_info # <--- Guardamos la info del nodo
        
        self.setObjectName("SidebarContainer")
        self.setStyleSheet(STYLES["sidebar_container"])
        
        self.full_width = 230
        self.mini_width = 64
        self.is_collapsed = False
        
        self.child_buttons = []  
        self.parent_buttons = {} 
        self.submenus = {}       
        
        self.setFixedWidth(self.full_width)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        self._setup_header()
        self._setup_menu()
        self._setup_footer() # <--- Ahora sí funcionará

        self.anim = QVariantAnimation()
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic) 
        self.anim.valueChanged.connect(self.setFixedWidth)
        self.anim.finished.connect(self._on_animation_finished)

    def _setup_header(self):
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet("background: transparent; border: none;")
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(15, 10, 15, 10)
        
        self.lbl_title = QLabel("TechStore")
        self.lbl_title.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {Palette.Text_Primary};")
        
        self.btn_toggle = QPushButton()
        self.btn_toggle.setIcon(get_icon("chevron-left.svg")) 
        self.btn_toggle.setFixedSize(32, 32)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setStyleSheet(f"QPushButton {{ background: transparent; border: none; border-radius: 4px; }} QPushButton:hover {{ background: {Palette.Bg_Hover}; }}")
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
        self.menu_layout.setContentsMargins(10, 5, 10, 5) # Márgenes corregidos
        self.menu_layout.setSpacing(2)
        self.menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        ICON_MAP = {
            "Recursos Humanos": "users.svg", "Logística": "archive.svg",
            "Facturación": "file-text.svg", "Otros": "settings.svg",
            "SUCURSAL": "home.svg", "PRODUCTO": "box.svg", "INVENTARIO": "layers.svg",
            "CLIENTE": "user.svg", "EMPLEADO": "briefcase.svg", 
            "FACTURA": "file.svg", "DETALLE_FACTURA": "list.svg"
        }

        self._add_section_label("MÓDULOS")

        for group_name, tables in self.menu_structure.items():
            if not tables: continue

            group_icon = ICON_MAP.get(group_name, "folder.svg")
            btn_group = SidebarButton(group_name, group_icon, is_parent=True)
            self.menu_layout.addWidget(btn_group)
            
            submenu_frame = QFrame()
            submenu_layout = QVBoxLayout(submenu_frame)
            submenu_layout.setContentsMargins(0, 0, 0, 0)
            submenu_layout.setSpacing(2)
            
            submenu_frame.show() 
            self.submenus[group_name] = submenu_frame
            self.parent_buttons[group_name] = btn_group

            btn_group.clicked.connect(lambda checked, f=submenu_frame: self._toggle_submenu(f))

            for table in tables:
                table_icon = ICON_MAP.get(table, "circle.svg")
                btn_child = SidebarButton(table.capitalize(), table_icon, is_parent=False, table_id=table)
                btn_child.clicked.connect(lambda checked, b=btn_child: self._handle_child_click(b))
                submenu_layout.addWidget(btn_child)
                self.child_buttons.append(btn_child)

            self.menu_layout.addWidget(submenu_frame)

        self.menu_layout.addStretch()
        scroll.setWidget(content)
        self.layout.addWidget(scroll)

    # 2. RESTAURADO: Footer con info del nodo
    def _setup_footer(self):
        self.footer = QFrame()
        self.footer.setFixedHeight(60)
        self.footer.setStyleSheet(f"border-top: 1px solid {Palette.Border_Light}; background: transparent;")
        
        f_layout = QHBoxLayout(self.footer)
        f_layout.setContentsMargins(15, 10, 15, 10)
        f_layout.setSpacing(10) 
        
        # Icono con Iniciales
        initials = self.node_info['key'][:2] if self.node_info else "NO"
        self.lbl_node_icon = QLabel(initials)
        self.lbl_node_icon.setFixedSize(32, 32)
        self.lbl_node_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_node_icon.setStyleSheet(f"""
            background-color: {Palette.Success}; 
            color: {Palette.Bg_Main}; 
            font-weight: bold; border-radius: 16px;
        """)

        # Texto Info (Contenedor para ocultarlo fácil)
        self.info_container = QWidget()
        v_layout = QVBoxLayout(self.info_container)
        v_layout.setContentsMargins(0,0,0,0)
        v_layout.setSpacing(0)
        
        key_text = self.node_info['key'] if self.node_info else "Desconectado"
        role_text = self.node_info['role'] if self.node_info else ""
        
        lbl_node_name = QLabel(key_text)
        lbl_node_name.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {Palette.Text_Primary};")
        
        lbl_role = QLabel(role_text)
        lbl_role.setStyleSheet(f"font-size: 10px; color: {Palette.Text_Secondary};")
        
        v_layout.addWidget(lbl_node_name)
        v_layout.addWidget(lbl_role)

        f_layout.addWidget(self.lbl_node_icon)
        f_layout.addWidget(self.info_container)
        f_layout.addStretch()
        self.layout.addWidget(self.footer)

    def _toggle_submenu(self, frame):
        if frame.isVisible():
            frame.hide()
        else:
            frame.show()
        
        self.menu_layout.invalidate() 
        self.menu_layout.activate()
        self.updateGeometry()
        self.resize(self.width(), self.height() + 1)
        self.resize(self.width(), self.height() - 1)

    def _handle_child_click(self, clicked_btn):
        for btn in self.child_buttons:
            btn.setChecked(False)
        clicked_btn.setChecked(True)
        self.table_selected.emit(clicked_btn.table_id)

    def _add_section_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("SectionLabel")
        lbl.setStyleSheet(STYLES["sidebar_section_label"])
        self.menu_layout.addWidget(lbl)

    # En frontend/components.py

    def toggle_sidebar(self):
        self.anim.stop()
        current = self.width()
        
        if self.is_collapsed: 
            # ==========================================
            # ABRIR (EXPANDIR)
            # ==========================================
            self.anim.setStartValue(current)
            self.anim.setEndValue(self.full_width)
            
            self.btn_toggle.setIcon(get_icon("chevron-left.svg"))
            self.lbl_title.show()
            self.info_container.show()
            
            for btn in self.child_buttons + list(self.parent_buttons.values()):
                btn.setText(btn.text_original)
                # Iconos normales al abrir
                btn.setIconSize(QSize(16, 16) if not btn.is_parent else QSize(20, 20))
                
                if btn.is_parent:
                     btn.setStyleSheet(STYLES["sidebar_btn"])
                else:
                     btn.setStyleSheet(STYLES["sidebar_btn"] + 
                                       f"QPushButton {{ padding-left: 30px; color: {Palette.Text_Secondary}; }}")
            
            for frame in self.submenus.values():
                if frame.property("was_visible"): frame.show()

        else: 
            # ==========================================
            # CERRAR (COLAPSAR)
            # ==========================================
            self.anim.setStartValue(current)
            self.anim.setEndValue(self.mini_width)
            
            self.btn_toggle.setIcon(get_icon("menu.svg"))
            self.lbl_title.hide()
            self.info_container.hide()
            
            for frame in self.submenus.values():
                frame.setProperty("was_visible", frame.isVisible())
                frame.hide()

            # ESTILO MINI (FORZADO MATEMÁTICO)
            # Ancho Barra (64) - Icono (24) = 40px sobrantes.
            # Padding-left: 20px exactos centra el icono.
            mini_style = f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    
                    /* TRUCO PARA CENTRADO PERFECTO */
                    text-align: left; 
                    padding-left: 5px; 
                    margin: 3px; 
                }}
                QPushButton:hover {{
                    background-color: {Palette.Bg_Hover};
                }}
                QPushButton:checked {{
                    background-color: {Palette.Bg_Active};
                    color: {Palette.Success};
                }}
            """

            for btn in self.child_buttons + list(self.parent_buttons.values()):
                btn.setText("") 
                btn.setIconSize(QSize(24, 24)) 
                btn.setStyleSheet(mini_style)
            
        self.anim.start()
        self.is_collapsed = not self.is_collapsed

    def _on_animation_finished(self):
        pass
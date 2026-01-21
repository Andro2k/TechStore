# frontend/components.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, 
    QFrame, QScrollArea, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor
from .theme import Palette, STYLES
from .utils import get_icon

# --- Botón Padre (Grupos como "Recursos Humanos") ---
class SidebarButton(QPushButton):
    def __init__(self, text, icon_name, is_parent=False, table_id=None, parent=None):
        super().__init__(text, parent)
        self.table_id = table_id
        self.is_parent = is_parent
        
        self.setIcon(get_icon(icon_name))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(not is_parent)

        if is_parent:
            self.setIconSize(QSize(20, 20))
            self.setStyleSheet(STYLES["sidebar_btn"]) 
        else:
            self.setIconSize(QSize(18, 18))
            # Padding de 30px para dejar espacio a la línea conectora
            self.setStyleSheet(STYLES["sidebar_btn"] + 
                               f"QPushButton {{ padding-left: 36px; color: {Palette.Text_Secondary}; }}")

# --- Botón Hijo con Líneas (Dibuja la "L") ---
class SubmenuButton(SidebarButton):
    def paintEvent(self, event):
        # 1. Configurar pintor
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 2. Configurar lápiz (Color sutil de las líneas)
        line_color = QColor(Palette.Text_Secondary)
        line_color.setAlphaF(0.3)
        
        pen = QPen(line_color)
        pen.setWidth(1)
        painter.setPen(pen)

        # 3. Coordenadas
        x_pos = 20  
        center_y = self.rect().center().y()

        # A. Línea Vertical (Desde arriba hasta el centro)
        p_top = QPoint(x_pos, 0)
        p_center = QPoint(x_pos, center_y)
        painter.drawLine(p_top, p_center)

        # B. Línea Horizontal (Desde el tallo hacia el icono)
        p_right = QPoint(x_pos + 10, center_y)
        painter.drawLine(p_center, p_right)

        painter.end()

        # 4. Dibujar el botón normal encima (Icono + Texto)
        super().paintEvent(event)


class Sidebar(QFrame):
    table_selected = pyqtSignal(str)

    def __init__(self, menu_structure, node_info, parent=None):
        super().__init__(parent)
        self.menu_structure = menu_structure
        self.node_info = node_info
        
        self.setObjectName("SidebarContainer")
        self.setStyleSheet(f"background-color: {Palette.Bg_Main};")
        self.setFixedWidth(186) 
        
        self.child_buttons = []  
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self._setup_header()
        self._setup_menu()
        self._setup_footer()

    def _setup_header(self):
        header_frame = QFrame()
        header_frame.setFixedHeight(70)
        header_frame.setStyleSheet("background: transparent; border: none;")
        
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(20, 15, 20, 15)
        
        self.lbl_title = QLabel("TechStore")
        self.lbl_title.setStyleSheet(f"font-weight: bold; font-size: 20px; color: {Palette.Text_Primary};")
        
        h_layout.addWidget(self.lbl_title)
        h_layout.addStretch()
        self.layout.addWidget(header_frame)

    def _setup_menu(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {Palette.Bg_Main}; border: none; }}
            QScrollBar:vertical {{ background: {Palette.Bg_Main}; width: 8px; }}
            QScrollBar::handle:vertical {{ background: {Palette.Border_Light}; }}
        """)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content = QWidget()
        content.setObjectName("ScrollContent")
        content.setStyleSheet(f"background-color: {Palette.Bg_Main};")
        
        self.menu_layout = QVBoxLayout(content)
        self.menu_layout.setContentsMargins(10, 5, 10, 5)
        self.menu_layout.setSpacing(2)
        self.menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        ICON_MAP = {
            "Recursos Humanos": "users.svg", "Logística": "archive.svg",
            "Facturación": "file-text.svg", "Otros": "settings.svg",
            "SUCURSAL": "home.svg", "PRODUCTO": "box.svg", "INVENTARIO": "layers.svg",
            "CLIENTE": "user.svg", "EMPLEADO": "briefcase.svg", 
            "FACTURA": "file.svg", "DETALLE_FACTURA": "list.svg"
        }

        self._add_section_label("NAVEGACIÓN")

        for group_name, tables in self.menu_structure.items():
            if not tables: continue

            # Botón Padre
            group_icon = ICON_MAP.get(group_name, "folder.svg")
            btn_group = SidebarButton(group_name, group_icon, is_parent=True)
            self.menu_layout.addWidget(btn_group)
            
            # Contenedor Hijos
            submenu_frame = QFrame()
            sp = submenu_frame.sizePolicy()
            sp.setRetainSizeWhenHidden(False)
            submenu_frame.setSizePolicy(sp)
            
            submenu_layout = QVBoxLayout(submenu_frame)
            submenu_layout.setContentsMargins(0, 0, 0, 0)
            submenu_layout.setSpacing(0)
            
            submenu_frame.hide() 
            
            btn_group.clicked.connect(lambda checked, f=submenu_frame: self._toggle_submenu(f))

            for table in tables:
                table_icon = ICON_MAP.get(table, "circle.svg")

                btn_child = SubmenuButton(table.capitalize(), table_icon, is_parent=False, table_id=table)
                
                btn_child.clicked.connect(lambda checked, b=btn_child: self._handle_child_click(b))
                submenu_layout.addWidget(btn_child)
                self.child_buttons.append(btn_child)

            self.menu_layout.addWidget(submenu_frame)

        self.menu_layout.addStretch()
        scroll.setWidget(content)
        self.layout.addWidget(scroll)

    def _setup_footer(self):
        footer = QFrame()
        footer.setFixedHeight(70)
        footer.setStyleSheet(f"background-color: {Palette.Bg_Main};")
        
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(15, 10, 15, 10)
        f_layout.setSpacing(12) 
        
        initials = self.node_info['key'][:2].upper() if self.node_info else "NA"
        lbl_icon = QLabel(initials)
        lbl_icon.setFixedSize(36, 36)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet(f"background-color: {Palette.Success}; color: {Palette.Bg_Main}; font-weight: bold; border-radius: 18px;")

        info_container = QWidget()
        v_layout = QVBoxLayout(info_container)
        v_layout.setContentsMargins(0,0,0,0)
        v_layout.setSpacing(2)
        
        lbl_name = QLabel(self.node_info['key'] if self.node_info else "Desconectado")
        lbl_name.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {Palette.Text_Primary};")
        
        lbl_role = QLabel(self.node_info['role'] if self.node_info else "Sin Rol")
        lbl_role.setStyleSheet(f"font-size: 11px; color: {Palette.Text_Secondary};")
        
        v_layout.addWidget(lbl_name)
        v_layout.addWidget(lbl_role)

        f_layout.addWidget(lbl_icon)
        f_layout.addWidget(info_container)
        f_layout.addStretch()
        self.layout.addWidget(footer)

    def _toggle_submenu(self, frame):
        if frame.isVisible():
            frame.hide()
        else:
            frame.show()
        
        # Forzar repintado para evitar iconos trabados
        self.menu_layout.invalidate() 
        self.menu_layout.activate()
        self.update()

    def _handle_child_click(self, clicked_btn):
        for btn in self.child_buttons:
            btn.setChecked(False)
        clicked_btn.setChecked(True)
        self.table_selected.emit(clicked_btn.table_id)

    def _add_section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(STYLES["sidebar_section_label"])
        self.menu_layout.addWidget(lbl)
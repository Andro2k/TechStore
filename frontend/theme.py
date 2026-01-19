# frontend/theme.py
import sys
import os

# ==========================================
# 0. SISTEMA DE RUTAS
# ==========================================
def asset_url(filename: str) -> str:
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, "assets", "icons", filename).replace("\\", "/")

# ==========================================
# 1. PALETA DE COLORES (Estilo "Spline" Dark)
# ==========================================
class DarkPalette:
    # Fondos
    Bg_Sidebar     = "#0e0e0e"  # Negro casi puro
    Bg_Main        = "#1a1a1a"  # Fondo general
    Bg_Active_Btn  = "#262626"  # Botones activos / Inputs
    Bg_Card        = "#141414"  # Fondo para tarjetas (ligeramente distinto al main)
    
    # Textos
    Text_Primary   = "#ffffff"
    Text_Secondary = "#888888"
    Text_Category  = "#555555"
    
    # Acentos y Bordes
    Primary        = "#ffffff"
    Border         = "#333333"

c = DarkPalette

# ==========================================
# 2. ESTILOS (QSS Dictionary)
# ==========================================
STYLES = {
    # --- CONTENEDOR PRINCIPAL DEL SIDEBAR ---
    "sidebar_container": f"""
        QWidget#Sidebar {{
            background-color: {c.Bg_Sidebar};
            border-right: 1px solid {c.Border};
        }}
        QLabel#SidebarTitle {{
            background-color: transparent;
            color: {c.Text_Primary};
            font-size: 15px;
            font-weight: bold;
            padding-left: 10px;
        }}
    """,

    # --- CATEGORÍAS ---
    "sidebar_category": f"""
        QLabel {{
            background-color: transparent;
            color: {c.Text_Category};
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            padding-left: 15px;
            padding-top: 15px;
            padding-bottom: 5px;
        }}
    """,

    # --- BOTONES DEL MENÚ ---
    "sidebar_btn": f"""
        QPushButton {{
            background-color: transparent;
            color: {c.Text_Secondary};
            text-align: left;
            padding: 10px 15px;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            margin: 2px 10px;
        }}
        QPushButton:hover {{
            background-color: {c.Bg_Active_Btn};
            color: {c.Text_Primary};
        }}
        QPushButton:checked {{
            background-color: {c.Bg_Active_Btn};
            color: {c.Text_Primary};
            font-weight: bold;
        }}
    """,

    # --- NUEVO: TARJETAS (Cards) --- 
    # (Esto faltaba y causaba el error)
    "card": f"""
        QFrame {{
            background-color: {c.Bg_Card};
            
            border-radius: 12px;
        }}
    """,

    "h2": f"""
        QLabel {{
            background-color: transparent;
            font-size: 16px; font-weight: bold; color: #0078d7;
        }}
    """,

    # --- BOTONES DE ACCIÓN ---
    "btn_primary": f"""
        QPushButton {{
            background-color: {c.Primary};
            color: {c.Bg_Sidebar};
            border: none;
            border-radius: 12;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background-color: {c.Bg_Sidebar};
        }}
        QPushButton:pressed {{
            background-color: {c.Primary};
            margin-top: 2px; /* Efecto de presión */
        }}
    """,

    "btn_outline": f"""
        QPushButton {{
            background-color: transparent;
            border: 1px solid {c.Border};
            color: {c.Primary};
            border-radius: 12;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 13px;
        }}
        QPushButton:hover {{
            border: 1px solid {c.Primary};
            color: {c.Primary};
            background-color: {c.Bg_Main};
        }}
        QPushButton:pressed {{
            background-color: {c.Bg_Sidebar};
        }}
    """,

    # --- NUEVO: INPUTS (Cajas de texto) ---
    "input": f"""
        QLineEdit {{
            background-color: {c.Bg_Active_Btn};
            border: 1px solid {c.Border};
            border-radius: 8px;
            padding: 10px;
            color: {c.Text_Primary};
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border: 1px solid {c.Text_Primary}; /* Borde blanco al enfocar */
            background-color: {c.Bg_Active_Btn};
        }}
    """,

    # --- COMBOBOX ---
    "combobox": f"""
        QComboBox {{
            background-color: {c.Bg_Active_Btn};
            border: 1px solid {c.Border};
            color: {c.Text_Primary};
            border-radius: 8px;
            padding: 8px;
        }}
        QComboBox::drop-down {{ border: none; }}
        QComboBox QAbstractItemView {{
            background-color: {c.Bg_Sidebar};
            color: {c.Text_Primary};
            selection-background-color: {c.Bg_Active_Btn};
            border: 1px solid {c.Border};
        }}
    """,

    # --- NUEVO: TABLAS ---
    "table": f"""
        QTableWidget {{
            background-color: {c.Bg_Card};
            gridline-color: {c.Border};
            border: 1px solid {c.Border};
            color: {c.Text_Primary};
            border-radius: 8px;
        }}
        QHeaderView::section {{
            background-color: {c.Bg_Sidebar};
            color: {c.Text_Secondary};
            padding: 8px;
            border: none;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
        }}
        QTableWidget::item {{
            padding: 5px;
        }}
        QTableCornerButton::section {{
            background-color: {c.Bg_Sidebar};
            border: none;
        }}
    """,
    
    # --- HOJA GLOBAL SIMPLE ---
    "main_window": f"""
        QMainWindow, QWidget {{
            background-color: {c.Bg_Main};
            font-family: "Segoe UI", sans-serif;
            color: {c.Text_Primary};
        }}
    """
}
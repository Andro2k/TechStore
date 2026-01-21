# frontend/theme.py

import sys
import os

# ==========================================
# 1. SISTEMA DE RUTAS
# ==========================================
def asset_url(filename: str) -> str:
    """Devuelve la ruta absoluta de un recurso para usar en QSS (CSS)."""
    if getattr(sys, 'frozen', False):
        # Si es un ejecutable (PyInstaller)
        base_path = sys._MEIPASS
    else:
        # Si estamos en desarrollo:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(current_dir)
    
    # Construimos la ruta: TechStore + assets + icons + archivo
    return os.path.join(base_path, "assets", "icons", filename).replace("\\", "/")

# ==========================================
# 2. PALETA DE COLORES (MATTE DARK)
# ==========================================
class Palette:
    """
    Paleta basada en el diseño 'Untitled UI' (Matte Black).
    """
    # --- Fondos ---
    Bg_Main        = "#121212" # Fondo del sidebar (Muy oscuro)
    Bg_Surface     = "#1A1A1A" # Fondo del contenido principal (Ligeramente más claro)
    Bg_Hover       = "#2d2d2d" # Estado Hover
    Bg_Active      = "#262626" # Estado Activo/Seleccionado
    
    # --- Bordes ---
    Border_Light   = "#333333" # Bordes sutiles
    Border_Focus   = "#555555" # Borde al hacer click
    
    # --- Textos ---
    Text_Primary   = "#FFFFFF" # Títulos
    Text_Secondary = "#9ca3af" # Subtítulos e iconos (Gray 400)
    Text_Tertiary  = "#6b7280" # Texto deshabilitado o muy secundario
    
    # --- Acentos ---
    # En la imagen el acento es sutil (blanco o gris claro), no un color fuerte.
    Accent_Color   = "#FFFFFF" 
    
    # --- Estados ---
    Error          = "#cf6679"
    Success        = "#03dac6"

class Dims:
    """Dimensiones estándar"""
    radius = {
        "card":   "16px",  # Bordes curvos grandes (como en la imagen del contenido)
        "btn":    "6px",   # Botones sidebar
        "input":  "8px",
        "scroll": "4px"
    }
    font = {
        "family": "Segoe UI",
        "h1": "18px",
        "body": "13px",
        "small": "11px"
    }
# ==========================================
# 3. HOJA DE ESTILOS MAESTRA (QSS)
# ==========================================
def get_main_stylesheet() -> str:
    p = Palette
    d = Dims
    
    return f"""
    /* --- RESET GENERAL --- */
    QMainWindow, QWidget {{ 
        background-color: {p.Bg_Main}; 
        color: {p.Text_Primary};
        font-family: "{d.font['family']}";
        font-size: {d.font['body']};
    }}
    
    /* --- CONTENIDO DERECHO --- */
    QWidget#ContentArea {{
        background-color: {p.Bg_Surface};
        border-top-left-radius: 12px;
        border-bottom-left-radius: 12px;
    }}

    /* --- LABELS --- */
    QLabel {{ background: transparent; border: none; }}
    QLabel#Title {{ font-size: {d.font['h1']}; font-weight: bold; margin-bottom: 10px; }}
    QLabel#Subtitle {{ color: {p.Text_Secondary}; }}
    QLabel#Badge {{ color: {p.Text_Secondary}; font-size: {d.font['small']}; }}

    /* --- COMBOBOX (Selector de tablas) --- */
    QComboBox {{
        background-color: {p.Bg_Hover};
        border: 1px solid {p.Border_Light};
        border-radius: {d.radius['input']};
        padding: 5px 10px;
        color: {p.Text_Primary};
        min-width: 200px;
    }}
    QComboBox:hover {{ border: 1px solid {p.Border_Focus}; }}
    QComboBox::drop-down {{ border: none; width: 20px; }}
    QComboBox QAbstractItemView {{
        background-color: {p.Bg_Hover};
        color: {p.Text_Primary};
        selection-background-color: {p.Bg_Active};
        border: 1px solid {p.Border_Light};
    }}

    /* --- TABLAS (QTableWidget) --- */
    QTableWidget {{
        background-color: {p.Bg_Surface};
        gridline-color: {p.Border_Light};
        border: none;
        outline: none;
    }}
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {p.Border_Light};
    }}
    QTableWidget::item:selected {{
        background-color: {p.Bg_Hover};
        color: {p.Text_Primary};
    }}
    QHeaderView::section {{
        background-color: {p.Bg_Surface};
        color: {p.Text_Secondary};
        padding: 8px;
        border: none;
        border-bottom: 2px solid {p.Border_Light};
        font-weight: bold;
        text-transform: uppercase;
        font-size: 11px;
    }}
    
    /* --- SCROLLBARS (Minimalistas) --- */
    QScrollBar:vertical {{ background: {p.Bg_Surface}; width: 8px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: {p.Border_Light}; border-radius: 4px; min-height: 20px; }}
    QScrollBar::handle:vertical:hover {{ background: {p.Border_Focus}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """

# ==========================================
# 4. ESTILOS ESPECÍFICOS PARA WIDGETS
# ==========================================
# theme.py (Solo actualiza el diccionario STYLES)

STYLES = {
    # Botón del sidebar: Texto a la izquierda, sin borde
    "sidebar_btn": f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 6px;
            text-align: left;
            padding: 4px; 
            margin: 2px 0px;
        }}
        QPushButton:hover {{
            background-color: {Palette.Bg_Hover};
        }}
        QPushButton:checked {{
            background-color: {Palette.Bg_Active};
            color: {Palette.Text_Primary};
        }}
    """,
    
    # Etiquetas de sección (ej: "Main", "Projects")
    "sidebar_section_label": f"""
        QLabel {{
            color: {Palette.Text_Tertiary};
            font-weight: bold;
            font-size: 11px;
            text-transform: uppercase;
            padding-left: 12px;
            margin-top: 10px;
            margin-bottom: 5px;
        }}
    """,

    # Contenedor principal
    "sidebar_container": f"""
        QWidget {{
            background-color: {Palette.Bg_Main};
            
        }}
    """,

    # --- BOTONES (Adaptados a TechStore Palette) ---
    
    # 1. Botón Principal (Guardar, Aplicar)
    # Usa tu color de acento (Success) con fondo sutil
    "btn_primary": f"""
        QPushButton {{ 
            background-color: {Palette.Bg_Active}; 
            border: 1px solid {Palette.Success};
            color: {Palette.Success};
            padding: 6px 12px; border-radius: 6px;
            font-size: 12px; font-weight: bold; 
        }}
        QPushButton:hover {{ 
            background-color: {Palette.Success}; 
            color: {Palette.Bg_Main}; /* Texto oscuro al pasar el mouse */
        }}
    """,

    # 2. Botón Secundario / Delineado (Configurar, Gestionar)
    "btn_outlined": f"""
        QPushButton {{ 
            background-color: transparent; 
            color: {Palette.Text_Primary}; 
            padding: 6px 12px; 
            border: 1px solid {Palette.Border_Light}; 
            border-radius: 6px;
            font-size: 12px; font-weight: bold; 
        }} 
        QPushButton:hover {{ 
            border-color: {Palette.Text_Secondary}; 
            background-color: {Palette.Bg_Hover};
        }}
    """,

    # 3. Botón "Peligroso" (Borrar, Desvincular)
    "btn_danger_outlined": f"""
        QPushButton {{
            background-color: transparent; 
            color: {Palette.Error};
            padding: 6px 12px; 
            border: 1px solid {Palette.Error}; 
            border-radius: 6px;
            font-weight: bold;
        }}
        QPushButton:hover {{ 
            background-color: {Palette.Error}; 
            color: {Palette.Text_Primary}; 
        }}
    """,

    # 4. Botón Toggle (Activado/Desactivado) - Ideal para bots o estados
    "btn_toggle": f"""
        QPushButton {{
            background-color: {Palette.Bg_Surface};
            border: 1px solid {Palette.Border_Light};
            border-radius: 6px;
            color: {Palette.Text_Secondary};
            padding: 6px 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {Palette.Bg_Hover};
            color: {Palette.Text_Primary};
        }}
        /* ESTADO ACTIVO (CHECKED) */
        QPushButton:checked {{
            background-color: {Palette.Bg_Active}; 
            border: 1px solid {Palette.Success};
            color: {Palette.Success};
        }}
    """,

    # 5. Botón Fantasma (Iconos pequeños, Editar/Borrar en tablas)
    "btn_icon_ghost": f"""
        QPushButton {{ 
            background: transparent; 
            border: none; 
            border-radius: 6px; 
        }} 
        QPushButton:hover {{ 
            background-color: {Palette.Bg_Hover}; 
        }}
    """,
    
    # 6. Botón de Navegación / Shortcut (Más grande)
    "btn_shortcut": f"""
        QPushButton {{ 
            background-color: {Palette.Bg_Surface}; 
            color: {Palette.Text_Primary};
            border-radius: 8px; 
            border: 1px solid {Palette.Border_Light};
            padding: 10px;
        }} 
        QPushButton:hover {{ 
            background-color: {Palette.Bg_Hover}; 
            border-color: {Palette.Success}; 
        }}
    """,

    # Estilo para la barra de herramientas superior (Buscador + Filtros)
    "top_bar": f"""
        QFrame {{
            background-color: {Palette.Bg_Main};
            border-radius: {Dims.radius['input']};
            border: none;
            padding: 0px;
        }}
    """,

    "input_box": f"""
        QLineEdit {{
            background-color: {Palette.Bg_Surface};
            border: 1px solid {Palette.Border_Light};
            border-radius: {Dims.radius['btn']};
            color: {Palette.Text_Primary};
            padding: 6px 10px;
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border: 1px solid {Palette.Success}; /* Borde verde al escribir */
        }}
    """,

    "combo_box": f"""
        QComboBox {{
            background-color: {Palette.Bg_Surface};
            border: 1px solid {Palette.Border_Light};
            border-radius: {Dims.radius['btn']};
            color: {Palette.Text_Primary};
            padding: 6px 10px;
            min-width: 150px;
        }}
        QComboBox::drop-down {{ border: none; }}
        QComboBox::down-arrow {{ 
            image: url({asset_url("chevron-down.svg")});
            width: 16px; height: 16px;
        }}
        QComboBox::down-arrow::on {{
            image: url({asset_url("chevron-up.svg")}); 
            width: 16px; height: 16px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {Palette.Bg_Hover};
            color: {Palette.Text_Primary};
            selection-background-color: {Palette.Bg_Active};
        }}
    """
}
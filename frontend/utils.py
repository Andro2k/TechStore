# frontend/utils.py
import sys
import os
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_icon(name):
    """Devuelve un QIcon estándar"""
    full_path = resource_path(os.path.join("assets", "icons", name))
    return QIcon(full_path)

def get_colored_pixmap(name, color_hex, size=24):
    """
    Carga un icono SVG/PNG y lo tiñe de un color específico.
    Retorna un QPixmap listo para usarse en un QLabel o dibujar.
    """
    # 1. Cargar el icono base
    icon = get_icon(name)
    pixmap = icon.pixmap(size, size)
    
    # 2. Si el icono no carga, devolvemos un pixmap vacío para evitar crash
    if pixmap.isNull():
        return pixmap

    # 3. Pintar el icono (Técnica de Mascara)
    colored_pixmap = QPixmap(pixmap.size())
    colored_pixmap.fill(Qt.GlobalColor.transparent) # Fondo transparente

    painter = QPainter(colored_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # A. Dibujar el color sólido
    painter.setBrush(QColor(color_hex))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRect(colored_pixmap.rect())
    
    # B. Usar el icono original como máscara de recorte (SourceIn)
    # Esto mantiene el color solo donde había pixeles en el icono original
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
    painter.drawPixmap(0, 0, pixmap)
    
    painter.end()
    
    return colored_pixmap
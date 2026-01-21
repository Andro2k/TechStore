# frontend/utils.py
import sys
import os
from PyQt6.QtGui import QIcon

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_icon(name):
    # Asegúrate de que la ruta coincida con tu estructura
    full_path = resource_path(os.path.join("assets", "icons", name))
    return QIcon(full_path)
# main.py
import sys
from PyQt6.QtWidgets import QApplication
from backend.data_manager import DataManager
from frontend.window import TechStoreWindow

def main():
    app = QApplication(sys.argv)

    try:
        # 1. Iniciar Backend
        backend = DataManager()
        print(f"Backend iniciado en nodo: {backend.current_node['key']}")

        # 2. Iniciar Frontend (Inyectando el backend)
        window = TechStoreWindow(backend)
        window.show()

        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error fatal al iniciar: {e}")

if __name__ == "__main__":
    main()
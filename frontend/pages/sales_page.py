from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QFormLayout, QFrame, QMessageBox)
from PyQt6.QtCore import Qt

class SalesPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Nueva Transacción de Venta")
        title.setStyleSheet("font-size: 20px; color: #0078d7; font-weight: bold;")
        layout.addWidget(title)
        
        # Tarjeta blanca para el formulario
        card = QFrame()
        # card.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #ddd;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.input_cli = QLineEdit()
        self.input_cli.setPlaceholderText("Ej: 101")
        
        self.input_prod = QLineEdit()
        self.input_prod.setPlaceholderText("Ej: 50")
        
        self.input_cant = QLineEdit()
        self.input_cant.setPlaceholderText("Ej: 2")
        
        btn_process = QPushButton("✅ Procesar Factura")
        btn_process.setMinimumHeight(45)
        btn_process.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_process.clicked.connect(self.process_sale)

        form_layout.addRow("ID Cliente:", self.input_cli)
        form_layout.addRow("ID Producto:", self.input_prod)
        form_layout.addRow("Cantidad:", self.input_cant)
        form_layout.addRow("", btn_process)

        card_layout.addLayout(form_layout)
        layout.addWidget(card)
        layout.addStretch()

    def process_sale(self):
        # Obtenemos el nodo desde la ventana principal (truco parent)
        main_window = self.window()
        nodo = main_window.combo_sede.currentText()

        try:
            cli = int(self.input_cli.text())
            prod = int(self.input_prod.text())
            cant = int(self.input_cant.text())

            msg = self.db_manager.registrar_venta(nodo, cli, prod, cant)
            QMessageBox.information(self, "Venta Exitosa", msg)
            
            # Limpiar
            self.input_prod.clear()
            self.input_cant.clear()
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingresa solo números")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
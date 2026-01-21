# frontend/forms.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QHBoxLayout, QPushButton, QMessageBox, QDoubleSpinBox, QSpinBox)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from .theme import Palette, STYLES

class BaseForm(QDialog):
    """Formulario base Modal con validación inteligente"""
    def __init__(self, parent, title):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True) # Esto lo hace Modal (bloquea la ventana de atrás)
        self.setFixedSize(400, 600)
        
        # Quitamos el botón de ayuda (?) de la barra de título para que se vea más limpio
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # Estilos base
        self.setStyleSheet(f"""
            QDialog {{ background-color: {Palette.Bg_Main}; color: {Palette.Text_Primary}; }}
            QLabel {{ color: {Palette.Text_Secondary}; font-weight: bold; margin-top: 10px; }}
            QLineEdit, QSpinBox, QDoubleSpinBox {{
                background-color: {Palette.Bg_Surface};
                border: 1px solid {Palette.Border_Light};
                border-radius: 6px;
                padding: 8px;
                color: {Palette.Text_Primary};
                font-size: 13px;
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{ 
                border: 1px solid {Palette.Success}; 
            }}
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.inputs = {}     # Referencias a los widgets
        self.validators = {} # Reglas de validación: {'campo': 'digits'}

    def add_input(self, label_text, field_name, input_type="text", required=True, validation_rule=None):
        """
        validation_rule: 'digits' (solo números), 'email' (formato correo), None (texto libre)
        """
        lbl = QLabel(label_text + (" *" if required else ""))
        
        widget = None
        if input_type == "text":
            widget = QLineEdit()
            widget.setPlaceholderText(f"Ingrese {label_text.lower()}...")
            # Conectamos la validación en tiempo real
            widget.textChanged.connect(lambda: self.validate_field(field_name))
            
        elif input_type == "money":
            widget = QDoubleSpinBox()
            widget.setMaximum(99999.99)
            widget.setPrefix("$ ")
            widget.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons) # Estilo moderno sin flechas
            
        elif input_type == "number":
            widget = QSpinBox()
            widget.setMaximum(99999999)
            widget.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        self.layout.addWidget(lbl)
        self.layout.addWidget(widget)
        
        # Guardamos referencias
        self.inputs[field_name] = widget
        self.validators[field_name] = {
            "required": required,
            "rule": validation_rule,
            "type": input_type
        }

    def validate_field(self, field_name):
        """Valida un campo específico y cambia su color"""
        widget = self.inputs[field_name]
        rules = self.validators[field_name]
        is_valid = True
        
        # Solo validamos QLineEdit (los SpinBox siempre tienen números válidos)
        if isinstance(widget, QLineEdit):
            text = widget.text().strip()
            
            # 1. Validar Requerido
            if rules["required"] and not text:
                is_valid = False
            
            # 2. Validar Reglas Específicas (Si no está vacío)
            if text and rules["rule"] == "digits":
                # Si contiene algo que NO sea dígito, es inválido
                if not text.isdigit():
                    is_valid = False
            
            # --- CAMBIO DE ESTILO VISUAL ---
            self.set_input_style(widget, is_valid)
            
        return is_valid

    def set_input_style(self, widget, is_valid):
        """Cambia el borde a Rojo o Normal/Verde"""
        if not is_valid:
            # ESTADO ERROR: Borde Rojo
            widget.setStyleSheet(f"""
                border: 1px solid {Palette.Error}; 
                background-color: rgba(207, 102, 121, 0.1);
            """)
        else:
            # ESTADO NORMAL
            widget.setStyleSheet(f"""
                background-color: {Palette.Bg_Surface};
                border: 1px solid {Palette.Border_Light};
            """)

    def validate_all(self):
        """Valida todos los campos antes de guardar"""
        all_valid = True
        first_error_widget = None
        
        for name in self.inputs:
            if not self.validate_field(name):
                all_valid = False
                if not first_error_widget:
                    first_error_widget = self.inputs[name]
        
        if first_error_widget:
            first_error_widget.setFocus() # Llevar cursor al primer error
            QMessageBox.warning(self, "Datos Incompletos", "Por favor corrija los campos marcados en rojo.")
            
        return all_valid

    def add_buttons(self, on_save):
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 20, 0, 0)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(STYLES["btn_outlined"])
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Guardar")
        self.btn_save.setStyleSheet(STYLES["btn_primary"])
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Lógica personalizada para el botón Guardar
        self.btn_save.clicked.connect(lambda: self.attempt_save(on_save))
        
        # HACE QUE LA TECLA ENTER ACTIVE ESTE BOTÓN
        self.btn_save.setDefault(True) 
        self.btn_save.setAutoDefault(True)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_save)
        self.layout.addLayout(btn_layout)

    def attempt_save(self, on_save_callback):
        """Intenta guardar solo si todo es válido"""
        if self.validate_all():
            on_save_callback()

    def get_data(self):
        data = {}
        for name, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                data[name] = widget.text().strip()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                data[name] = widget.value()
        return data

# ==========================================
# FORMULARIOS ESPECÍFICOS
# ==========================================

class EmployeeForm(BaseForm):
    def __init__(self, parent=None):
        super().__init__(parent, "Nuevo Empleado")
        
        self.add_input("ID Empleado", "Id_empleado", "number", required=True)
        self.add_input("Nombre Completo", "nombre", required=True)
        self.add_input("Dirección", "direccion", required=True)
        
        # AQUÍ ESTÁ LA MAGIA DEL TELÉFONO: validation_rule="digits"
        self.add_input("Teléfono", "telefono", required=True, validation_rule="digits")
        
        self.add_input("Correo Electrónico", "correo", required=False) # Correo opcional
        self.add_input("ID Sucursal", "id_sucursal", "number", required=True) 
        
        self.layout.addStretch()
        self.add_buttons(self.accept)

class ProductForm(BaseForm):
    def __init__(self, parent=None):
        super().__init__(parent, "Nuevo Producto")
        
        self.add_input("ID Producto", "Id_producto", "number", required=True)
        self.add_input("Nombre del Producto", "nombre", required=True)
        self.add_input("Marca", "marca", required=True)
        self.add_input("Precio", "precio", "money", required=True)
        
        self.layout.addStretch()
        self.add_buttons(self.accept)
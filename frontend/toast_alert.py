# frontend/components/toast.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGraphicsOpacityEffect, QPushButton)
from PyQt6.QtCore import (Qt, QPropertyAnimation, pyqtProperty, 
                          QRectF, QPoint, QEvent, QEasingCurve)
from PyQt6.QtGui import QColor, QPainter, QPainterPath

# --- IMPORTACIONES PROPIAS INTEGRAS ---
from frontend.theme import Palette, STYLES
from frontend.utils import get_colored_pixmap

# ==========================================
# CONFIGURACIÓN VINCULADA AL THEME
# ==========================================
TOAST_CONFIG = {
    "types": {
        "success": {
            "color": Palette.Success,
            "icon": "check.svg"  # Asegúrate de tener check.svg en assets/icons
        },
        "error": {
            "color": Palette.Error,
            "icon": "trash.svg"  # Usamos trash o alert-circle.svg
        },
        "warning": {
            "color": "#FFD60A",  # Amarillo (puedes agregarlo a Palette si quieres)
            "icon": "warning.svg" # O el icono que tengas
        },
        "info": {
            "color": Palette.Text_Secondary,
            "icon": "info.svg"
        }
    }
}

class ToastIcon(QLabel): # <-- Hereda de QLabel ahora
    """
    Muestra el icono SVG teñido del color correspondiente al tipo de notificación.
    Sin círculo de fondo.
    """
    def __init__(self, tipo, parent=None):
        super().__init__(parent)
        
        # Definimos el tamaño del icono. 24x24 es un buen tamaño estándar.
        icon_size = 24
        self.setFixedSize(icon_size, icon_size)
        
        # 1. Obtener configuración del tipo (ej. 'success')
        config = TOAST_CONFIG["types"].get(tipo, TOAST_CONFIG["types"]["info"])
        
        # El color que antes era para el fondo del círculo, ahora es para el icono.
        color_hex = config["color"] 
        icon_name = config["icon"]

        # 2. Usar la utilidad para colorear el icono con el color del tipo
        # IMPORTANTE: Aquí pasamos 'color_hex' en lugar de "#FFFFFF"
        colored_pixmap = get_colored_pixmap(icon_name, color_hex, size=icon_size)

        # 3. Mostrar el pixmap resultante en este QLabel
        if not colored_pixmap.isNull():
            self.setPixmap(colored_pixmap)
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class ToastNotification(QWidget):
    _active_toasts = []
    MAX_VISIBLE = 4 

    def __init__(self, parent, titulo, mensaje, tipo="info"):
        super().__init__(parent)
        self.parent_ref = parent
        self._progress = 0.0
        
        clean_type = tipo.replace("status_", "")
        if clean_type not in TOAST_CONFIG["types"]:
            clean_type = "info"
        self.tipo = clean_type
        
        self.titulo_text = titulo
        self.mensaje_text = mensaje
        
        # Colores del tema actual
        self.bg_color = QColor(Palette.Bg_Hover)      # Fondo gris oscuro
        self.title_color = Palette.Text_Primary       # Texto blanco
        self.body_color = Palette.Text_Secondary      # Texto gris
        self.accent_color = QColor(TOAST_CONFIG["types"][self.tipo]["color"])
        
        self._configure_window()
        self._setup_ui()
        self._setup_animations()

        if self.parent_ref:
            self.parent_ref.installEventFilter(self)

    def _configure_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(320)

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15) # Margenes definidos a mano o usa LAYOUT si tienes
        main_layout.setSpacing(12)

        # 1. ICONO
        icon_widget = ToastIcon(self.tipo, self)
        main_layout.addWidget(icon_widget, 0, Qt.AlignmentFlag.AlignTop)

        # 2. TEXTOS
        text_container = QWidget()
        text_container.setStyleSheet("background: transparent; border: none;")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        lbl_title = QLabel(self.titulo_text)
        lbl_title.setStyleSheet(f"color: {self.title_color}; font-weight: bold; font-size: 13px;")
        
        lbl_msg = QLabel(self.mensaje_text)
        lbl_msg.setStyleSheet(f"color: {self.body_color}; font-size: 12px;")
        lbl_msg.setWordWrap(True)
        
        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_msg)
        main_layout.addWidget(text_container, 1)

        # 3. BOTÓN CERRAR
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(20, 20)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        # Usamos el estilo ghost de tu theme.py
        btn_close.setStyleSheet(STYLES["btn_icon_ghost"] + f"color: {Palette.Text_Tertiary};")
        btn_close.clicked.connect(self.close_toast)
        main_layout.addWidget(btn_close, 0, Qt.AlignmentFlag.AlignTop)

    def _setup_animations(self):
        # Opacidad
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_fade.setDuration(300)
        
        # Barra de tiempo
        self.anim_bar = QPropertyAnimation(self, b"progress")
        self.anim_bar.setDuration(4000)
        self.anim_bar.setStartValue(0.0)
        self.anim_bar.setEndValue(1.0)
        self.anim_bar.finished.connect(self.close_toast)

        # Movimiento
        self.anim_pos = QPropertyAnimation(self, b"pos")
        self.anim_pos.setDuration(300)
        self.anim_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

    @pyqtProperty(float)
    def progress(self): return self._progress

    @progress.setter
    def progress(self, value): 
        self._progress = value
        self.update()

    def eventFilter(self, source, event):
        if source == self.parent_ref and event.type() in (QEvent.Type.Resize, QEvent.Type.Move):
            ToastNotification.reposition_all(animate=False)
        return super().eventFilter(source, event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8) # Radio de 8px fijo
        
        # 1. Fondo
        painter.fillPath(path, self.bg_color)
        
        # 2. Borde Sutil
        painter.setPen(QColor(Palette.Border_Light))
        painter.drawPath(path)
        
        # 3. Barra de progreso inferior
        if self._progress > 0:
            painter.setClipPath(path)
            bar_height = 3
            bar_width = self.width() * (1 - self._progress)
            
            # Dibujar barra
            rect_bar = QRectF(0, self.height() - bar_height, bar_width, bar_height)
            painter.fillPath(self._rect_to_path(rect_bar), self.accent_color)

    def _rect_to_path(self, rect):
        p = QPainterPath()
        p.addRect(rect)
        return p

    def show_toast(self):
        if len(ToastNotification._active_toasts) >= self.MAX_VISIBLE:
            oldest = ToastNotification._active_toasts.pop(0)
            oldest.close_toast_immediate()
        
        ToastNotification._active_toasts.append(self)
        self.adjustSize() 
        self.show()
        self.raise_()
        ToastNotification.reposition_all(animate=True)
        
        self.anim_fade.setStartValue(0); self.anim_fade.setEndValue(1); self.anim_fade.start()
        self.anim_bar.start()

    def close_toast(self):
        if self.anim_fade.direction() == QPropertyAnimation.Direction.Backward: return
        self.anim_fade.setDirection(QPropertyAnimation.Direction.Backward)
        self.anim_fade.finished.connect(self._cleanup)
        self.anim_fade.start()

    def close_toast_immediate(self):
        self._cleanup()

    def _cleanup(self):
        if self.parent_ref: self.parent_ref.removeEventFilter(self)
        if self in ToastNotification._active_toasts: 
            ToastNotification._active_toasts.remove(self)
        ToastNotification.reposition_all(animate=True)
        self.close()

    def move_to(self, target_pos: QPoint, animate=True):
        if animate:
            if self.anim_pos.state() == QPropertyAnimation.State.Running:
                self.anim_pos.stop()
            self.anim_pos.setEndValue(target_pos)
            self.anim_pos.start()
        else:
            self.move(target_pos)

    @staticmethod
    def reposition_all(animate=True):
        active = ToastNotification._active_toasts
        if not active: return

        first_toast = active[0]
        parent = first_toast.parent_ref
        if not parent: return
        
        # Usamos geometry global para posicionar
        parent_geo = parent.geometry()
        screen_pos = parent.mapToGlobal(QPoint(0,0))
        
        margin_bottom = 20
        margin_right = 20
        spacing = 10
        
        current_y = screen_pos.y() + parent_geo.height() - margin_bottom

        for toast in reversed(active):
            w = toast.width()
            h = toast.height()
            
            target_x = screen_pos.x() + parent_geo.width() - w - margin_right
            target_y = current_y - h
            
            toast.move_to(QPoint(target_x, target_y), animate)
            current_y = target_y - spacing
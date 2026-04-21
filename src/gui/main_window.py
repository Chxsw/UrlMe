from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QLabel, QLineEdit, QPushButton,
                             QComboBox, QFileDialog, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from utils.workers import DownloadWorker, ConvertWorker, InfoWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("UrlMe — Gestor Multimedia")
        self.resize(780, 480)
        self.setMinimumSize(700, 420)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        tabs = QTabWidget()
        tabs.addTab(self.build_download_tab(), "  Descargar  ")
        tabs.addTab(self.build_convert_tab(), "  Convertir  ")

        main_layout.addWidget(tabs)

        self.info_thread = None
        self.download_thread = None
        self.convert_thread = None
        self.selected_file = ""
        self.current_url_ready = ""

    # ------------------------------------------------------------------ #
    #  TAB: DESCARGAR                                                      #
    # ------------------------------------------------------------------ #
    def build_download_tab(self):
        tab = QWidget()
        root = QHBoxLayout(tab)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(0)

        # ── Panel izquierdo ──────────────────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(6)

        url_label = QLabel("ENLACE DEL MEDIO")
        url_label.setProperty("class", "field-label")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Pega la URL aquí…")
        self.url_input.setMinimumHeight(40)

        fmt_label = QLabel("FORMATO DE SALIDA")
        fmt_label.setProperty("class", "field-label")
        fmt_label.setContentsMargins(0, 10, 0, 0)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["Video (MP4)", "Audio (MP3)"])
        self.format_combo.setMinimumHeight(40)

        self.preview_btn = QPushButton("Buscar video")
        self.preview_btn.setMinimumHeight(40)
        self.preview_btn.clicked.connect(self.start_preview)

        self.status_label_download = QLabel("")
        self.status_label_download.setWordWrap(True)
        self.status_label_download.setProperty("class", "status-label")

        left.addWidget(url_label)
        left.addWidget(self.url_input)
        left.addWidget(fmt_label)
        left.addWidget(self.format_combo)
        left.addSpacing(8)
        left.addWidget(self.preview_btn)
        left.addStretch()
        left.addWidget(self.status_label_download)

        # ── Divisor vertical ─────────────────────────────────────────────
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setProperty("class", "v-separator")

        # ── Panel derecho ────────────────────────────────────────────────
        right = QVBoxLayout()
        right.setSpacing(10)
        right.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Contenedor del thumbnail
        self.thumb_container = QWidget()
        self.thumb_container.setFixedSize(300, 168)
        self.thumb_container.setProperty("class", "thumb-container")

        self.thumb_label = QLabel(self.thumb_container)
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setFixedSize(300, 168)
        self.thumb_label.setText("Vista previa")
        self.thumb_label.setProperty("class", "thumb-placeholder")

        # Overlay título sobre la imagen
        self.thumb_overlay = QLabel(self.thumb_container)
        self.thumb_overlay.setFixedWidth(300)
        self.thumb_overlay.setWordWrap(True)
        self.thumb_overlay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.thumb_overlay.setProperty("class", "thumb-overlay")
        self.thumb_overlay.move(0, 100)
        self.thumb_overlay.resize(300, 68)
        self.thumb_overlay.hide()

        # Badges
        badges_row = QHBoxLayout()
        badges_row.setSpacing(6)
        badges_row.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.badge_format = QLabel("MP4")
        self.badge_format.setProperty("class", "badge-format")
        self.badge_format.hide()

        self.badge_source = QLabel("YouTube")
        self.badge_source.setProperty("class", "badge-source")
        self.badge_source.hide()

        badges_row.addWidget(self.badge_format)
        badges_row.addWidget(self.badge_source)
        badges_row.addStretch()

        self.download_btn = QPushButton("Confirmar descarga")
        self.download_btn.setEnabled(False)
        self.download_btn.setProperty("class", "action-btn")
        self.download_btn.setMinimumHeight(44)
        self.download_btn.clicked.connect(self.start_download)

        right.addWidget(self.thumb_container)
        right.addLayout(badges_row)
        right.addStretch()
        right.addWidget(self.download_btn)

        # ── Ensamblar ────────────────────────────────────────────────────
        root.addLayout(left, 1)
        root.addSpacing(24)
        root.addWidget(separator)
        root.addSpacing(24)
        root.addLayout(right, 1)

        return tab

    # ------------------------------------------------------------------ #
    #  TAB: CONVERTIR                                                      #
    # ------------------------------------------------------------------ #
    def build_convert_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(48, 40, 48, 40)
        layout.setSpacing(10)

        header = QLabel("Convertir video a MP3")
        header.setProperty("class", "section-header")

        subtitle = QLabel("Selecciona un archivo MP4 local para extraer el audio.")
        subtitle.setProperty("class", "section-subtitle")
        subtitle.setWordWrap(True)

        self.select_file_btn = QPushButton("Explorar archivos…")
        self.select_file_btn.setMinimumHeight(40)
        self.select_file_btn.clicked.connect(self.choose_file)

        self.file_path_label = QLabel("Ningún archivo seleccionado")
        self.file_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_path_label.setProperty("class", "file-path-label")
        self.file_path_label.setWordWrap(True)

        self.convert_btn = QPushButton("Convertir a MP3")
        self.convert_btn.setEnabled(False)
        self.convert_btn.setProperty("class", "action-btn")
        self.convert_btn.setMinimumHeight(44)
        self.convert_btn.clicked.connect(self.start_conversion)

        self.status_label_convert = QLabel("")
        self.status_label_convert.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label_convert.setProperty("class", "status-label")
        self.status_label_convert.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(subtitle)
        layout.addSpacing(16)
        layout.addWidget(self.select_file_btn)
        layout.addWidget(self.file_path_label)
        layout.addStretch()
        layout.addWidget(self.convert_btn)
        layout.addWidget(self.status_label_convert)

        return tab

    # ------------------------------------------------------------------ #
    #  LÓGICA                                                              #
    # ------------------------------------------------------------------ #
    def start_preview(self):
        url = self.url_input.text().strip()
        if not url:
            self._set_status_download("Por favor, ingresa una URL.", "error")
            return

        self.preview_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self._set_status_download("Buscando información…", "neutral")

        self.info_thread = InfoWorker(url)
        self.info_thread.info_signal.connect(self.on_preview_finished)
        self.info_thread.start()

    def on_preview_finished(self, info, image_data, error_msg):
        self.preview_btn.setEnabled(True)

        if error_msg:
            self._set_status_download(error_msg, "error")
            self.thumb_label.clear()
            self.thumb_label.setText("Vista previa")
            self.thumb_overlay.hide()
            self.badge_format.hide()
            self.badge_source.hide()
            return

        self._set_status_download("¡Video encontrado!", "success")
        title = info.get("title", "Video sin título")
        self.current_url_ready = self.url_input.text()

        self.thumb_overlay.setText(title)
        self.thumb_overlay.show()
        self.thumb_overlay.raise_()

        fmt_text = self.format_combo.currentText()
        self.badge_format.setText("MP4" if "MP4" in fmt_text else "MP3")
        self.badge_format.show()
        self.badge_source.show()

        if image_data:
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.thumb_label.setText("")
            self.thumb_label.setPixmap(
                pixmap.scaled(
                    self.thumb_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        self.download_btn.setEnabled(True)

    def start_download(self):
        formato = self.format_combo.currentText()
        self.download_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)
        self._set_status_download("Descargando… Por favor espera.", "neutral")

        self.download_thread = DownloadWorker(self.current_url_ready, formato)
        self.download_thread.finished_signal.connect(self.on_download_finished)
        self.download_thread.start()

    def on_download_finished(self, success, message):
        self.preview_btn.setEnabled(True)
        self._set_status_download(message, "success" if success else "error")
        if success:
            self.url_input.clear()
            self.download_btn.setEnabled(False)
            self.thumb_overlay.hide()
            self.badge_format.hide()
            self.badge_source.hide()

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Video", "", "Videos MP4 (*.mp4)"
        )
        if file_path:
            import os
            self.selected_file = file_path
            self.file_path_label.setText(os.path.basename(file_path))
            self.convert_btn.setEnabled(True)
            self._set_status_convert("Archivo listo para convertir.", "success")

    def start_conversion(self):
        if not self.selected_file:
            return
        self.convert_btn.setEnabled(False)
        self.select_file_btn.setEnabled(False)
        self._set_status_convert("Convirtiendo a MP3… Por favor espera.", "neutral")

        self.convert_thread = ConvertWorker(self.selected_file)
        self.convert_thread.finished_signal.connect(self.on_convert_finished)
        self.convert_thread.start()

    def on_convert_finished(self, success, message):
        self.convert_btn.setEnabled(True)
        self.select_file_btn.setEnabled(True)
        self._set_status_convert(message, "success" if success else "error")

    # ── Helpers ──────────────────────────────────────────────────────────
    def _set_status_download(self, text, kind="neutral"):
        self.status_label_download.setText(text)
        self.status_label_download.setProperty("status", kind)
        self.status_label_download.style().unpolish(self.status_label_download)
        self.status_label_download.style().polish(self.status_label_download)

    def _set_status_convert(self, text, kind="neutral"):
        self.status_label_convert.setText(text)
        self.status_label_convert.setProperty("status", kind)
        self.status_label_convert.style().unpolish(self.status_label_convert)
        self.status_label_convert.style().polish(self.status_label_convert)
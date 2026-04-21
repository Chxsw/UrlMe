# Forma gratuita y sin anuncios para descargar videos o audios a traves de sus URLs
# - VA
# Imports
import sys
import os
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Cargar los estilos (ahora leyendo styles.css)
    css_path = os.path.join(os.path.dirname(__file__), "gui", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Aviso: No se encontró el archivo de estilos en {css_path}")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
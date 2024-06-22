import sys
import os
import configparser
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QTabWidget, QVBoxLayout, QFileDialog
from PyQt5.QtGui import QPainter, QColor, QFont
import random

class RainWidget(QWidget):
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 400
    CODE_LENGTH_RANGE = (5, 20)
    SPEED = 5  # Aumento de la velocidad de caída

    class BinaryColumn:
        def __init__(self, x):
            self.x = x
            self.y = -random.randint(0, RainWidget.SCREEN_HEIGHT)
            self.length = random.randint(*RainWidget.CODE_LENGTH_RANGE)
            self.code = ''.join(str(random.randint(0, 1)) for _ in range(self.length))
            self.font = QFont()
            self.font.setPointSize(18)

        def update(self):
            self.y += RainWidget.SPEED
            if self.y > RainWidget.SCREEN_HEIGHT:
                self.y = -self.length * 18
                self.length = random.randint(*RainWidget.CODE_LENGTH_RANGE)
                self.code = ''.join(str(random.randint(0, 1)) for _ in range(self.length))

        def draw(self, painter):
            painter.setPen(QColor(0, 255, 0))
            for i, char in enumerate(self.code):
                painter.drawText(self.x, self.y + i * 18, char)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setMinimumSize(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.columns = [self.BinaryColumn(x) for x in range(0, self.SCREEN_WIDTH, 30)]
        self.timer = self.startTimer(int(1000/30))  # 30 FPS

    def timerEvent(self, event):
        self.updateRain()

    def updateRain(self):
        for column in self.columns:
            column.update()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        for column in self.columns:
            column.draw(painter)

class MaestroWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Maestro Rlab - ¡Bienvenido!")
        self.setGeometry(100, 100, 650, 250)
        self.instalar_y_actualizar_bibliotecas()
        self.maestro_folder = self.cargar_configuracion()

        while not self.maestro_folder or not os.path.exists(self.maestro_folder):
            self.solicitar_carpeta_maestra()

        self.notebook = QTabWidget(self)
        self.root_layout = QVBoxLayout()
        self.root_layout.addWidget(self.notebook)
        self.setLayout(self.root_layout)

        self.create_buttons_tabs()


    def instalar_y_actualizar_bibliotecas(self):
        try:
            import docx
            import openpyxl
            import xlwt
            import PIL
            print("¡Las bibliotecas necesarias ya están instaladas!")
        except ImportError:
            try:
                subprocess.run(["pip", "install", "--upgrade", "python-docx", "openpyxl", "xlwt", "Pillow"], check=True)
                print("¡Las bibliotecas se han instalado y/o actualizado correctamente!")
            except subprocess.CalledProcessError as e:
                print(f"¡Error al instalar y/o actualizar las bibliotecas! {e}")

    def cargar_configuracion(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        try:
            config.read(config_path)
            maestro_folder = config.get('General', 'maestro_folder')
        except (configparser.NoSectionError, configparser.NoOptionError, FileNotFoundError):
            maestro_folder = None
        return maestro_folder

    def guardar_configuracion(self):
        config = configparser.ConfigParser()
        config['General'] = {'maestro_folder': self.maestro_folder}
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        with open(config_path, 'w') as configfile:
            config.write(configfile)

    def solicitar_carpeta_maestra(self):
        QMessageBox.information(self, "¡Hola!", "¡Bienvenido al Maestro Rlab! Por favor, selecciona la carpeta maestra.")

        # Abre un cuadro de diálogo para que el usuario seleccione la carpeta maestra
        carpeta_maestra = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta maestra", os.path.expanduser("~"))

        if not carpeta_maestra:
            # Si el usuario cancela la selección, muestra un mensaje y cierra la aplicación
            QMessageBox.critical(self, "Error", "No se ha seleccionado ninguna carpeta maestra.")
            self.close()
        else:
            # Si se selecciona una carpeta, actualiza la variable de la carpeta maestra y guarda la configuración
            self.maestro_folder = carpeta_maestra
            self.guardar_configuracion()
            self.actualizar_lista_archivos()

    def actualizar_lista_archivos(self):
        self.notebook.clear()
        self.create_buttons_tabs()

    def create_buttons_tabs(self):
        folders = next(os.walk(self.maestro_folder))[1]
        section_folders = {folder: [] for folder in folders}

        for root, dirs, files in os.walk(self.maestro_folder):
            for file in files:
                for folder in folders:
                    if folder in root:
                        if file.endswith(('.py', '.exe')):
                            section_folders[folder].append(os.path.join(root, file))

        for functionality, files in section_folders.items():
            functionality_tab = QWidget()
            functionality_layout = QVBoxLayout()
            functionality_tab.setLayout(functionality_layout)
            self.notebook.addTab(functionality_tab, functionality)

            color = QColor(71, 164, 71) 

            for file_path in files:
                script_name = os.path.basename(file_path).replace(".py", "").replace(".exe", "")
                button_text = f"{script_name}"
                button = QPushButton(button_text)
                button.clicked.connect(lambda _, s=file_path: self.execute_script(s))
                button.setStyleSheet(f"font-size: 16px; padding: 10px 20px; background-color: {color.name()}; color: white; border: none; border-radius: 5px;")
                functionality_layout.addWidget(button)

            exit_button = QPushButton("Salir")
            exit_button.clicked.connect(self.close)
            exit_button.setStyleSheet("font-size: 16px; padding: 10px 20px; background-color: #E74C3C; color: white; border: none; border-radius: 5px;")
            functionality_layout.addWidget(exit_button)

    def execute_script(self, script):
        try:
            if script.endswith('.py'):
                subprocess.Popen(['python', script])
            else:
                subprocess.Popen([script])
        except Exception as e:
            QMessageBox.critical(self, "Error de ejecución", f"No se pudo ejecutar el script: {str(e)}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maestro Rlab")
        self.setGeometry(100, 100, 600, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.maestroWidget = MaestroWidget()
        self.rainWidget = RainWidget()

        self.maestroWidget.setStyleSheet("background-color: transparent;")  

        self.layout.addWidget(self.rainWidget)
        self.layout.addWidget(self.maestroWidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

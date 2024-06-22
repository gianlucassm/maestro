import sys
import serial
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QObject

class WizA101Comunicacion(QObject):
    resultado_recibido = pyqtSignal(str)

    def __init__(self, puerto_usb):
        super().__init__()
        self._puerto_usb = puerto_usb

    def conectar(self):
        try:
            with serial.Serial(self._puerto_usb, 9600, timeout=1) as ser:
                ser.write(b'Hola, WIZ-A101!')
                respuesta = ser.readline().decode()
                self.resultado_recibido.emit(respuesta)
        except Exception as e:
            self.resultado_recibido.emit(f"Error al conectar con WIZ-A101 a través de USB: {str(e)}")

class AplicacionInmunofluorescencia(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicación de Inmunofluorescencia")
        self.setGeometry(100, 100, 600, 400)

        self._wiz_comunicacion = WizA101Comunicacion(puerto_usb='COM3')
        self._wiz_comunicacion.resultado_recibido.connect(self.mostrar_resultado)

        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout_principal = QVBoxLayout()
        self.central_widget.setLayout(self.layout_principal)

        self.boton_conectar = QPushButton("Conectar a WIZ-A101")
        self.boton_conectar.clicked.connect(self._wiz_comunicacion.conectar)
        self.layout_principal.addWidget(self.boton_conectar)

        self.frame_resultado = QWidget()
        self.layout_resultado = QVBoxLayout()
        self.frame_resultado.setLayout(self.layout_resultado)
        self.layout_principal.addWidget(self.frame_resultado)

        self.etiqueta_resultado = QLabel("Resultado de la comunicación:")
        self.layout_resultado.addWidget(self.etiqueta_resultado)

        self.texto_resultado = QTextEdit()
        self.texto_resultado.setReadOnly(True)
        self.layout_resultado.addWidget(self.texto_resultado)

    def mostrar_resultado(self, resultado):
        self.texto_resultado.setPlainText(resultado)

def main():
    app = QApplication(sys.argv)
    ventana = AplicacionInmunofluorescencia()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

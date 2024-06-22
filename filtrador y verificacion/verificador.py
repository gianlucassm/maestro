import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt

def generate_default_stylesheet():
    default_stylesheet = """
/* styles.qss */

QWidget {
    background-color: #f0f0f0;
}

QLabel {
    font-size: 24px; /* Aumentar el tamaño de la fuente */
}

QLineEdit {
    font-size: 24px; /* Aumentar el tamaño de la fuente */
}

QPushButton {
    background-color: #4CAF50; /* Green */
    border: none;
    color: white;
    padding: 12px 28px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 20px;
    margin: 6px 3px;
    cursor: pointer;
    border-radius: 10px;
}

QPushButton:hover {
    background-color: #45a049;
}
"""
    with open("styles.qss", "w") as f:
        f.write(default_stylesheet)

def calcular_digito_verificador(rut):
    rut = rut.replace('.', '').replace('-', '')
    if rut.isdigit() and len(rut) == 8:
        total = 0
        multiplo = 2
        for digito in reversed(rut):
            total += int(digito) * multiplo
            multiplo += 1
            if multiplo == 8:
                multiplo = 2
        resto = total % 11
        dv = 11 - resto
        if dv == 11:
            return '0'
        elif dv == 10:
            return 'K'
        else:
            return str(dv)
    else:
        return 'RUT inválido'

def calcular_dv():
    rut = entry_rut.text()
    digito_verificador = calcular_digito_verificador(rut)
    label_resultado.setText(f'Dígito verificador: {digito_verificador}')
    label_resultado.setStyleSheet("font-size: 24px; color: green; font-weight: bold;") # Ajustar el tamaño de la fuente del resultado

# Verificar si existe el archivo styles.qss y crearlo si no existe
if not os.path.exists("styles.qss"):
    generate_default_stylesheet()

# Crear la aplicación PyQt
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Calculadora de Dígito Verificador de RUT Chileno")
window.setGeometry(100, 100, 500, 200)

# Crear elementos de la interfaz
layout = QVBoxLayout()

label_rut = QLabel("Ingrese el RUT (sin puntos ni guión):")
label_rut.setAlignment(Qt.AlignCenter)
label_rut.setStyleSheet("font-size: 24px;") # Ajustar el tamaño de la fuente del label de entrada
layout.addWidget(label_rut)

entry_rut = QLineEdit()
entry_rut.setAlignment(Qt.AlignCenter)
entry_rut.returnPressed.connect(calcular_dv)  # Conectar la señal returnPressed al método calcular_dv
layout.addWidget(entry_rut)

button_calcular = QPushButton("Calcular Dígito Verificador")
button_calcular.clicked.connect(calcular_dv)
layout.addWidget(button_calcular)

label_resultado = QLabel("")
label_resultado.setAlignment(Qt.AlignCenter)
label_resultado.setStyleSheet("font-size: 24px; color: green; font-weight: bold;")
layout.addWidget(label_resultado)

window.setLayout(layout)

# Aplicar hoja de estilo
with open("styles.qss", "r") as f:
    app.setStyleSheet(f.read())

# Mostrar la ventana
window.show()

# Ejecutar la aplicación
sys.exit(app.exec_())

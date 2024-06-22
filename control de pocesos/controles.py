import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QInputDialog, QGridLayout
from openpyxl import Workbook
from openpyxl.styles import Alignment
from datetime import datetime
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class ControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro de Controles de Calidad")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.controles = ["TTC1", "TTC2", "TTC3", "RE1", "RE2", "RE3", "FT1", "FT2", "FT3", "OIM1", "OIM2", "OIM3", "HEPA1","HEPA2","NBNP1","NBNP2","NBNP3"]
        self.config = {"selected_controls": self.controles}

        self.create_main_ui()

    def create_main_ui(self):
        label_title = QLabel("Registro de Controles de Calidad", self)
        label_title.setFont(QFont("Arial", 18, QFont.Bold))
        self.layout.addWidget(label_title)

        grid_layout = QGridLayout()

        column_spacing = 3

        prefijos_controles = {
            "TTC": ["TTC1", "TTC2", "TTC3"],
            "RE": ["RE1", "RE2", "RE3"],
            "FT": ["FT1", "FT2", "FT3"],
            "OIM": ["OIM1", "OIM2", "OIM3"],
            "HEPA": ["HEPA1", "HEPA2"],
            "NBNP": ["NBNP1", "NBNP2", "NBNP3"]
        }

        row_offset = 0
        for prefijo, controles in prefijos_controles.items():
            label_prefijo = QLabel(prefijo, self)
            label_prefijo.setFont(QFont("Arial", 14, QFont.Bold))
            grid_layout.addWidget(label_prefijo, row_offset, 0, 1, 1)

            column_offset = 1
            for control in controles:
                label_control = QLabel(control, self)
                label_control.setAlignment(Qt.AlignCenter)
                label_control.setFont(QFont("Arial", 12))
                label_control.setStyleSheet("QLabel { background-color: #f0f0f0; border-radius: 5px; padding: 5px; color: #333; }")
                grid_layout.addWidget(label_control, row_offset, column_offset)

                determinaciones_entry = QLineEdit("0", self)
                determinaciones_entry.setFixedWidth(30)
                determinaciones_entry.setAlignment(Qt.AlignCenter)
                determinaciones_entry.setStyleSheet("QLineEdit { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 5px; padding: 5px; }")
                grid_layout.addWidget(determinaciones_entry, row_offset + 1, column_offset)

                column_offset += 1 + column_spacing

            row_offset += 2

        self.layout.addLayout(grid_layout)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Agregar", self)
        add_button.clicked.connect(self.add_control)
        add_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; border-radius: 5px; padding: 10px; }")
        button_layout.addWidget(add_button)

        remove_button = QPushButton("Quitar", self)
        remove_button.clicked.connect(self.remove_control)
        remove_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; border: none; border-radius: 5px; padding: 10px; }")
        button_layout.addWidget(remove_button)

        generate_button = QPushButton("Generar", self)
        generate_button.clicked.connect(self.generar_planilla)
        generate_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border: none; border-radius: 5px; padding: 10px; }")
        button_layout.addWidget(generate_button)

        self.layout.addLayout(button_layout)

        self.adjustSize()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def add_control(self):
        control, ok_pressed = QInputDialog.getText(self, "Agregar Control", "Ingrese el nombre del nuevo control:")
        if ok_pressed and control:
            self.config["selected_controls"].append(control)
            self.create_main_ui()

    def remove_control(self):
        control, ok_pressed = QInputDialog.getText(self, "Quitar Control", "Ingrese el nombre del control a quitar:")
        if ok_pressed and control in self.config["selected_controls"]:
            self.config["selected_controls"].remove(control)
            self.create_main_ui()
        elif ok_pressed:QMessageBox.critical(self, "Error", "El control especificado no está en la lista.")

    def generar_planilla(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Excel files (*.xlsx)")
        if file_path:
            try:
                wb = Workbook()
                ws = wb.active
                ws.append(['Fecha de Control'] + self.config["selected_controls"])

                fecha = datetime.now().strftime("%d-%m-%Y")
                controles_realizados = [entry.text() for entry in self.findChildren(QLineEdit)]
                ws.append([fecha] + controles_realizados)

                for col in ws.columns:
                    max_length = max(len(str(cell.value)) for cell in col)
                    adjusted_width = (max_length + 2) * 1.2
                    ws.column_dimensions[col[0].column_letter].width = adjusted_width
                    for cell in col:
                        cell.alignment = Alignment(horizontal='center', vertical='center')

                wb.save(file_path)
                QMessageBox.information(self, "Éxito", f"Datos guardados exitosamente en '{file_path}'")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Se produjo un error al guardar los datos: {e}")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ControlApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

           

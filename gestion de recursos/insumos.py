import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QLineEdit,
    QDialog, QMessageBox, QFileDialog, QTableWidgetItem, QTableWidget,QInputDialog
)
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
import xlsxwriter
import json
import os
import subprocess

# Función para instalar o actualizar las librerías necesarias
def instalar_actualizar_librerias():
    try:
        # Comando para instalar o actualizar las librerías
        comando = "pip install --upgrade openpyxl xlsxwriter"
        subprocess.run(comando, shell=True)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"No se pudieron instalar/actualizar las librerías: {e}")

class Insumo:
    def __init__(self, nombre, cantidad, lote, vencimiento, fecha_ingreso=None):
        self.nombre = nombre
        self.cantidad = cantidad
        self.lote = lote
        self.vencimiento = vencimiento
        self.fecha_ingreso = fecha_ingreso if fecha_ingreso else datetime.now()
        self.fecha_critico = None
        self.fecha_agotado = None

    def calcular_fechas(self, valor_critico):
        if self.cantidad <= valor_critico:
            self.fecha_critico = self.fecha_ingreso + timedelta(days=7)
        if self.cantidad == 0:
            self.fecha_agotado = datetime.now()

class Stock:
    def __init__(self):
        self.insumos = []

    def agregar_insumo(self, insumo):
        self.insumos.append(insumo)

    def cargar_stock(self, archivo):
        try:
            with open(archivo, 'r') as f:
                data = json.load(f)
                for r in data:
                    nombre = r.get('nombre', '')
                    cantidad = r.get('cantidad', 0)
                    lote = r.get('lote', '')
                    vencimiento = r.get('vencimiento', '')
                    fecha_ingreso_str = r.get('fecha_ingreso', None)
                    fecha_ingreso = None
                    if fecha_ingreso_str:
                        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"]:
                            try:
                                fecha_ingreso = datetime.strptime(fecha_ingreso_str, fmt)
                                break
                            except ValueError:
                                pass
                    insumo = Insumo(nombre, cantidad, lote, vencimiento, fecha_ingreso)
                    self.insumos.append(insumo)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error al cargar el archivo 'stock.json'.")

    def guardar_stock(self, archivo):
        try:
            with open(archivo, 'w') as f:
                json.dump([insumo.__dict__ for insumo in self.insumos], f, default=str)
        except FileNotFoundError:
            print("Error al guardar el archivo 'stock.json'.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestor de Stock de controles y calibradores")
        self.resize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.desarrollador = "GIAN LUCAS SAN MARTIN"
        self.version = "1.1"
        self.fecha_actualizacion = datetime.now().strftime("%Y-%m-%d")

        self.stock = Stock()
        self.stock_path = os.path.join(os.path.dirname(sys.argv[0]), "stockI.json")  
        self.stock.cargar_stock(self.stock_path)

        self.ventana_agregar = None  

        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout()

        info_label = QLabel(f"Desarrollador: {self.desarrollador}, Versión: {self.version}, Última Actualización: {self.fecha_actualizacion}")
        layout.addWidget(info_label)

        buttons_layout = QVBoxLayout()

        buttons = [
            ("Ver Stock", self.ver_stock),
            ("Agregar Insumo", self.abrir_ventana_agregar),
            ("Actualizar Cantidad", self.actualizar_cantidad),
            ("Eliminar Insumo", self.eliminar_insumo),
            ("Guardar Stock", self.guardar_stock),
            ("Guardar Excel", self.guardar_excel),  # Agregar botón para guardar Excel
            ("Salir", self.salir)
        ]

        for text, function in buttons:
            button = QPushButton(text)
            button.clicked.connect(function)
            buttons_layout.addWidget(button)

        layout.addLayout(buttons_layout)

        self.buscar_insumo_entry = QLineEdit()
        self.buscar_insumo_entry.setPlaceholderText("Buscar Insumo...")
        self.buscar_insumo_entry.textChanged.connect(self.buscar_insumo)
        layout.addWidget(self.buscar_insumo_entry)

        self.stock_tree = QTreeWidget()
        self.stock_tree.setColumnCount(7)
        self.stock_tree.setHeaderLabels(["Nombre", "Cantidad", "Lote", "Vencimiento", "Fecha de Ingreso", "Fecha Crítica", "Fecha de Agotado"])
        layout.addWidget(self.stock_tree)

        self.central_widget.setLayout(layout)

        # Actualizar el árbol de stock
        self.actualizar_stock()

    def ver_stock(self):
        # Actualizar el árbol de stock
        self.actualizar_stock()

    def actualizar_stock(self):
        self.stock_tree.clear()
        for insumo in self.stock.insumos:
            self.insert_insumo_to_tree(insumo)

    def insert_insumo_to_tree(self, insumo):
        item = QTreeWidgetItem(self.stock_tree)
        item.setText(0, insumo.nombre)
        item.setText(1, str(insumo.cantidad))
        item.setText(2, insumo.lote)
        item.setText(3, insumo.vencimiento)
        item.setText(4, insumo.fecha_ingreso.strftime("%Y-%m-%d %H:%M:%S"))
        item.setText(5, insumo.fecha_critico.strftime("%Y-%m-%d %H:%M:%S") if insumo.fecha_critico else "")
        item.setText(6, insumo.fecha_agotado.strftime("%Y-%m-%d %H:%M:%S") if insumo.fecha_agotado else "")

    def abrir_ventana_agregar(self):
        self.ventana_agregar = QDialog(self)
        self.ventana_agregar.setWindowTitle("Agregar Insumo")

        layout = QVBoxLayout()

        self.nombre_entry = QLineEdit()
        self.nombre_entry.setPlaceholderText("Nombre")
        layout.addWidget(self.nombre_entry)

        self.cantidad_entry = QLineEdit()
        self.cantidad_entry.setPlaceholderText("Cantidad")
        layout.addWidget(self.cantidad_entry)

        self.lote_entry = QLineEdit()
        self.lote_entry.setPlaceholderText("Lote")
        layout.addWidget(self.lote_entry)

        self.vencimiento_entry = QLineEdit()
        self.vencimiento_entry.setPlaceholderText("Vencimiento")
        layout.addWidget(self.vencimiento_entry)

        agregar_button = QPushButton("Agregar")
        agregar_button.clicked.connect(self.agregar_insumo_submit)
        layout.addWidget(agregar_button)

        self.ventana_agregar.setLayout(layout)
        self.ventana_agregar.exec_()

    def agregar_insumo_submit(self):
        nombre = self.nombre_entry.text()
        cantidad = self.cantidad_entry.text()
        lote = self.lote_entry.text()
        vencimiento = self.vencimiento_entry.text()

        if not all((nombre, cantidad, lote, vencimiento)):
            QMessageBox.critical(self, "Error", "Todos los campos son requeridos.")
            return

        try:
            cantidad = int(cantidad)
        except ValueError:
            QMessageBox.critical(self, "Error", "La cantidad debe ser un número entero.")
            return

        if cantidad <= 0:
            QMessageBox.critical(self, "Error", "La cantidad debe ser mayor que cero.")
            return

        insumo = Insumo(nombre, cantidad, lote, vencimiento)
        insumo.calcular_fechas(0)
        self.stock.agregar_insumo(insumo)
        self.stock.guardar_stock(self.stock_path)
        self.actualizar_stock()
        self.ventana_agregar.close()

    def actualizar_cantidad(self):
        seleccion = self.stock_tree.selectedItems()
        if seleccion:
            item = seleccion[0]
            for insumo in self.stock.insumos:
                if insumo.nombre == item.text(0):
                    nueva_cantidad, ok = QInputDialog.getInt(self, "Actualizar Cantidad", f"Nueva cantidad para {insumo.nombre}:")
                    if ok:
                        insumo.cantidad = nueva_cantidad
                        insumo.calcular_fechas(0)
                        self.stock.guardar_stock(self.stock_path)
                        self.actualizar_stock()

    def eliminar_insumo(self):
        seleccion = self.stock_tree.selectedItems()
        if seleccion:
            item = seleccion[0]
            nombre_insumo = item.text(0)
            for idx, insumo in enumerate(self.stock.insumos):
                if insumo.nombre == nombre_insumo:
                    self.stock.insumos.pop(idx)
                    break
            self.stock.guardar_stock(self.stock_path)
            self.actualizar_stock()

    def buscar_insumo(self):
        query = self.buscar_insumo_entry.text().lower()
        self.stock_tree.clear()
        for insumo in self.stock.insumos:
            if query in insumo.nombre.lower():
                self.insert_insumo_to_tree(insumo)

    def guardar_stock(self):
        self.stock.guardar_stock(self.stock_path)
        QMessageBox.information(self, "Guardar Stock", "Stock guardado correctamente en 'stock.json'.")

    def guardar_excel(self):
        workbook = xlsxwriter.Workbook("stock.xlsx")
        worksheet = workbook.add_worksheet()

        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        worksheet.write(0, 0, f"Fecha: {fecha_actual}")

        headers = ["Nombre", "Cantidad", "Lote", "Vencimiento", "Fecha de Ingreso", "Fecha Crítica", "Fecha de Agotado"]
        for col, header in enumerate(headers):
            worksheet.write(1, col, header)

        row = 2
        for insumo in self.stock.insumos:
            worksheet.write(row, 0, insumo.nombre)
            worksheet.write(row, 1, insumo.cantidad)
            worksheet.write(row, 2, insumo.lote)
            worksheet.write(row, 3, insumo.vencimiento)
            worksheet.write(row, 4, insumo.fecha_ingreso.strftime("%Y-%m-%d %H:%M:%S"))
            worksheet.write(row, 5, insumo.fecha_critico.strftime("%Y-%m-%d %H:%M:%S") if insumo.fecha_critico else "")
            worksheet.write(row, 6, insumo.fecha_agotado.strftime("%Y-%m-%d %H:%M:%S") if insumo.fecha_agotado else "")
            row += 1

        workbook.close()
        QMessageBox.information(self, "Guardar Excel", "Stock guardado correctamente en 'stock.xlsx'.")

    def salir(self):
        sys.exit()

def main():
    # Instalar o actualizar las librerías necesarias
    instalar_actualizar_librerias()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()



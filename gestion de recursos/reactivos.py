from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QInputDialog, QMessageBox, QTreeWidget, QTreeWidgetItem, QFrame
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
import json
import os
import sys
import xlsxwriter

class Reactivo:
    def __init__(self, nombre, cantidad, lote, vencimiento, fecha_ingreso=None):
        self.nombre = nombre
        self.cantidad = cantidad
        self.lote = lote
        self.vencimiento = vencimiento
        self.fecha_ingreso = fecha_ingreso if fecha_ingreso else datetime.now()
        self.fecha_critico = None
        self.fecha_agotado = None
        self.determinaciones_por_reactivo = 100  # Valor por defecto para otros reactivos
        if nombre.lower() == "(r señal)":  # Si el reactivo es "(R SEÑAL)"
            self.determinaciones_por_reactivo = 210  # Cambiar el número de determinaciones por reactivo

    def calcular_fechas(self, valor_critico):
        if self.cantidad <= valor_critico:
            self.fecha_critico = self.fecha_ingreso + timedelta(days=7)
        if self.cantidad == 0:
            self.fecha_agotado = datetime.now()

class StockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Stock de Reactivos de Laboratorio")
        self.stock = Stock()
        executable_path = os.path.dirname(sys.argv[0])
        self.stock_path = os.path.join(executable_path, "stockR.json")
        if not os.path.exists(self.stock_path):
            # Si el archivo no existe, crea uno vacío
            with open(self.stock_path, 'w') as f:
                json.dump([], f)

        self.stock.cargar_stock(self.stock_path)

        self.ventana_agregar = None  # Variable para la ventana de agregar reactivo

        self.create_widgets()

    def create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        label = QLabel("Seleccione una opción:")
        layout.addWidget(label)

        buttons_layout = QVBoxLayout()  # Layout para los botones
        buttons_layout.setSpacing(10)  # Espacio entre los botones
        buttons = [
            ("Ver Stock", self.ver_stock),
            ("Agregar Reactivo", self.agregar_reactivo),
            ("Actualizar Cantidad", self.actualizar_cantidad),
            ("Eliminar Reactivo", self.eliminar_reactivo),
            ("Guardar Stock", self.guardar_stock),
            ("Generar Listado Excel", self.generar_listado_excel),
            ("Salir", self.salir)
        ]

        for text, callback in buttons:
            button = QPushButton(text)
            button.clicked.connect(callback)
            button.setFixedSize(150, 30)  # Tamaño fijo para los botones
            buttons_layout.addWidget(button)

        buttons_frame = QFrame()  # Frame para los botones
        buttons_frame.setLayout(buttons_layout)
        layout.addWidget(buttons_frame)

        self.buscar_reactivo_entry = QLineEdit()
        self.buscar_reactivo_entry.setPlaceholderText("Buscar reactivo...")
        self.buscar_reactivo_entry.textChanged.connect(self.buscar_reactivo)
        layout.addWidget(self.buscar_reactivo_entry)

        self.stock_frame = QFrame()  # Frame para la visualización del stock
        stock_layout = QVBoxLayout()
        self.stock_tree = QTreeWidget()
        headers = ["Nombre", "Cantidad", "Lote", "Vencimiento", "Fecha de Ingreso", "Fecha Crítica", "Fecha de Agotado", "Determinaciones Totales"]
        self.stock_tree.setHeaderLabels(headers)
        stock_layout.addWidget(self.stock_tree)
        self.stock_frame.setLayout(stock_layout)
        layout.addWidget(self.stock_frame)

        central_widget.setLayout(layout)

        self.actualizar_stock()

    def ver_stock(self):
        self.actualizar_stock()

    def actualizar_stock(self):
        self.stock_tree.clear()
        for reactivo in self.stock.reactivos:
            self.insert_reactivo_to_tree(reactivo)

    def insert_reactivo_to_tree(self, reactivo):
        cantidad = str(reactivo.cantidad)
        determinaciones_totales = str(reactivo.cantidad * reactivo.determinaciones_por_reactivo)
        fecha_ingreso = reactivo.fecha_ingreso.strftime("%Y-%m-%d %H:%M:%S")
        fecha_critico = reactivo.fecha_critico.strftime("%Y-%m-%d %H:%M:%S") if reactivo.fecha_critico else ""
        fecha_agotado = reactivo.fecha_agotado.strftime("%Y-%m-%d %H:%M:%S") if reactivo.fecha_agotado else ""
        item = QTreeWidgetItem([reactivo.nombre, cantidad, reactivo.lote, reactivo.vencimiento, fecha_ingreso, fecha_critico, fecha_agotado, determinaciones_totales])
        if reactivo.cantidad <= 1:
            item.setForeground(0, Qt.red)  # Establecer el color rojo para cantidades críticas
        self.stock_tree.addTopLevelItem(item)

    def agregar_reactivo(self):
        self.ventana_agregar = QWidget()  # Ventana modal para agregar reactivo
        self.ventana_agregar.setWindowTitle("Agregar Reactivo")
        layout = QVBoxLayout()

        nombre_label = QLabel("Nombre:")
        layout.addWidget(nombre_label)
        self.nombre_entry = QLineEdit()
        layout.addWidget(self.nombre_entry)

        cantidad_label = QLabel("Cantidad:")
        layout.addWidget(cantidad_label)
        self.cantidad_entry = QLineEdit()
        layout.addWidget(self.cantidad_entry)

        lote_label = QLabel("Lote:")
        layout.addWidget(lote_label)
        self.lote_entry = QLineEdit()
        layout.addWidget(self.lote_entry)

        vencimiento_label = QLabel("Vencimiento:")
        layout.addWidget(vencimiento_label)
        self.vencimiento_entry = QLineEdit()
        layout.addWidget(self.vencimiento_entry)

        agregar_button = QPushButton("Agregar")
        agregar_button.clicked.connect(self.agregar_reactivo_submit)
        layout.addWidget(agregar_button)

        self.ventana_agregar.setLayout(layout)
        self.ventana_agregar.exec_()

    def agregar_reactivo_submit(self):
        nombre = self.nombre_entry.text()
        cantidad = self.cantidad_entry.text()
        lote = self.lote_entry.text()
        vencimiento = self.vencimiento_entry.text()

        if not all((nombre, cantidad, lote, vencimiento)):
            QMessageBox.warning(self.ventana_agregar, "Error", "Todos los campos son requeridos.")
            return

        try:
            cantidad = int(cantidad)
        except ValueError:
            QMessageBox.warning(self.ventana_agregar, "Error", "La cantidad debe ser un número entero.")
            return

        if cantidad <= 0:
            QMessageBox.warning(self.ventana_agregar, "Error", "La cantidad debe ser mayor que cero.")
            return

        determinaciones_por_reactivo = 100  # Valor por defecto para otros reactivos
        if nombre.lower() == "(r señal)":
            determinaciones_por_reactivo = 210 # Cambiar el número de determinaciones por reactivo si es "(R SEÑAL)"

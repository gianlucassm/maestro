import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from openpyxl import Workbook
from datetime import datetime
import threading
import subprocess
import time

class RegistroMuestrasApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Registro de Muestras Repetidas")

        # Configuración de estilos
        style = ttk.Style()
        style.configure("TFrame", background="#E1D8B2")
        style.configure("TLabel", background="#E1D8B2")
        style.configure("TButton", background="#B4CCB9")
        style.configure("TEntry", fieldbackground="#F3EFEF")

        self.frame = ttk.Frame(self.master, padding="20", style="TFrame")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.label_nombre_paciente = ttk.Label(self.frame, text="Nombre del Paciente:", style="TLabel")
        self.label_nombre_paciente.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)

        self.entry_nombre_paciente = ttk.Entry(self.frame)
        self.entry_nombre_paciente.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        self.label_numero_muestra = ttk.Label(self.frame, text="Número de Muestra:", style="TLabel")
        self.label_numero_muestra.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)

        self.entry_numero_muestra = ttk.Entry(self.frame)
        self.entry_numero_muestra.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        self.label_examenes_repetidos = ttk.Label(self.frame, text="Exámenes Repetidos (separados por /):", style="TLabel")
        self.label_examenes_repetidos.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)

        self.entry_examenes_repetidos = ttk.Entry(self.frame)
        self.entry_examenes_repetidos.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        self.btn_registrar = ttk.Button(self.frame, text="Registrar Muestra", command=self.registrar_muestra, style="TButton")
        self.btn_registrar.grid(row=3, column=0, columnspan=2, pady=10)

        self.btn_exportar_excel = ttk.Button(self.frame, text="Exportar a Excel", command=self.exportar_a_excel, style="TButton")
        self.btn_exportar_excel.grid(row=4, column=0, columnspan=2, pady=10)

        # Etiqueta para mostrar el contador de muestras registradas
        self.label_contador = ttk.Label(self.frame, text="Muestras registradas: 0", style="TLabel")
        self.label_contador.grid(row=5, column=0, columnspan=2, pady=5)

        # Inicializar el contador
        self.contador_muestras = 0

        # Cargar datos del archivo JSON y actualizar el contador al iniciar la aplicación
        self.update_counter_from_json()

        # Iniciar el proceso de actualización periódica de openpyxl y recuento de muestras
        self.start_background_tasks()

    def actualizar_contador(self, increment=1):
        # Actualizar y mostrar el contador de muestras registradas
        self.contador_muestras += increment
        self.label_contador.config(text=f"Muestras registradas: {self.contador_muestras}")

    def limpiar_formulario(self):
        # Limpiar los campos de entrada del formulario
        self.entry_nombre_paciente.delete(0, tk.END)
        self.entry_numero_muestra.delete(0, tk.END)
        self.entry_examenes_repetidos.delete(0, tk.END)

    def registrar_muestra(self):
        nombre_paciente = self.entry_nombre_paciente.get()
        numero_muestra = self.entry_numero_muestra.get()
        examenes_repetidos = self.entry_examenes_repetidos.get().split("/") if self.entry_examenes_repetidos.get() else []

        if nombre_paciente and numero_muestra and examenes_repetidos:
            # Crear un nuevo registro con la fecha y hora actual
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            registro = {
                "nombre_paciente": nombre_paciente,
                "numero_muestra": numero_muestra,
                "examenes_repetidos": "/".join(examenes_repetidos),
                "fecha": fecha_actual
            }

            # Intentar cargar los datos existentes desde el archivo JSON
            try:
                with open("registros.json", "r") as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = []

            # Agregar el nuevo registro a los datos existentes
            data.append(registro)

            # Guardar los datos actualizados en el archivo JSON
            with open("registros.json", "w") as f:
                json.dump(data, f, indent=2)

            # Actualizar y mostrar el contador de muestras registradas
            self.actualizar_contador()

            messagebox.showinfo("Registro Exitoso", f"Se ha registrado la muestra '{numero_muestra}' para {nombre_paciente}.")

            # Limpiar el formulario
            self.limpiar_formulario()
        else:
            messagebox.showerror("Error", "Por favor, completa todos los campos.")

    def exportar_a_excel(self):
        # Cargar datos desde el archivo JSON
        try:
            with open("registros.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "No hay datos para exportar.")
            return

        # Crear un nuevo libro de trabajo y obtener la hoja activa
        workbook = Workbook()
        sheet = workbook.active

        # Escribir el encabezado de los datos
        sheet.append(["Fecha", "Número de Muestra", "Nombre del Paciente", "Exámenes Repetidos"])

        # Escribir la información desde la línea 2 en adelante
        for row in data:
            sheet.append([
                row['fecha'],
                row['numero_muestra'],
                row['nombre_paciente'],
                row['examenes_repetidos']
            ])

        # Abrir un cuadro de diálogo para seleccionar la ubicación del archivo Excel
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

        if file_path:
            # Guardar el libro de trabajo en el archivo Excel
            workbook.save(file_path)
            messagebox.showinfo("Exportación Exitosa", f"Los datos se han exportado correctamente a {file_path}")

            # Reiniciar los registros (sin eliminar el archivo)
            with open("registros.json", "w") as f:
                json.dump([], f)

            # Reiniciar el contador
            self.contador_muestras = 0
            self.label_contador.config(text="Muestras registradas: 0")

            # Limpiar el formulario después de exportar
            self.limpiar_formulario()

    def update_counter_from_json(self):
        try:
            with open("registros.json", "r") as f:
                data = json.load(f)
                self.contador_muestras = len(data)
                self.label_contador.config(text=f"Muestras registradas: {self.contador_muestras}")
        except FileNotFoundError:
            pass

    def start_background_tasks(self):
        # Hilo secundario para la actualización periódica de openpyxl y recuento de muestras
        def background_tasks():
            while True:
                time.sleep(3600)  # Espera 1 hora
                # Actualizar openpyxl
                subprocess.run(["pip", "install", "--upgrade", "openpyxl"])

                # Actualizar el contador desde el archivo JSON
                self.update_counter_from_json()

        # Iniciar el hilo secundario
        background_thread = threading.Thread(target=background_tasks)
        background_thread.daemon = True
        background_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroMuestrasApp(root)
    root.mainloop()

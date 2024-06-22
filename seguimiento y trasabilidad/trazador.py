import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import pickle
from PIL import Image, ImageGrab

class GridCanvas(tk.Canvas):
    def __init__(self, master, gradilla, app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.gradilla = gradilla
        self.app = app
        self.cell_size = 40
        self.circle_radius = 12
        self.font_size = 6
        self.selected_item = None
        self.draw_grid()
        self.bind("<Button-1>", self.on_click)

    def draw_grid(self):
        for i in range(9, -1, -1):
            for j in range(10):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                self.create_rectangle(x0, y0, x1, y1, outline="black", width=1)
                center_x = (x0 + x1) / 2
                center_y = (y0 + y1) / 2
                self.create_oval(center_x - self.circle_radius, center_y - self.circle_radius,
                                 center_x + self.circle_radius, center_y + self.circle_radius, outline="black",
                                 fill="white")

    def update_grid(self):
        self.delete("muestra")
        for i in range(9, -1, -1):
            for j in range(10):
                if self.gradilla.grid[i][j] != '':
                    x0 = j * self.cell_size
                    y0 = i * self.cell_size
                    x1 = x0 + self.cell_size
                    y1 = y0 + self.cell_size
                    center_x = (x0 + x1) / 2
                    center_y = (y0 + y1) / 2
                    id = self.gradilla.grid[i][j]
                    fill_color = "#f0f0f0"  # Color ligeramente más claro para el fondo de cuadricula ocupada
                    outline_color = "black"
                    for suffix, color in self.gradilla.suffix_to_color.items():
                        if id.endswith(suffix):
                            circle_fill_color = color
                            break
                    else:
                        circle_fill_color = "yellow"  # Color predeterminado si no se encuentra un sufijo coincidente
                    if (j, i) == self.selected_item:
                        fill_color = "red"  # Cambia el color a rojo si la muestra está seleccionada
                        outline_color = "red"
                    self.create_rectangle(x0, y0, x1, y1, outline=outline_color, width=1, fill=fill_color)
                    self.create_oval(center_x - self.circle_radius, center_y - self.circle_radius,
                                     center_x + self.circle_radius, center_y + self.circle_radius,
                                     outline="black", fill=circle_fill_color, tags="muestra")
                    self.create_text(center_x, center_y + self.circle_radius + 5, text=id, fill="black", tags="muestra", font=("Arial", self.font_size, "bold"))

    def on_click(self, event):
        x, y = event.x, event.y
        col = x // self.cell_size
        row = y // self.cell_size
        if 0 <= col < 10 and 0 <= row < 10:
            self.selected_item = (col, row)
            self.update_grid()
            self.app.enable_editing_buttons()
        else:
            self.selected_item = None
            self.app.disable_editing_buttons()

    def delete_selected_muestra(self):
        if self.selected_item:
            col, row = self.selected_item
            id = self.gradilla.grid[row][col]
            self.gradilla.eliminar_muestra(id)
            self.update_grid()
            self.app.disable_editing_buttons()
            self.app.clear_entry()


class GradillaApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Trasabilidad de Muestras en Gradilla")

        # Configura la ventana para que sea autoajustable
        self.master.geometry("")

        self.frame = tk.Frame(master)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.gradilla = Gradilla()
        self.grid_frame = tk.Frame(self.frame, bd=2, relief=tk.GROOVE)
        self.grid_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.grid_canvas = GridCanvas(self.grid_frame, self.gradilla, self, width=400, height=400)
        self.grid_canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.label = tk.Label(self.button_frame, text="Ingrese el código de la muestra (4 dígitos).(2 dígitos):")
        self.label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        self.entry = tk.Entry(self.button_frame, width=10)
        self.entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.entry.bind("<Return>", lambda event: self.colocar_muestra())

        self.colocar_button = tk.Button(self.button_frame, text="Colocar Muestra", command=self.colocar_muestra, width=20)
        self.colocar_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.edit_button = tk.Button(self.button_frame, text="Editar", command=self.editar, width=10)
        self.edit_button.grid(row=3, column=0, padx=5, pady=5)

        self.delete_button = tk.Button(self.button_frame, text="Borrar Seleccionada", command=self.borrar_seleccionada, width=20)
        self.delete_button.grid(row=3, column=1, padx=5, pady=5)

        self.save_button = tk.Button(self.button_frame, text="Guardar Gradilla", command=self.guardar_gradilla, width=20)
        self.save_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.search_button = tk.Button(self.button_frame, text="Buscar Muestra", command=self.buscar_muestra, width=20)
        self.search_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        self.clear_entry() 

    def enable_editing_buttons(self):
        self.edit_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)

    def disable_editing_buttons(self):
        self.edit_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)

    def colocar_muestra(self):
        muestra = self.entry.get()
        if not self.validar_muestra(muestra):
            tk.messagebox.showerror("Error", "El código de la muestra debe tener el formato 4 números seguidos de un punto y luego 2 números.")
            return

        posicion = self.gradilla.obtener_proxima_posicion()
        if posicion is None:
            tk.messagebox.showerror("Error", "No hay más espacio en la gradilla.")
            return

        fila, columna = posicion
        if self.gradilla.colocar_muestra(muestra, fila, columna):
            self.grid_canvas.update_grid()
            self.clear_entry()  
        else:
            tk.messagebox.showerror("Error", "La posición ya está ocupada.")

    def editar(self):
        muestra_id = self.grid_canvas.itemcget(self.grid_canvas.selected_item, "text")
        new_id = simpledialog.askstring("Editar Muestra", f"Ingrese el nuevo código para la muestra '{muestra_id}':")
        if new_id is not None and self.validar_muestra(new_id):
            col, row = self.grid_canvas.selected_item
            self.gradilla.editar_muestra(muestra_id, new_id, row, col)
            self.grid_canvas.update_grid()
            self.clear_entry()  
            self.grid_canvas.selected_item = (col, row)  

    def borrar_seleccionada(self):
        self.grid_canvas.delete_selected_muestra()
        self.clear_entry()  

    def guardar_gradilla(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl"), ("All Files", "*.*")])
        if filename:
            # Guardar la imagen de la gradilla como JPG
            image = ImageGrab.grab(bbox=(self.grid_frame.winfo_rootx(), self.grid_frame.winfo_rooty(), 
                                          self.grid_frame.winfo_rootx() + self.grid_frame.winfo_width(), 
                                          self.grid_frame.winfo_rooty() + self.grid_frame.winfo_height()))
            image = image.resize((800,900))  # Ajustar la resolución
            image.save(os.path.splitext(filename)[0] + ".jpg", "JPEG")

            # Guardar la gradilla como un archivo pickle
            with open(filename, "wb") as f:
                pickle.dump(self.gradilla, f)
            messagebox.showinfo("Éxito", "Gradilla guardada correctamente.")

    def buscar_muestra(self):
        muestra = simpledialog.askstring("Buscar Muestra", "Ingrese el código de la muestra a buscar:")
        if muestra:
            found = False
            for filename in os.listdir('C:/Users/Windows/Desktop/dist/master/trasabilidad'):
                if filename.endswith(".pkl"):
                    with open(os.path.join('C:/Users/Windows/Desktop/dist/master/trasabilidad', filename), "rb") as f:
                        gradilla = pickle.load(f)
                        for i in range(10):
                            for j in range(10):
                                if gradilla.grid[i][j] == muestra:
                                    self.mostrar_gradilla(gradilla, (j, i))
                                    found = True
                                    break
                            if found:
                                break
                if found:
                    break
            if not found:
                messagebox.showinfo("Resultado", f"Muestra no encontrada en ninguna gradilla.")

    def mostrar_gradilla(self, gradilla, muestra_pos):
        top = tk.Toplevel()
        top.title("Gradilla")
        canvas = tk.Canvas(top, width=400, height=400)
        canvas.pack()
        for i in range(9, -1, -1):
            for j in range(10):
                x0 = j * 40
                y0 = i * 40
                x1 = x0 + 40
                y1 = y0 + 40
                canvas.create_rectangle(x0, y0, x1, y1, outline="black", width=1)
                center_x = (x0 + x1) / 2
                center_y = (y0 + y1) / 2
                if gradilla.grid[i][j] != '':
                    fill_color = "#f0f0f0"  # Color ligeramente más claro para el fondo de cuadricula ocupada
                    if (j, i) == muestra_pos:
                        fill_color = "red"  # Cambio el color a rojo solo para la muestra buscada
                    canvas.create_oval(center_x - 12, center_y - 12, center_x + 12, center_y + 12, outline="black", fill=fill_color)
                    canvas.create_text(center_x, center_y, text=gradilla.grid[i][j], fill="black", font=("Arial", 7, "bold"))

    def validar_muestra(self, muestra):
        parts = muestra.split(".")
        if len(parts) != 2:
            return False
        if not parts[0].isdigit() or not parts[1].isdigit():
            return False
        if len(parts[0]) != 4 or len(parts[1]) != 2:
            return False
        return True

    def clear_entry(self):
        self.entry.delete(0, tk.END)


class Gradilla:
    def __init__(self):
        self.grid = [['' for _ in range(10)] for _ in range(10)]
        self.next_position = (9, 0)
        self.suffix_to_color = {
            ".13": "gray",
            ".14": "yellow",
            ".01": "yellow",
            ".02": "purple",
            ".03": "lightblue",
            ".25": "purple",
            ".28": "gray",
            ".38": "yellow",
            ".51": "yellow"
        }

    def colocar_muestra(self, muestra, fila, columna):
        if fila < 0 or fila >= 10 or columna < 0 or columna >= 10:
            return False
        if self.grid[fila][columna] != '':
            return False
        self.grid[fila][columna] = muestra
        return True

    def obtener_proxima_posicion(self):
        fila, columna = self.next_position
        while self.grid[fila][columna] != '':
            columna += 1
            if columna > 9:
                columna = 0
                fila -= 1
            if fila < 0:
                return None
        self.next_position = (fila, columna)
        return fila, columna

    def eliminar_muestra(self, muestra_id):
        for i in range(10):
            for j in range(10):
                if self.grid[i][j] == muestra_id:
                    self.grid[i][j] = ''
                    self.next_position = (i, j)
                    return

    def editar_muestra(self, old_id, new_id, row, col):
        self.grid[row][col] = new_id

        # Asignar color basado en el sufijo
        for suffix, color in self.suffix_to_color.items():
            if new_id.endswith(suffix):
                # No se puede acceder a grid_canvas desde esta función
                # Se debe manejar el cambio de color en la interfaz de usuario
                break


def main():
    root = tk.Tk()
    app = GradillaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

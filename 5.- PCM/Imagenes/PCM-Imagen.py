import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np

class ImageApp:
    def __init__(self, master):
        self.master = master
        master.title("Visor de Imágenes")

        # Cambiar el color de fondo del marco principal
        master.configure(bg='#7D3711')  # Color "Brown"

        # Crear un marco para los controles y cambiar su color de fondo
        self.controls_frame = tk.Frame(master, bg='#8A5C24')  # Color "Brown"
        self.controls_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        # Crear un marco para la imagen y cambiar su color de fondo
        self.image_frame = tk.Frame(master, bg='#FFFFFF')  # Color "White"
        self.image_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Ruta de la imagen
        self.image_path = "Imagen.jpg"
        # Cargar la imagen original
        self.original_image = Image.open(self.image_path)

        # Redimensionar la imagen para que sea más pequeña y conservar una copia de la original
        self.resized_image = self.original_image.resize((800, 550))
        self.original_resized_image = self.resized_image.copy()

        # Convertir la imagen a un formato que Tkinter pueda mostrar
        self.photo = ImageTk.PhotoImage(self.resized_image)

        # Crear un widget de etiqueta para mostrar la imagen
        self.label = tk.Label(self.image_frame, image=self.photo)
        self.label.pack()

        # Crear una etiqueta en la parte superior del marco de controles
        self.label2 = tk.Label(self.controls_frame, text="Tipo de imagen", bg='#8A5C24', font=('Cascadia Code ExtraLight', 24))
        self.label2.pack(side=tk.TOP, anchor='nw', pady=5)

        # Crear un botón para convertir a color
        self.btn_color = tk.Button(self.controls_frame, text="A color (3 Matrices de 255 niveles)", command=self.show_original_image)
        self.btn_color.pack(side=tk.TOP, padx=5, pady=5)

        # Crear un botón para convertir a escala de grises
        self.btn_grayscale = tk.Button(self.controls_frame, text="Escala de grises (Matriz de 255 niveles)", command=self.convert_to_grayscale)
        self.btn_grayscale.pack(side=tk.TOP, padx=5, pady=5)

        # Crear un botón para convertir a blanco y negro
        self.btn_black_white = tk.Button(self.controls_frame, text="Blanco y negro (Matriz de 2 niveles)", command=self.convert_to_black_white)
        self.btn_black_white.pack(side=tk.TOP, padx=5, pady=5)

        # Crear una etiqueta para la recuantización
        self.label3 = tk.Label(self.controls_frame, text="Recuantización", bg='#8A5C24', font=('Cascadia Code ExtraLight', 24))
        self.label3.pack(side=tk.TOP, anchor='nw', pady=5)

        # Interfaz de la cuantizacion
        self.cuantizacionGUI = tk.Frame(self.controls_frame, bg='#8A5C24')
        self.cuantizacionGUI.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        self.label1 = tk.Label(self.cuantizacionGUI, text="Cantidad bits/muestra:", bg='#8A5C24', font=('Arial', 12))
        self.label1.pack(side=tk.LEFT)

        self.combox = ttk.Combobox(self.cuantizacionGUI)
        self.combox['values'] = ("1", "2", "4", "8")  # Lista de opciones
        self.combox.current(0)  # Establecer la opción predeterminada
        self.combox.pack(side=tk.LEFT, pady=10)
        self.combox.bind("<<ComboboxSelected>>", self.quantize_image)  # Manejar la selección

    def quantize_image(self, event=None):
        bits = int(self.combox.get())
        if bits:
            if hasattr(self, 'gray_image'):  # Si la imagen está en escala de grises
                quantized_image = self.quantize(np.array(self.gray_image), bits)
            elif hasattr(self, 'black_white_image'):  # Si la imagen está en blanco y negro
                quantized_image = self.quantize(np.array(self.black_white_image), bits)
            else:  # Si la imagen está en color
                quantized_image = self.quantize(np.array(self.original_resized_image), bits)

            # Redimensionar la imagen cuantizada a las dimensiones originales
            quantized_image_pil = Image.fromarray(quantized_image).resize((800, 550))
            
            # Guardar la imagen recuantizada como archivo de imagen
            save_filename = f"recuantized_image_{bits}bits.jpg"
            quantized_image_pil.save(save_filename)

            # Guardar el código PCM en un archivo de texto
            txt_filename = f"recuantized_image_{bits}bits.txt"
            np.savetxt(txt_filename, quantized_image.flatten(), fmt='%d')

            # Mostrar la imagen recuantizada
            self.photo = ImageTk.PhotoImage(quantized_image_pil)
            self.label.config(image=self.photo)

    def quantize(self, image_data, bits):
        levels = 2 ** bits
        max_val = np.max(image_data)
        quantized = np.floor((image_data.astype(float) / max_val) * levels) * (max_val / levels)
        return quantized.astype(np.uint8)

    def convert_to_grayscale(self):
        # Convertir la imagen a escala de grises
        self.gray_image = self.original_image.convert("L")
        self.resized_image = self.gray_image.resize((800, 550))

        # Convertir la imagen a un formato que Tkinter pueda mostrar
        self.photo = ImageTk.PhotoImage(self.resized_image)
        self.label.config(image=self.photo)

        # Eliminar la imagen en blanco y negro si existe
        if hasattr(self, 'black_white_image'):
            delattr(self, 'black_white_image')

    def convert_to_black_white(self):
        # Convertir la imagen a blanco y negro
        self.black_white_image = self.original_image.convert("1")
        self.resized_image = self.black_white_image.resize((800, 550))

        # Convertir la imagen a un formato que Tkinter pueda mostrar
        self.photo = ImageTk.PhotoImage(self.resized_image)
        self.label.config(image=self.photo)

        # Eliminar la imagen en escala de grises si existe
        if hasattr(self, 'gray_image'):
            delattr(self, 'gray_image')

    def show_original_image(self):
        # Mostrar la imagen original a color
        self.resized_image = self.original_resized_image.copy()
        self.photo = ImageTk.PhotoImage(self.resized_image)
        self.label.config(image=self.photo)

        # Eliminar la imagen en escala de grises si existe
        if hasattr(self, 'gray_image'):
            delattr(self, 'gray_image')

        # Eliminar la imagen en blanco y negro si existe
        if hasattr(self, 'black_white_image'):
            delattr(self, 'black_white_image')

root = tk.Tk()
app = ImageApp(root)
root.mainloop()

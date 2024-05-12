import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import numpy as np

class ImageApp:
    def __init__(self, master):
        self.master = master
        master.title("Visor de Imágenes")
        # Ruta de la imagen
        self.image_path = "Imagen.jpg"
        # Cargar la imagen original
        self.original_image = Image.open(self.image_path)
        
        master.configure(bg='blue')

        # Redimensionar la imagen para que sea más pequeña y conservar una copia de la original
        self.resized_image = self.original_image.resize((800, 550))
        self.original_resized_image = self.resized_image.copy()

        # Convertir la imagen a un formato que Tkinter pueda mostrar
        self.photo = ImageTk.PhotoImage(self.resized_image)

        # Crear un widget de etiqueta para mostrar la imagen
        self.label = tk.Label(master, image=self.photo)
        self.label.pack()

        # Crear un botón para recuantizar
        self.btn_quantize = tk.Button(master, text="Recuantizar", command=self.quantize_image)
        self.btn_quantize.pack(side=tk.LEFT, padx=5, pady=5)

        # Crear un botón para convertir a escala de grises
        self.btn_grayscale = tk.Button(master, text="Matriz de 255", command=self.convert_to_grayscale)
        self.btn_grayscale.pack(side=tk.LEFT, padx=5, pady=5)

        # Crear un botón para convertir a blanco y negro
        self.btn_black_white = tk.Button(master, text="Matriz de 2", command=self.convert_to_black_white)
        self.btn_black_white.pack(side=tk.LEFT, padx=5, pady=5)

        # Crear un botón para volver a la imagen original a color
        self.btn_color = tk.Button(master, text="3 Matrices", command=self.show_original_image)
        self.btn_color.pack(side=tk.LEFT, padx=5, pady=5)

    def quantize_image(self):
        bits = simpledialog.askinteger("Recuantización", "Cuantos niveles de cuantizacion?:\n1 bit de codigo PCM\n2 bits de codigo PCM\n4 bits de codigo PCM\n8 bits de codigo PCM",
                                       minvalue=1, maxvalue=8)
        if bits:
            if hasattr(self, 'gray_image'):  # Si la imagen está en escala de grises
                quantized_image = self.quantize(np.array(self.gray_image), bits)
            elif hasattr(self, 'black_white_image'):  # Si la imagen está en blanco y negro
                quantized_image = self.quantize(np.array(self.black_white_image), bits)
            else:  # Si la imagen está en color
                quantized_image = self.quantize(np.array(self.original_resized_image), bits)

            # Guardar la imagen recuantizada como archivo de imagen
            save_filename = f"recuantized_image_{bits}bits.jpg"
            Image.fromarray(quantized_image).save(save_filename)

            # Guardar el código PCM en un archivo de texto
            txt_filename = f"recuantized_image_{bits}bits.txt"
            np.savetxt(txt_filename, quantized_image.flatten(), fmt='%d')

            # Mostrar la imagen recuantizada
            self.photo = ImageTk.PhotoImage(Image.fromarray(quantized_image))
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

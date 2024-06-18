import tkinter as tk
from tkinter import filedialog, Menu, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import os

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        
        self.canvas = tk.Canvas(root, width=500, height=500)
        self.canvas.pack()

        self.menu = Menu(root)
        self.root.config(menu=self.menu)

        self.file_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_file)

        self.modulation_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Modulation", menu=self.modulation_menu)
        self.modulation_menu.add_command(label="ASK", command=lambda: self.set_modulation("ASK"))
        self.modulation_menu.add_command(label="8PSK", command=lambda: self.set_modulation("8PSK"))
        self.modulation_menu.add_command(label="16QAM", command=lambda: self.set_modulation("16QAM"))

        self.bits_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Bits", menu=self.bits_menu)
        for bits in range(0, 4):
            self.bits_menu.add_command(label=f"{2**bits} bits", command=lambda b=bits: self.set_bits(b))

        self.file_path = None
        self.file_type = None
        self.modulation = None
        self.bits = None

    def open_file(self):
        file_type = simpledialog.askstring("Select File Type", "Introduce 'I' para imagen o 'A' para audio")
        if file_type not in ['I', 'A']:
            messagebox.showerror("Invalid Input", "Introduzca un caracter valido")
            return
        self.file_type = file_type
        if file_type == 'I':
            self.file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
            if self.file_path:
                self.display_image()
        elif file_type == 'A':
            self.file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav")])
            if self.file_path:
                self.display_audio()

    def display_image(self):
        image = Image.open(self.file_path)
        image = ImageOps.grayscale(image)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image = image.resize((canvas_width, canvas_height), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(250, 250, image=self.photo)
        self.image = np.array(image)

    def display_audio(self):
        rate, data = wavfile.read(self.file_path)
        plt.figure(figsize=(10, 4))
        plt.plot(data)
        plt.title('Audio Signal')
        plt.xlabel('Sample')
        plt.ylabel('Amplitude')
        plt.show()
        self.audio = data

    def set_modulation(self, modulation_type):
        self.modulation = modulation_type
        self.modulation_process()
        
    def set_bits(self, bits):
        self.bits = bits
        self.modulation_process()

    def plot_binary_signal(self, image_array):
        # Asegúrate de que el arreglo sea 1D para obtener los primeros 10 valores
        flattened_image = image_array.flatten()
        print(flattened_image)
        
        # Obtener los primeros 10 valores
        first_10_values = flattened_image[:10]
        print(first_10_values)
        
        # Convertir a binario
        binary_values = [np.binary_repr(value, width=8) for value in first_10_values]
        print(binary_values)
        
        # Convertir binarios a listas de bits
        bit_sequences = [[int(bit) for bit in binary_value] for binary_value in binary_values]
        print(bit_sequences)
        
        # Aplanar la lista de listas de bits para la gráfica
        bit_sequence_flat = [bit for sequence in bit_sequences for bit in sequence]
        print(bit_sequence_flat)
        
        # Calcular el intervalo de tiempo para cada bit
        longitud_bits_por_segundo = len(bit_sequence_flat)
        
        # Crear los valores de tiempo para el eje X
        x_values = np.linspace(0, 1, longitud_bits_por_segundo, endpoint=False)
        y_values = bit_sequence_flat


        # Parámetros de la señal cosenoidal
        amplitude = 1.0  # Voltios
        frequency = 25000000  # 1 MHz
        # Necesitamos muchos más puntos para representar adecuadamente una señal de 1 MHz
        x_dense = np.linspace(0, 1, 1000)
        cosine_signal = amplitude * np.cos(2 * np.pi * frequency * x_dense)

        

        # Crear una figura con 3 subplots (en una columna)
        fig, axs = plt.subplots(3, 1, figsize=(10, 6))

        # Primera gráfica: Señal digital original
        axs[0].step(x_values, y_values, where='mid')
        axs[0].set_ylim(-0.5, 1.5)
        axs[0].set_yticks([0, 1])
        axs[0].set_xlabel('Time (seconds)')
        axs[0].set_ylabel('Bit Value')
        axs[0].set_title('Digital Signal Representation of First 10 Pixel Values in Binary')
        axs[0].grid(True)

        # Segunda gráfica: Señal cosenoidal
        axs[1].plot(x_dense, cosine_signal)
        axs[1].set_title('Señal Cosenoidal de 1V y 1MHz')
        axs[1].set_xlabel('Time (seconds)')
        axs[1].set_ylabel('Amplitude (V)')
        axs[1].grid(True)

        # Tercera gráfica: Otra transformación (por ejemplo, duplicar cada bit)
        y_values_duplicated = [bit for bit in y_values for _ in range(2)]
        x_values_duplicated = np.linspace(0, 1, len(y_values_duplicated), endpoint=False)
        axs[2].step(x_values_duplicated, y_values_duplicated, where='mid', color='g')
        axs[2].set_ylim(-0.5, 1.5)
        axs[2].set_yticks([0, 1])
        axs[2].set_xlabel('Time (seconds)')
        axs[2].set_ylabel('Bit Value')
        axs[2].set_title('Duplicated Digital Signal')
        axs[2].grid(True)
            
        
        # Ajustar el layout para que las etiquetas no se solapen
        plt.tight_layout()
        plt.show()
        # Graficar la señal digital
        #plt.figure(figsize=(10, 2))
        #plt.step(x_values, y_values, where='mid')
        #plt.ylim(-0.5, 1.5)
        #plt.yticks([0, 1])
        #plt.xlabel('Bit Index')
        #plt.ylabel('Bit Value')
        #plt.title('Digital Signal Representation of First 10 Pixel Values in Binary')
        #plt.grid(True)
        #plt.show()

    def modulation_process(self):
        if self.file_type == 'I' and self.image is not None and self.modulation is not None and self.bits is not None:
            quantization_levels = 2 ** self.bits
            max_val = 255
            print(self.image)
            quantized_image = (self.image / max_val * (quantization_levels - 1)).astype(int)
            re_quantized_image = (quantized_image / (quantization_levels - 1) * max_val).astype(np.uint8)
            processed_image = Image.fromarray(re_quantized_image)
            self.photo = ImageTk.PhotoImage(processed_image)
            self.canvas.create_image(250, 250, image=self.photo)
            self.plot_binary_signal(self.image)
        elif self.file_type == 'A' and self.audio is not None:
            # Implement audio processing if needed
            pass
    
root = tk.Tk()
app = ImageProcessorApp(root)
root.mainloop()

import tkinter as tk
from tkinter import filedialog, Menu, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.interpolate import interp1d
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
        self.file_type = tk.StringVar()

        top = tk.Toplevel(self.root)
        top.title("Select File Type")

        image_check = tk.Checkbutton(top, text="Image", variable=self.file_type, onvalue="I", offvalue="")
        audio_check = tk.Checkbutton(top, text="Audio", variable=self.file_type, onvalue="A", offvalue="")
        select_button = tk.Button(top, text="Seleccionar", command=top.destroy)

        image_check.pack()
        audio_check.pack()
        select_button.pack()

        self.root.wait_window(top)

        file_type = self.file_type.get()
        if file_type not in ['I', 'A']:
            messagebox.showerror("Invalid Input", "Seleccione una opción válida")
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

    def plot_binary_signal(self, image_array, n_bits_por_baudio):
        
        flattened_image = image_array.flatten()
        Muestra = flattened_image[:n_bits_por_baudio]
        binary_values = [np.binary_repr(value, width=8) for value in Muestra]     # Convertir a binario
        bit_sequences = [[int(bit) for bit in binary_value] for binary_value in binary_values]        # Convertir binarios a listas de bits
        bit_sequence_flat = [bit for sequence in bit_sequences for bit in sequence]        # Aplanar la lista de listas de bits para la gráfica
        print(bit_sequence_flat)
 
        señal_digital_NRZ = [-1 if bit == 0 else 1 for bit in bit_sequence_flat]        # Convertir 0 a -1 en bit_sequence_flat NRZ

        longitud_bits_por_segundo = len(señal_digital_NRZ) #numero de bits en la cadena
        
        # Configuracion de ejes para señal digital
        x_values = np.linspace(0, 1, longitud_bits_por_segundo, endpoint=False)
        marcas_en_eje_x = [i * (1 / longitud_bits_por_segundo) for i in range(0, longitud_bits_por_segundo+1)]
        y_values = señal_digital_NRZ

        # Parámetros de la señal cosenoidal
        amplitude = 1.0  # Voltios
        frequency = 0.5e6  # 5 MHz
        x_dense = np.linspace(0, 1, 10000)# Necesitamos muchos más puntos para representar adecuadamente una señal de 1 MHz
        cosine_signal = amplitude * np.cos(2 * np.pi * frequency * x_dense)

        # Interpolar la señal digital para que coincida con el tiempo de muestreo del coseno
        interpolation_function = interp1d(x_values, y_values, kind='nearest', fill_value='extrapolate')
        y_interpolated = interpolation_function(x_dense)

        # Crear una figura con 3 subplots (en una columna)
        fig, axs = plt.subplots(3, 1, figsize=(10, 6))

        # Primera gráfica: Señal digital original (interpolada)
        axs[0].step(x_dense, y_interpolated, where='post')
        axs[0].set_ylim(-1.5, 1.5)
        axs[0].set_yticks([-1, 0, 1])
        axs[0].set_xticks(marcas_en_eje_x)
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

        #Seleccionando la tecnica de modulacion
        if self.modulation == "ASK":
            señal_modulada = (1 + y_interpolated) * (amplitude/2) * np.cos(2 * np.pi * frequency * x_dense)
        elif self.modulation == "8PSK":
            phase_map = {
                (0, 0, 0): -112.5,
                (0, 0, 1): -157.5,
                (0, 1, 0): -67.5,
                (0, 1, 1): -22.5,
                (1, 0, 0): 112.5,
                (1, 0, 1): 157.5,
                (1, 1, 0): 67.5,
                (1, 1, 1): 22.5
            }
            
            señal_modulada = np.array([])

            for i in range(0, len(bit_sequence_flat), 3):
                bits = tuple(bit_sequence_flat[i:i+3])
                if len(bits) < 3:
                    # Completar con ceros si no hay suficientes bits
                    bits += (0,) * (3 - len(bits))
                phase = phase_map[bits]
                phase_radians = np.deg2rad(phase)
                signal_segment = np.cos(2 * np.pi * frequency * x_dense[i:i+10000//(len(bit_sequence_flat)//3)] + phase_radians)
                señal_modulada = np.concatenate((señal_modulada, signal_segment))

        elif self.modulation == "16QAM":
            amplitude_phase_map = {
                (0, 0, 0, 0): (0.311, -135),
                (0, 0, 0, 1): (0.85, -165),
                (0, 0, 1, 0): (0.311, 45),
                (0, 0, 1, 1): (0.85, -15),
                (0, 1, 0, 0): (0.85, -105),
                (0, 1, 0, 1): (1.161, -135),
                (0, 1, 1, 0): (0.85, -75),
                (0, 1, 1, 1): (1.161, -45),
                (1, 0, 0, 0): (0.311, 135),
                (1, 0, 0, 1): (0.85, 165),
                (1, 0, 1, 0): (0.311, 75),
                (1, 0, 1, 1): (0.85, 15),
                (1, 1, 0, 0): (0.85, 105),
                (1, 1, 0, 1): (1.161, 135),
                (1, 1, 1, 0): (0.85, 75),
                (1, 1, 1, 1): (1.161, 45)
            }

            señal_modulada = np.array([])
            num_segments = len(bit_sequence_flat) // 4
            segment_length = len(x_dense) // num_segments

            for i in range(0, len(bit_sequence_flat), 4):
                bits = tuple(bit_sequence_flat[i:i+4])
                if len(bits) < 4:
                    bits += (0,) * (4 - len(bits))  # Completar con ceros si no hay suficientes bits
                amplitude, phase = amplitude_phase_map[bits]
                phase_radians = np.deg2rad(phase)
                start_idx = (i // 4) * segment_length
                end_idx = start_idx + segment_length
                x_segment = x_dense[start_idx:end_idx]
                signal_segment = amplitude * np.cos(2 * np.pi * frequency * x_segment + phase_radians)
                señal_modulada = np.concatenate((señal_modulada, signal_segment))

        # Tercera gráfica: Señal modulada
        axs[2].plot(x_dense, señal_modulada)
        axs[2].set_title('Señal Modulada AM')
        axs[2].set_xlabel('Time (seconds)')
        axs[2].set_ylabel('Amplitude (V)')
        axs[2].grid(True)
        
        # Ajustar el layout para que las etiquetas no se solapen
        plt.tight_layout()
        plt.show()

    def modulation_process(self):
        if self.file_type == 'I' and self.image is not None and self.modulation is not None and self.bits is not None:

            if self.modulation == "ASK":
                self.plot_binary_signal(self.image, 1)
            elif self.modulation == "8PSK":
                self.plot_binary_signal(self.image, 3)
            elif self.modulation == "16QAM":
                self.plot_binary_signal(self.image, 5)

        elif self.file_type == 'A' and self.audio is not None:
            # Implement audio processing if needed
            pass
    
root = tk.Tk()
app = ImageProcessorApp(root)
root.mainloop()
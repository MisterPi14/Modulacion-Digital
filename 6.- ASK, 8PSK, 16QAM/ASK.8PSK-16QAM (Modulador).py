import tkinter as tk
from tkinter import filedialog, Menu, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.interpolate import interp1d
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")

        # Crear un contenedor común
        self.container = tk.Frame(root)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Crear un frame para la imagen
        self.image_frame = tk.Frame(self.container)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.image_frame, width=500, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Crear un frame para el audio
        self.audio_frame = tk.Frame(self.container)

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
            self.bits_menu.add_command(label=f"{2**bits} bits", command=lambda b=2**bits: self.set_bits(b))


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
    ########################################  Procesos Imagen  ###############################################
    def display_image(self):
        # Ocultar el frame de audio si está visible
        self.audio_frame.pack_forget()
        # Mostrar el frame de la imagen
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        #Abriendo foto y creando variable
        image = Image.open(self.file_path)
        image = ImageOps.grayscale(image)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image = image.resize((canvas_width, canvas_height), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(250, 250, image=self.photo)
        self.image = np.array(image)
        print(type(self.image))

    def recuantizar_imagen(self, imagen, n_bits):
        if not (1 <= n_bits <= 8):
            raise ValueError("El número de bits debe estar entre 1 y 8")

        niveles = 2 ** n_bits
        factor = 256 // niveles
        
        imagen_recuantizada = (imagen // factor) * factor
        return imagen_recuantizada

    ########################################  Procesos Audio  ###############################################

    def display_audio(self):
        rate, self.audio = wavfile.read(self.file_path)

        # Ocultar el frame de la imagen si está visible
        self.image_frame.pack_forget()

        # Mostrar el frame de audio
        self.audio_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Limpiar cualquier figura previa
        for widget in self.audio_frame.winfo_children():
            widget.destroy()

        figura, self.eje = plt.subplots()
        lienzo = FigureCanvasTkAgg(figura, self.audio_frame)
        widget_lienzo = lienzo.get_tk_widget()
        widget_lienzo.pack(fill=tk.BOTH, expand=True)

        self.trazar_forma_onda_audio(self.audio)

    def recuantizar_audio(self, audio_array, bits):
        if bits:
            max_val = np.max(np.abs(audio_array))
            audio_unitario = audio_array / max_val
            dinamicRange = (2 ** bits)-1
            quantized_audio = np.round(audio_unitario * dinamicRange) / dinamicRange * max_val
            return quantized_audio
    
    def trazar_forma_onda_audio(self, audio_array):
        self.eje.clear()
        self.eje.plot(audio_array)
        self.eje.set_title("Señal de audio digital")
        self.eje.set_xlabel("Muestras")
        self.eje.set_ylabel("Nivel de voltaje")
        # Ajustar los límites del eje Y para aumentar la escala en amplitud
        max_amplitud = np.max(np.abs(audio_array))
        self.eje.set_ylim(-max_amplitud * 1.2, max_amplitud * 1.2)
        # Ajustar los límites del eje X para aumentar la escala en el tiempo
        self.eje.set_xlim(0, len(audio_array) * 1.2)

        # Actualizar el lienzo
        self.eje.figure.canvas.draw()


    ########################################  Logica de la aplicacion  ###############################################

    def set_modulation(self, modulation_type):
        self.modulation = modulation_type
        if self.bits is not None:
            self.modulation_process()
        
    def set_bits(self, bits):
        self.bits = bits
        if self.modulation is not None:
            self.modulation_process()

    def plot_binary_signal(self, secuencia_bits, n_bits_por_baudio):
        
        if self.file_type == 'I':
            flattened_image = secuencia_bits.flatten()
            Muestra = flattened_image[:n_bits_por_baudio]
            binary_values = [np.binary_repr(value, width=8) for value in Muestra]     # Convertir a binario
            bit_sequences = [[int(bit) for bit in binary_value] for binary_value in binary_values]        # Convertir binarios a listas de bits
            bit_sequence_flat = [bit for sequence in bit_sequences for bit in sequence]        # Aplanar la lista de listas de bits para la gráfica
        elif self.file_type == 'A':
            audio_bits = np.unpackbits(np.array(secuencia_bits, dtype=np.uint8))
            bit_sequence_flat = audio_bits[:n_bits_por_baudio * 8].tolist()


        print(bit_sequence_flat)
 
        señal_digital_NRZ = [-1 if bit == 0 else 1 for bit in bit_sequence_flat]        # Convertir 0 a -1 en bit_sequence_flat NRZ

        longitud_bits_por_segundo = len(señal_digital_NRZ) #numero de bits en la cadena
        
        # Configuracion de ejes para señal digital
        x_values = np.linspace(0, 1, longitud_bits_por_segundo, endpoint=False)
        marcas_en_eje_x = [i * (1 / longitud_bits_por_segundo) for i in range(0, longitud_bits_por_segundo+1)]
        y_values = señal_digital_NRZ

        # Parámetros de la señal cosenoidal
        amplitude = 1.0  # Voltios
        frequency = 0.15e6  # 5 MHz
        x_dense = np.linspace(0, 1, 10000)# Necesitamos muchos más puntos para representar adecuadamente una señal de 1 MHz
        cosine_signal = amplitude * np.sin(2 * np.pi * frequency * x_dense)

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
        axs[0].set_xlabel('Tiempo (segundos)')
        axs[0].set_ylabel('Amplitud (voltaje)')
        axs[0].set_title('Señal digital (Primeros 8 baudios)')
        axs[0].grid(True)

        # Segunda gráfica: Señal cosenoidal
        axs[1].plot(x_dense, cosine_signal)
        axs[1].set_title('Señal portadora senoidal de 1V y 1MHz')
        axs[1].set_xlabel('Tiempo (segundos)')
        axs[1].set_ylabel('Amplitud (voltaje)')
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
                print(bits, phase)
                #phase_radians = np.deg2rad(phase)
                signal_segment = np.cos(2 * np.pi * frequency * x_dense[i:i+10000//(len(bit_sequence_flat)//3)] + phase)
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
                print(bits, amplitude, phase)
                #phase_radians = np.deg2rad(phase)
                start_idx = (i // 4) * segment_length
                end_idx = start_idx + segment_length
                x_segment = x_dense[start_idx:end_idx]
                signal_segment = amplitude * np.cos(2 * np.pi * frequency * x_segment + phase)
                señal_modulada = np.concatenate((señal_modulada, signal_segment))

        # Tercera gráfica: Señal modulada
        axs[2].plot(x_dense, señal_modulada)
        axs[2].set_title('Señal Modulada en '+self.modulation)
        axs[2].set_xlabel('Tiempo (segundos)')
        axs[2].set_ylabel('Amplitud (voltaje)')
        axs[2].grid(True)
        
        # Ajustar el layout para que las etiquetas no se solapen
        fig.tight_layout()
        fig.show()

    def modulation_process(self):
        if self.file_type == 'I' and self.image is not None:
            self.imagenRecuantArr = self.recuantizar_imagen(self.image, self.bits)
            self.imagenRecuantizada = ImageTk.PhotoImage(Image.fromarray(self.imagenRecuantArr))
            self.canvas.create_image(250, 250, image=self.imagenRecuantizada)
            if self.modulation == "ASK":
                self.plot_binary_signal(self.imagenRecuantArr, 1)
            elif self.modulation == "8PSK":
                self.plot_binary_signal(self.imagenRecuantArr, 3)
            elif self.modulation == "16QAM":
                self.plot_binary_signal(self.imagenRecuantArr, 4)

        elif self.file_type == 'A' and self.audio is not None:
            AudioRecuantizado = self.recuantizar_audio(self.audio, self.bits)
            self.trazar_forma_onda_audio(AudioRecuantizado)# Graficar la señal cuantizada
            if self.modulation == "ASK":
                self.plot_binary_signal(AudioRecuantizado, 1)
            elif self.modulation == "8PSK":
                self.plot_binary_signal(AudioRecuantizado, 3)
            elif self.modulation == "16QAM":
                self.plot_binary_signal(AudioRecuantizado, 4)
        
        self.modulation = None
        self.bits = None
    
root = tk.Tk()
app = ImageProcessorApp(root)
root.mainloop()
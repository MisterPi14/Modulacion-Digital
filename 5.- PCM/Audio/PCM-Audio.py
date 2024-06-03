import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import pyaudio
import wave
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

valores_permitidos = [4000, 8000, 10000, 20000, 30000, 44100]

class AplicacionAudio:
    def __init__(self, maestro):
        self.maestro = maestro
        self.BLOQUE = 1024
        self.FORMATO = pyaudio.paInt16 
        self.TASA = 4000
        self.CANALES = 1
        self.cuadros = []
        self.esta_grabando = False

        self.pa = pyaudio.PyAudio()

        self.contenedor_controles = tk.Frame(maestro)
        self.contenedor_controles.pack(side=tk.LEFT, fill=tk.Y, padx=50, pady=100)

        contenedor_btn_canales = tk.Frame(self.contenedor_controles)
        contenedor_btn_canales.pack(padx=10, pady=10)

        self.btncanetiqueta = tk.Label(contenedor_btn_canales, text="Numero de canales mono->1 estereo->2\t", font=('Arial', 12))
        self.btncanetiqueta.pack(side=tk.LEFT)

        self.boton_nCanales = tk.Button(contenedor_btn_canales, text="Mono", command=self.convercion_mono_estereo, width=10)
        self.boton_nCanales.pack(side=tk.RIGHT)

        contenedor_fb_slider = tk.Frame(self.contenedor_controles)
        contenedor_fb_slider.pack(padx=10, pady=10)

        self.fbetiqueta = tk.Label(contenedor_fb_slider, text="Frecuencia de muestreo\t", font=('Arial', 12))
        self.fbetiqueta.pack(side=tk.LEFT)

        self.fb_slider = tk.Scale(contenedor_fb_slider, from_=min(valores_permitidos), to=max(valores_permitidos),
                            orient='horizontal', length=400, tickinterval=0, resolution=-1,
                            showvalue=1)
        
        self.fb_slider.configure(sliderlength=20, troughcolor='blue', command=self.ajustar_deslizador)
        self.fb_slider.pack(side=tk.RIGHT)
        self.fb_slider.get()  # leer el valor del slide

        contenedor_botonera_acciones = tk.Frame(self.contenedor_controles)
        contenedor_botonera_acciones.pack(padx=10, pady=10)

        self.btn_grabar = tk.Button(contenedor_botonera_acciones, text="⏺️ (Grabar)", command=self.iniciar_grabacion)
        self.btn_grabar.pack(side=tk.LEFT, padx=20)

        self.btn_parar = tk.Button(contenedor_botonera_acciones, text="⏹️ (Detener)", command=self.parar_grabacion, state='disabled')
        self.btn_parar.pack(side=tk.LEFT, padx=20)

        self.btn_reproducir = tk.Button(contenedor_botonera_acciones, text="▶️ (Reproducir)", command=lambda: self.reproducir_audio_desde_archivo("output.wav"))
        self.btn_reproducir.pack(side=tk.LEFT, padx=20)

        self.contenedor_botonera_cuantizacion = tk.Frame(self.contenedor_controles)
        self.contenedor_botonera_cuantizacion.pack(padx=10, pady=100)

        self.btn_recuantizar = tk.Button(self.contenedor_botonera_cuantizacion, text="Recuantizar y Guardar", command=self.recuantizar_y_guardar)
        self.btn_recuantizar.pack(side=tk.LEFT, padx=20)

        self.contenedor_graficador = tk.Frame(maestro)
        self.contenedor_graficador.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.figura, self.eje = plt.subplots()
        self.lienzo = FigureCanvasTkAgg(self.figura, self.contenedor_graficador)
        self.widget_lienzo = self.lienzo.get_tk_widget()
        self.widget_lienzo.pack(fill=tk.BOTH, expand=True)

    def convercion_mono_estereo(self):
        nuevo_valor = "Estereo" if self.boton_nCanales['text'] == "Mono" else "Mono"
        self.boton_nCanales.config(text=nuevo_valor)
        self.CANALES = 1 if self.boton_nCanales['text'] == "Mono" else 2

    def ajustar_deslizador(self, valor):
        valor_mas_cercano = min(valores_permitidos, key=lambda x: abs(x - float(valor)))
        self.fb_slider.set(valor_mas_cercano)
        self.TASA = self.fb_slider.get()

    def iniciar_grabacion(self):
        self.cuadros = []
        self.esta_grabando = True
        self.stream = self.pa.open(format=self.FORMATO, channels=self.CANALES, rate=self.TASA, input=True, frames_per_buffer=self.BLOQUE)
        self.thread = threading.Thread(target=self.grabar)
        self.thread.start()
        self.btn_grabar.config(state='disabled')
        self.btn_parar.config(state='normal')

    def grabar(self):
        while self.esta_grabando:
            data = self.stream.read(self.BLOQUE)
            self.cuadros.append(data)

    def parar_grabacion(self):
        self.esta_grabando = False
        self.stream.stop_stream()
        self.stream.close()
        self.btn_grabar.config(state='normal')
        self.btn_parar.config(state='disabled')
        self.guardar_wav()

    def guardar_wav(self):
        wf = wave.open("output.wav", 'wb')
        wf.setnchannels(self.CANALES)
        wf.setsampwidth(self.pa.get_sample_size(self.FORMATO))
        wf.setframerate(self.TASA)
        wf.writeframes(b''.join(self.cuadros))
        wf.close()
        self.trazar_forma_onda_audio(np.frombuffer(b''.join(self.cuadros), dtype=np.int16))

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
        self.lienzo.draw()

    def aplicar_resolucion_bits(self, event=None):
        bits = int(self.combo.get())
        if bits:
            audio_array = np.frombuffer(b''.join(self.cuadros), dtype=np.int16)
            cuantificado = self.cuantificar(audio_array, bits)
            self.guardar_wav_recuantizado(cuantificado, bits)
            self.trazar_forma_onda_audio(cuantificado)  # Graficar la señal cuantizada
            self.reproducir_audio_recuantizado(bits)

    def recuantizar_y_guardar(self):
        messagebox.showinfo("Instrucciones", "Introduce en la caja de opciones el numero o profundidad de bits para el codigo PCM (sin contemplar signo)")
        self.etiqueta_combo = tk.Label(self.contenedor_botonera_cuantizacion, text="Cantidad bits/muestra:\t", font=('Arial', 12))
        self.etiqueta_combo.pack(side=tk.LEFT)
        self.combo = ttk.Combobox(self.contenedor_botonera_cuantizacion)
        self.combo['values'] = ("1", "2", "4", "8")  # Lista de opciones
        self.combo.current(0)  # Establecer la opción predeterminada
        self.combo.pack(pady=20)
        self.combo.bind("<<ComboboxSelected>>", self.aplicar_resolucion_bits)  # Manejar la selección

    def cuantificar(self, audio_array, bits):
        max_val = np.max(np.abs(audio_array))
        levels = 2 ** bits
        return np.int16(((audio_array + max_val) / (2 * max_val) * (levels - 1)).round() * (2 * max_val / (levels - 1)) - max_val)

    def guardar_wav_recuantizado(self, cuantificado_array, bits):
        output_filename = f"Grabacion_cuantizada_a_{bits}bits.wav"
        txt_filename = f"Codigo_de_cuantizacion_a_{bits}bits.txt"
        self.guardar_binario(cuantificado_array, txt_filename, bits)  # Guardar en formato binario

        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(self.CANALES)
        wf.setsampwidth(self.pa.get_sample_size(self.FORMATO))
        wf.setframerate(self.TASA)
        wf.writeframes(cuantificado_array.tobytes())
        wf.close()

    def guardar_binario(self, cuantificado_array, filename, bits):
        with open(filename, 'w') as f:
            for muestra in cuantificado_array:
                # Ajustar cada muestra a n+1 bits para incluir el bit de signo
                n_bits_muestra = bits + 1
                binario = format(muestra & ((1 << n_bits_muestra) - 1), f'0{n_bits_muestra}b')
                f.write(binario + '\n')

    def reproducir_audio_recuantizado(self, bits):
        if bits:
            filename = f"Grabacion_cuantizada_a_{bits}bits.wav"
            if os.path.exists(filename):
                self.reproducir_audio_desde_archivo(filename)
            else:
                messagebox.showerror("Error", "El archivo especificado no existe.")

    def reproducir_audio_desde_archivo(self, filename):
        with wave.open(filename, 'rb') as wf:
            stream = self.pa.open(format=self.pa.get_format_from_width(wf.getsampwidth()),
                                  channels=wf.getnchannels(),
                                  rate=wf.getframerate(),
                                  output=True)
            data = wf.readframes(self.BLOQUE)
            while data:
                stream.write(data)
                data = wf.readframes(self.BLOQUE)
            stream.stop_stream()
            stream.close()

Interfaz = tk.Tk()
Interfaz.title("Audio Convertidor mono-estereo y PCM")
Interfaz.config(bg="lightblue")
AplicacionAudio(Interfaz)
Interfaz.mainloop()

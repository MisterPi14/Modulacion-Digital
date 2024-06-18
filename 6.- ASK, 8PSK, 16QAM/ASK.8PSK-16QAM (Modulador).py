import tkinter as tk
from tkinter import filedialog, Menu
from PIL import Image, ImageTk, ImageOps
import numpy as np

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
        self.file_menu.add_command(label="Open", command=self.open_image)

        self.modulation_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Modulation", menu=self.modulation_menu)
        self.modulation_menu.add_command(label="ASK", command=lambda: self.set_modulation("ASK"))
        self.modulation_menu.add_command(label="8PSK", command=lambda: self.set_modulation("8PSK"))
        self.modulation_menu.add_command(label="16QAM", command=lambda: self.set_modulation("16QAM"))

        self.bits_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Bits", menu=self.bits_menu)
        for bits in range(0, 4):
            self.bits_menu.add_command(label=f"{2**bits} bits", command=lambda b=bits: self.set_bits(b))

        self.image_path = None
        self.modulation = None
        self.bits = None

    def open_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if self.image_path:
            self.display_image()

    def display_image(self):
        image = Image.open(self.image_path)
        image = ImageOps.grayscale(image)
        # Obtener el tamaño del canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        # Redimensionar la imagen al tamaño del canvas
        image = image.resize((canvas_width, canvas_height), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(250, 250, image=self.photo)
        self.image = np.array(image)

    def set_modulation(self, modulation_type):
        self.modulation = modulation_type
        self.process_image()
        
    def set_bits(self, bits):
        self.bits = bits
        self.process_image()

    def process_image(self):
        if self.image is not None and self.modulation is not None and self.bits is not None:
            quantization_levels = 2 ** self.bits
            max_val = 255
            quantized_image = (self.image / max_val * (quantization_levels - 1)).astype(int)
            re_quantized_image = (quantized_image / (quantization_levels - 1) * max_val).astype(np.uint8)
            processed_image = Image.fromarray(re_quantized_image)
            self.photo = ImageTk.PhotoImage(processed_image)
            self.canvas.create_image(250, 250, image=self.photo)

root = tk.Tk()
app = ImageProcessorApp(root)
root.mainloop()

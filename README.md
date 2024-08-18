# Digital Modulation Projects Repository

Welcome to the Digital Modulation Projects Repository. This collection of Python-based projects is designed to demonstrate various digital modulation techniques, showcasing their implementation and visualization across different information transfer devices. Each project stands alone as an educational tool, providing insights into how these modulation techniques are applied in real-world scenarios.

## Overview of Projects

### PCM Audio Converter
- **File:** `PCM-Audio.py`
- **Description:** This project allows users to record, quantize, and playback audio signals. Users can switch between mono and stereo channels, adjust the sampling frequency, and apply different bit resolutions for Pulse Code Modulation (PCM). The project also includes the ability to visualize audio waveforms, helping users understand the effects of quantization on audio signals.
- **Key Features:**
  - **Interactive GUI:** Built with Tkinter, the graphical user interface makes it easy to control and visualize the audio processing steps.
  - **Real-Time Audio Processing:** The project processes and visualizes audio data in real time, demonstrating how changes in sampling rate and bit depth affect the signal.
  - **OOP Implementation:** The code is structured using Object-Oriented Programming, making the project modular and extensible.

### PCM Image Processor
- **File:** `PCM-Imagen.py`
- **Description:** This project provides tools for loading, quantizing, and re-quantizing images at various bit depths. The application enables users to convert images to grayscale, black and white, or color and observe how different quantization levels impact image quality. The project also generates corresponding PCM codes for the quantized images, illustrating the digital representation of visual data.
- **Key Features:**
  - **Image Quantization:** Supports multiple quantization levels, from 1-bit to 64-bits per sample, allowing users to explore the trade-offs between image fidelity and data size.
  - **Interactive Image Manipulation:** The GUI lets users experiment with different image transformations and instantly see the results.
  - **OOP Structure:** The project leverages OOP principles to organize the image processing functions, enhancing code readability and maintainability.

### Modulator: ASK, 8PSK, and 16QAM
- **File:** `ASK.8PSK-16QAM (Modulador).py`
- **Description:** This project implements three different modulation techniques: Amplitude Shift Keying (ASK), 8-Phase Shift Keying (8PSK), and 16-Quadrature Amplitude Modulation (16QAM). It can process both images and audio files, providing a clear visualization of how each modulation technique alters the transmitted signals.
- **Key Features:**
  - **Versatile Modulation Techniques:** Users can choose between ASK, 8PSK, and 16QAM, observing the modulation effects on both image and audio data.
  - **Graphical Visualization:** The project displays the modulated signals, offering a visual understanding of the differences between each modulation technique.
  - **Integrated OOP Design:** The code utilizes OOP to manage different modulation processes, making it easier to extend or modify.

## Objectives

Each of these projects serves as a practical example of how digital modulation techniques are applied in devices that handle audio and visual data. By working with these projects, users can gain hands-on experience with concepts like Pulse Code Modulation, quantization, and various modulation schemes. The projects are designed not only to educate but also to provide a platform for experimentation and further exploration of digital communication principles.

## Installation and Usage

To run the projects, ensure that Python 3.x is installed along with the required libraries. You can install the necessary dependencies using pip:

```bash
pip install numpy matplotlib pillow scipy pyaudio
```

To run any project, navigate to the directory containing the script and execute it with Python:

```bash
python PCM-Audio.py
python PCM-Imagen.py
python ASK.8PSK-16QAM\ (Modulador).py
```

## Features and Development Approach

While each project is self-contained, they all share common development practices such as Object-Oriented Programming (OOP), which contributes to their modularity, scalability, and ease of use. The use of OOP across these projects allows for better organization of code, making it easier to add new features or enhance existing ones.

import numpy as np

# Suponiendo que 'audio_samples' es una lista de muestras de audio
audio_samples = [100, -100, 200, -200, 32767, -32768]
audio_array = np.array(audio_samples, dtype=np.int8)

# Convertir cada número a su representación binaria
binary_representations = [format(x, '016b') for x in audio_array]
for value, binary in zip(audio_array, binary_representations):
    print(f'{value}: {binary}')

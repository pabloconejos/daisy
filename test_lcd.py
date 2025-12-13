from drivers.waveshare_1in69.lib import LCD_1inch69
from PIL import Image, ImageSequence
import time

# Inicializar pantalla
disp = LCD_1inch69.LCD_1inch69(rst=27, dc=25, bl=18)
disp.Init()
disp.clear()

# Cargar GIF
gif = Image.open("assets/prueba_gif.gif")

# Reproducir animación
try:
    while True:  # bucle infinito
        for frame in ImageSequence.Iterator(gif):
            # Convertir frame al tamaño y formato de la pantalla
            frame = frame.convert("RGB")
            frame = frame.resize((disp.width, disp.height))

            disp.ShowImage(frame)

            # Duración del frame (si existe en el GIF)
            duration = frame.info.get("duration", 100)
            time.sleep(duration / 1000.0)

except KeyboardInterrupt:
    disp.clear()

import os
import time
import threading
from dataclasses import dataclass
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from drivers.waveshare_1in69.lib import LCD_1inch69


# =========================
# Estado de la pantalla
# =========================
@dataclass
class ScreenState:
    mode: str = "clock"      # "clock" | "spotify" | "status"
    title: str = ""
    subtitle: str = ""


# =========================
# Display principal
# =========================
class DaisyDisplay:

    def __init__(
        self,
        rst=27,
        dc=25,
        bl=18,
        bl_freq=100,
        brightness=80,
        fps=1,
    ):
        self.state = ScreenState()
        self.fps = fps
        self._lock = threading.Lock()
        self._stop = False

        # --- Init LCD ---
        self.disp = LCD_1inch69.LCD_1inch69(
            rst=rst,
            dc=dc,
            bl=bl,
            bl_freq=bl_freq
        )
        self.disp.Init()
        self.disp.clear()

        try:
            self.disp.bl_DutyCycle(brightness)
        except Exception:
            pass

        # --- Fonts ---
        def load_font(path, size):
            return ImageFont.truetype(path, size)

        FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

        self.font_big = load_font(FONT_BOLD, 68)   # HORA → Extra Bold visual
        self.font_med = load_font(FONT_REG, 28)    # Wed, textos
        self.font_small = load_font(FONT_REG, 20)


        # --- Start render thread ---
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    # =========================
    # API pública
    # =========================
    def show_clock(self):
        with self._lock:
            self.state.mode = "clock"

    def show_spotify(self, song: str, artist: str):
        with self._lock:
            self.state.mode = "spotify"
            self.state.title = song[:32]
            self.state.subtitle = artist[:32]

    def show_status(self, title: str, subtitle: str = ""):
        with self._lock:
            self.state.mode = "status"
            self.state.title = title[:32]
            self.state.subtitle = subtitle[:32]

    def stop(self):
        self._stop = True

    # =========================
    # Loop de render
    # =========================
    def _loop(self):
        interval = 1.0 / max(1, self.fps)
        last_key = None

        while not self._stop:
            with self._lock:
                mode = self.state.mode
                title = self.state.title
                subtitle = self.state.subtitle

            key = (mode, title, subtitle)

            if mode == "clock":
                self._render_clock()
            else:
                if key != last_key:
                    self._render_card(mode, title, subtitle)

            last_key = key
            time.sleep(interval)

    # =========================
    # RENDER: Reloj estilo Apple
    # =========================
    def _render_clock(self):
        W, H = self.disp.width, self.disp.height

        now = datetime.now()
        hhmm = now.strftime("%H:%M")
        dow = now.strftime("%a")   # Wed
        day = now.strftime("%d")   # 30

        # Colores
        BG = (0, 0, 0)
        BLUE = (58, 112, 255)
        ORANGE = (255, 136, 36)
        YELLOW = (255, 215, 0)
        TEXT = (0, 0, 0)

        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)

        pad = 14
        gap = 14

        # --- Pastilla superior (hora) ---
        pill_h = 105
        pill = (pad, pad, W - pad, pad + pill_h)
        d.rounded_rectangle(pill, radius=26, fill=BLUE)

        tw, th = d.textbbox((0, 0), hhmm, font=self.font_big)[2:]
        d.text(
            ((W - tw) // 2, pad + (pill_h - th) // 2 - 4),
            hhmm,
            fill=TEXT,
            font=self.font_big,
        )

        # --- Zona inferior ---
        bottom_top = pill[3] + gap
        bottom_h = H - bottom_top - pad
        box_w = (W - pad * 2 - gap) // 2

        # Izquierda: fecha
        left = (pad, bottom_top, pad + box_w, bottom_top + bottom_h)
        d.rounded_rectangle(left, radius=26, fill=ORANGE)

        d.text((left[0] + 18, left[1] + 18), dow, fill=TEXT, font=self.font_med)
        d.text((left[0] + 18, left[1] + 60), str(int(day)), fill=TEXT, font=self.font_big)

        # Derecha: carita feliz 🙂
        right = (pad + box_w + gap, bottom_top, W - pad, bottom_top + bottom_h)
        side = min(right[2] - right[0], right[3] - right[1])
        cx0 = right[0] + ((right[2] - right[0] - side) // 2)
        cy0 = right[1] + ((right[3] - right[1] - side) // 2)
        circle = (cx0, cy0, cx0 + side, cy0 + side)

        # Círculo
        d.ellipse(circle, fill=YELLOW)

        # Ojos
        eye_r = 6
        eye_y = cy0 + side // 3
        d.ellipse((cx0 + side * 0.30 - eye_r, eye_y - eye_r,
                   cx0 + side * 0.30 + eye_r, eye_y + eye_r), fill=TEXT)
        d.ellipse((cx0 + side * 0.70 - eye_r, eye_y - eye_r,
                   cx0 + side * 0.70 + eye_r, eye_y + eye_r), fill=TEXT)

        # Sonrisa
        smile_box = (
            cx0 + side * 0.30,
            cy0 + side * 0.45,
            cx0 + side * 0.70,
            cy0 + side * 0.80
        )
        d.arc(smile_box, start=0, end=180, fill=TEXT, width=4)

        self.disp.ShowImage(img)

    # =========================
    # RENDER: tarjetas simples
    # =========================
    def _render_card(self, mode: str, title: str, subtitle: str):
        img = Image.new("RGB", (self.disp.width, self.disp.height), "WHITE")
        d = ImageDraw.Draw(img)

        header = "SPOTIFY" if mode == "spotify" else "ESTADO"
        d.text((10, 10), header, fill="BLACK", font=self.font_med)
        d.line((10, 44, self.disp.width - 10, 44), fill="BLACK", width=2)

        d.text((10, 70), title, fill="BLACK", font=self.font_med)
        if subtitle:
            d.text((10, 110), subtitle, fill="BLACK", font=self.font_small)

        self.disp.ShowImage(img)

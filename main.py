"""THE WORLD TODAY - front page for Friday 27 November 2026.

A pure-stdlib Python program: draws a 1024x1024 newspaper front page
summing up the day's world news and writes it to /output/entry.png.

No Pillow, no network, no randomness: every run writes identical bytes.
Own bitmap font (5x7 glyphs drawn from scratch), own vector drawing,
own PNG encoder (zlib + struct).
"""

import math
import os
import struct
import zlib

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, one row per string, "#" = ink, "." = blank.
# Authored in this session; every glyph typed by hand below.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": (".....", ".....", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": (".....", ".....", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": (".....", ".....", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": (".....", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", ".....", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", ".....", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": (".....", ".....", "11010", "10101", "10101", "10101", "10101"),
    "n": (".....", ".....", "11110", "10001", "10001", "10001", "10001"),
    "o": (".....", ".....", "01110", "10001", "10001", "10001", "01110"),
    "p": (".....", "11110", "10001", "10001", "11110", "10000", "10000"),
    "q": (".....", "01111", "10001", "10001", "01111", "00001", "00001"),
    "r": (".....", ".....", "10110", "11001", "10000", "10000", "10000"),
    "s": (".....", ".....", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11110", "01000", "01000", "01000", "00100"),
    "u": (".....", ".....", "10001", "10001", "10001", "10011", "01101"),
    "v": (".....", ".....", "10001", "10001", "10001", "01010", "00100"),
    "w": (".....", ".....", "10001", "10101", "10101", "10101", "01010"),
    "x": (".....", ".....", "10001", "01010", "00100", "01010", "10001"),
    "y": (".....", ".....", "10001", "10001", "01111", "00001", "01110"),
    "z": (".....", ".....", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", "01100", "01100"),
    ",": (".....", ".....", ".....", ".....", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", ".....", ".....", ".....", "....."),
    "!": ("00100", "00100", "00100", "00100", "00100", ".....", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", ".....", "00100"),
    ":": (".....", "01100", "01100", ".....", "01100", "01100", "....."),
    ";": (".....", "01100", "01100", ".....", "01100", "00100", "01000"),
    "-": (".....", ".....", ".....", "01110", ".....", ".....", "....."),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "€": ("01110", "10001", "10000", "11111", "10000", "10001", "01110"),
    "•": (".....", ".....", "01100", "01100", ".....", ".....", "....."),
    "+": (".....", "00100", "00100", "11111", "00100", "00100", "....."),
}

CHAR_W = 6  # 5 glyph columns + 1 blank column, in font units


def text_width(text, scale):
    """Pixel width of text at a scale (trailing blank column trimmed)."""
    if not text:
        return 0
    return len(text) * CHAR_W * scale - scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.buf = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, bg)

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def fill_rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        r, g, b = color
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1):
                i = base + (x - x0) * 3
                self.buf[i] = r
                self.buf[i + 1] = g
                self.buf[i + 2] = b

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            for x in range(x0, x1):
                self.set_px(x, y + t, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            for y in range(y0, y1):
                self.set_px(x + t, y, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            half = thick // 2
            for a in range(-half, half + 1):
                for b in range(-half, half + 1):
                    self.set_px(x + a, y + b, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            half = int(math.sqrt(max(0, r * r - dy * dy)))
            for dx in range(-half, half + 1):
                self.set_px(cx + dx, cy + dy, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            if ry == 0:
                continue
            half = int(rx * math.sqrt(max(0.0, 1.0 - (dy * dy) / float(ry * ry))))
            for dx in range(-half, half + 1):
                self.set_px(cx + dx, cy + dy, color)

    def fill_poly(self, points, color):
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / float(y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.set_px(x, y, color)

    def star(self, cx, cy, r_out, r_in, color, points=5, rot=-math.pi / 2):
        pts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            a = rot + i * math.pi / points
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.fill_poly(pts, color)

    # ------------------------------------------------------------ text
    def draw_char(self, x, y, ch, scale, color):
        glyph = FONT[ch]
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    self.fill_rect(
                        x + col * scale, y + row * scale,
                        x + col * scale + scale, y + row * scale + scale,
                        color,
                    )

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            self.draw_char(cx, y, ch, scale, color)
            cx += CHAR_W * scale
        return cx

    def draw_text_centered(self, x0, x1, y, text, scale, color):
        w = text_width(text, scale)
        self.draw_text(x0 + (x1 - x0 - w) // 2, y, text, scale, color)


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale) <= max_width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def draw_block(cv, x, y, text, scale, max_width, color, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = 7 * scale + 4
    for line in wrap_text(text, scale, max_width):
        cv.draw_text(x, y, line, scale, color)
        y += leading
    return y


# ---------------------------------------------------------------- png
def encode_png(width, height, buf):
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter: none
        raw += buf[y * stride:(y + 1) * stride]
    data = zlib.compress(bytes(raw), 9)

    def chunk(tag, payload):
        out = struct.pack(">I", len(payload)) + tag + payload
        out += struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", data)
    png += chunk(b"IEND", b"")
    return png


# ------------------------------------------------------------- scenes
def scene_lead_strike(cv, x0, y0, w, h):
    """Night sky over a Kuwait facility: drone, explosion, smoke."""
    night = (13, 27, 62)
    cv.fill_rect(x0, y0, x0 + w, y0 + h, night)
    stars = [(18, 22), (52, 44), (96, 18), (140, 52), (178, 26), (216, 60),
             (258, 20), (300, 46), (338, 24), (382, 58), (410, 30), (70, 84),
             (150, 96), (238, 88), (330, 92), (396, 96), (36, 130), (408, 140)]
    for sx, sy in stars:
        cv.fill_rect(x0 + sx, y0 + sy, x0 + sx + 3, y0 + sy + 3, (235, 235, 245))
    # moon
    cv.fill_circle(x0 + 368, y0 + 52, 26, (232, 228, 200))
    cv.fill_circle(x0 + 360, y0 + 46, 6, (210, 204, 175))
    cv.fill_circle(x0 + 378, y0 + 60, 4, (210, 204, 175))
    # ground
    cv.fill_rect(x0, y0 + h - 96, x0 + w, y0 + h, (8, 14, 34))
    # facility: storage tanks, chimney, hall
    tank = (96, 102, 108)
    tank_top = (130, 136, 142)
    cv.fill_rect(x0 + 30, y0 + h - 62, x0 + 110, y0 + h - 8, tank)
    cv.fill_ellipse(x0 + 70, y0 + h - 62, 40, 10, tank_top)
    cv.fill_rect(x0 + 130, y0 + h - 52, x0 + 200, y0 + h - 8, tank)
    cv.fill_ellipse(x0 + 165, y0 + h - 52, 35, 9, tank_top)
    cv.fill_rect(x0 + 330, y0 + h - 88, x0 + 348, y0 + h - 8, (70, 76, 84))
    cv.fill_rect(x0 + 326, y0 + h - 96, x0 + 352, y0 + h - 88, (150, 60, 50))
    cv.fill_rect(x0 + 220, y0 + h - 40, x0 + 320, y0 + h - 8, (60, 64, 72))
    cv.fill_rect(x0 + 220, y0 + h - 48, x0 + 320, y0 + h - 40, (120, 126, 132))
    # explosion over the hall
    ex, ey = x0 + 268, y0 + h - 118
    cv.fill_circle(ex, ey, 74, (200, 40, 30))
    cv.fill_circle(ex, ey, 52, (255, 140, 0))
    cv.fill_circle(ex, ey, 34, (255, 205, 60))
    cv.star(ex, ey, 46, 18, (255, 230, 120), points=8)
    cv.star(ex, ey, 26, 10, (255, 255, 220), points=8)
    # smoke
    for cx, cy, r in [(236, 196, 18), (258, 176, 24), (286, 158, 20),
                      (312, 176, 16), (296, 198, 14)]:
        cv.fill_circle(x0 + cx, y0 + cy, r, (105, 105, 112))
    # drone, upper left of the blast
    dx, dy = x0 + 108, y0 + 118
    cv.line(dx - 34, dy - 12, dx + 34, dy + 12, (20, 20, 26), 2)
    cv.line(dx - 34, dy + 12, dx + 34, dy - 12, (20, 20, 26), 2)
    for rx, ry in [(dx - 34, dy - 12), (dx + 34, dy + 12),
                   (dx - 34, dy + 12), (dx + 34, dy - 12)]:
        cv.fill_circle(rx, ry, 7, (45, 45, 55))
    cv.fill_rect(dx - 16, dy - 7, dx + 16, dy + 7, (25, 25, 32))
    cv.fill_circle(dx + 20, dy, 4, (255, 60, 60))
    # label
    cv.draw_text(x0 + 14, y0 + 14, "KUWAIT - OVERNIGHT", 2, (240, 240, 245))


def scene_storm(cv, x0, y0, w, h):
    """Nor'easter: storm cloud, rain, lightning, a grounded balloon."""
    cv.fill_rect(x0, y0, x0 + w, y0 + h, (96, 116, 146))
    cv.fill_rect(x0, y0 + 58, x0 + w, y0 + h, (74, 92, 122))
    # cloud
    cloud = (198, 203, 210)
    for cx, cy, r in [(70, 34, 26), (110, 24, 30), (152, 34, 26),
                      (52, 46, 18), (170, 46, 18)]:
        cv.fill_circle(x0 + cx, y0 + cy, r, cloud)
    cv.fill_rect(x0 + 44, y0 + 34, x0 + 180, y0 + 58, cloud)
    # lightning
    cv.fill_poly([(x0 + 196, y0 + 30), (x0 + 212, y0 + 30), (x0 + 202, y0 + 52),
                  (x0 + 214, y0 + 52), (x0 + 190, y0 + 88), (x0 + 198, y0 + 58),
                  (x0 + 188, y0 + 58)], (255, 220, 60))
    # rain, slanted
    rain = (150, 180, 215)
    for rx in range(8, w, 22):
        cv.line(x0 + rx, y0 + 56, x0 + rx - 10, y0 + 88, rain, 2)
    # grounded parade balloon, deflated and tilted
    bx, by = x0 + 238, y0 + 62
    cv.fill_ellipse(bx, by, 44, 22, (196, 62, 52))
    cv.line(bx - 40, by - 8, bx + 40, by - 8, (150, 40, 34), 2)
    cv.line(bx - 40, by + 8, bx + 40, by + 8, (150, 40, 34), 2)
    cv.fill_rect(bx - 10, by + 22, bx + 10, by + 30, (120, 84, 52))
    cv.draw_text(x0 + 10, y0 + 6, "NEW YORK", 2, (240, 240, 245))


def scene_eu(cv, x0, y0, w, h):
    """EU flag field: ring of gold stars around the loan figure."""
    blue = (20, 40, 110)
    gold = (232, 190, 60)
    cv.fill_rect(x0, y0, x0 + w, y0 + h, blue)
    cx, cy, rr = x0 + w // 2, y0 + h // 2, 34
    for i in range(12):
        a = -math.pi / 2 + i * math.pi / 6
        cv.star(int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a)),
                7, 3, gold)
    cv.draw_text_centered(x0, x0 + w, y0 + h // 2 - 14, "45BN", 4, gold)


def scene_dove(cv, x0, y0, w, h):
    """Olive branch and dove over Gaza's sand."""
    cv.fill_rect(x0, y0, x0 + w, y0 + h, (232, 214, 178))
    cv.fill_rect(x0, y0 + h - 14, x0 + w, y0 + h, (198, 170, 128))
    # olive branch
    branch = (86, 128, 58)
    cv.line(x0 + 20, y0 + 78, x0 + 120, y0 + 34, branch, 3)
    for lx, ly in [(44, 66), (64, 56), (84, 46), (104, 38)]:
        cv.fill_ellipse(x0 + lx, y0 + ly, 12, 5, (96, 140, 66))
    for lx, ly in [(52, 74), (74, 64), (96, 54)]:
        cv.fill_ellipse(x0 + lx, y0 + ly, 10, 5, (76, 120, 56))
    # dove
    white = (250, 250, 246)
    cv.fill_ellipse(x0 + 205, y0 + 52, 46, 20, white)
    cv.fill_circle(x0 + 246, y0 + 34, 13, white)
    cv.fill_poly([(x0 + 258, y0 + 32), (x0 + 272, y0 + 37), (x0 + 258, y0 + 40)],
                 (232, 150, 40))
    cv.fill_circle(x0 + 250, y0 + 30, 2, (20, 20, 20))
    cv.fill_poly([(x0 + 168, y0 + 44), (x0 + 216, y0 + 28), (x0 + 224, y0 + 52),
                  (x0 + 186, y0 + 58)], (225, 225, 218))
    cv.fill_poly([(x0 + 162, y0 + 56), (x0 + 150, y0 + 66), (x0 + 164, y0 + 64),
                  (x0 + 172, y0 + 60)], white)
    cv.draw_text(x0 + 10, y0 + 6, "GAZA", 2, (90, 70, 50))


# ------------------------------------------------------------- layout
W = H = 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (176, 30, 30)
BLUE = (31, 58, 110)
GREY = (90, 88, 82)

LEAD_HEADLINE = "DRONE STRIKE IN KUWAIT KILLS TWO ITALIANS"
LEAD_DECK = "Rome blamed Iran for the overnight attack. Tehran denied any role."
LEAD_BODY = (
    "Two Italian technicians were killed when a drone hit a facility in "
    "Kuwait, Italy's foreign minister said. The dead worked for the Italian "
    "unit of German defence group Rheinmetall. Iran denies responsibility "
    "for the strike."
)

SECONDARIES = [
    {
        "kicker": "UNITED STATES",
        "headline": "STORM KNOCKS OUT POWER FOR 800,000",
        "body": (
            "A nor'easter battered the US East Coast, leaving 800,000 "
            "without power. The 100th Macy's parade moved to Saturday."
        ),
        "scene": scene_storm,
    },
    {
        "kicker": "EUROPE",
        "headline": "EU SPLIT OVER €45BN FOR UKRAINE",
        "body": (
            "Leaders in Brussels stayed divided over a €45bn loan for Kyiv "
            "in 2027. Four states resist; Germany wants all 27 to pay."
        ),
        "scene": scene_eu,
    },
    {
        "kicker": "MIDDLE EAST",
        "headline": "HAMAS WEIGHS REPLY AFTER 10 KILLED IN GAZA",
        "body": (
            "Hamas weighed its response after Israeli strikes killed 10 "
            "people in Gaza, Reuters reported."
        ),
        "scene": scene_dove,
    },
]

ALSO_TODAY = [
    "BRITAIN - Migration lowest since 1997.",
    "CHESS - Gukesh draws Game 3.",
    "THAILAND - Refinery blast hurts nine.",
    "SPAIN - Tanker sinks; one dead.",
]


def rule(cv, x0, x1, y, thick=2):
    cv.fill_rect(x0, y, x1, y + thick, INK)


def build():
    cv = Canvas(W, H, PAPER)
    # outer frame
    cv.fill_rect(16, 16, 1008, 18, INK)
    cv.fill_rect(16, 1004, 1008, 1006, INK)
    cv.fill_rect(16, 16, 18, 1006, INK)
    cv.fill_rect(1006, 16, 1008, 1006, INK)

    # masthead
    cv.draw_text_centered(28, 996, 40, "THE WORLD TODAY", 7, INK)
    rule(cv, 28, 996, 100, 4)
    rule(cv, 28, 996, 107, 1)
    cv.draw_text(28, 116, "FRIDAY 27 NOVEMBER 2026", 2, INK)
    right = "THE DAY IN ONE PAGE"
    cv.draw_text(996 - text_width(right, 2), 116, right, 2, INK)
    rule(cv, 28, 996, 140, 4)
    rule(cv, 28, 996, 147, 1)

    # lead story: illustration left, text right
    ix0, iy0, iw, ih = 28, 158, 440, 380
    scene_lead_strike(cv, ix0, iy0, iw, ih)
    cv.fill_rect(ix0, iy0, ix0 + iw, iy0 + 2, INK)
    cv.fill_rect(ix0, iy0 + ih - 2, ix0 + iw, iy0 + ih, INK)
    cv.fill_rect(ix0, iy0, ix0 + 2, iy0 + ih, INK)
    cv.fill_rect(ix0 + iw - 2, iy0, ix0 + iw, iy0 + ih, INK)

    tx, tw = 488, 508
    cv.draw_text(tx, 164, "MIDDLE EAST - LEAD STORY", 2, RED)
    y = 192
    for line in wrap_text(LEAD_HEADLINE, 4, tw):
        cv.draw_text(tx, y, line, 4, INK)
        y += 34
    rule(cv, tx, tx + tw, y + 8, 2)
    y = draw_block(cv, tx, y + 20, LEAD_DECK, 2, tw, INK)
    y = draw_block(cv, tx, y + 12, LEAD_BODY, 2, tw, INK)

    # divider
    rule(cv, 28, 996, 552, 4)
    rule(cv, 28, 996, 559, 1)

    # three secondary stories
    col_x = [28, 356, 684]
    for cx0, story in zip(col_x, SECONDARIES):
        story["scene"](cv, cx0, 566, 312, 92)
        cv.fill_rect(cx0, 566, cx0 + 312, 568, INK)
        cv.fill_rect(cx0, 656, cx0 + 312, 658, INK)
        cv.fill_rect(cx0, 566, cx0 + 2, 658, INK)
        cv.fill_rect(cx0 + 310, 566, cx0 + 312, 658, INK)
        cv.draw_text(cx0, 666, story["kicker"], 2, RED)
        hy = 688
        for line in wrap_text(story["headline"], 3, 312):
            cv.draw_text(cx0, hy, line, 3, INK)
            hy += 27
        draw_block(cv, cx0, hy + 6, story["body"], 2, 312, INK)

    # divider
    rule(cv, 28, 996, 866, 4)
    rule(cv, 28, 996, 873, 1)

    # also today
    cv.draw_text(28, 884, "ALSO TODAY", 2, RED)
    rule(cv, 28, 996, 902, 1)
    item_x = [28, 272, 516, 760]
    for ax0, item in zip(item_x, ALSO_TODAY):
        draw_block(cv, ax0, 912, item, 2, 232, INK)

    # footer: sources
    footer = "SOURCES: BBC - REUTERS - THE NEW YORK TIMES - USA TODAY"
    cv.draw_text_centered(28, 996, 970, footer, 2, GREY)

    return encode_png(W, H, cv.buf)


def main():
    data = build()
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.png", "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()

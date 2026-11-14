# Generates the launcher icons (shield + keyhole) and writes them into the freshly generated android/ project.
import os
from PIL import Image, ImageDraw

BG = (15, 23, 42, 255)        # #0f172a
TOP = (96, 165, 250)          # #60a5fa
BOT = (37, 99, 235)           # #2563eb
RES = "android/app/src/main/res"

def bez(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out

# shield outline in a 100 x 100 design box
SHIELD = ([(50, 12), (82, 24), (82, 48)] + bez((82, 48), (82, 70), (68, 84), (50, 90))
          + bez((50, 90), (32, 84), (18, 70), (18, 48)) + [(18, 24)])
KEY_C = (50, 46, 8.5)                                   # keyhole circle (cx, cy, r)
KEY_P = [(45.5, 50), (54.5, 50), (57, 66), (43, 66)]     # keyhole stem

def glyph(size, scale):
    """Shield + keyhole on a transparent size x size canvas; scale = design-box size / canvas size."""
    k = 4
    S = size * k
    g = S * scale / 100.0
    ox = oy = (S - 100 * g) / 2
    T = lambda pts: [(ox + x * g, oy + y * g) for x, y in pts]
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).polygon(T(SHIELD), fill=255)
    grad = Image.new("RGBA", (S, S))
    gd = ImageDraw.Draw(grad)
    y0, y1 = oy + 12 * g, oy + 90 * g
    for y in range(S):
        t = min(max((y - y0) / (y1 - y0), 0), 1)
        gd.line([(0, y), (S, y)], fill=tuple(int(TOP[i] + (BOT[i] - TOP[i]) * t) for i in range(3)) + (255,))
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    im.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(im)
    # soft highlight on the left half
    hl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(hl).polygon(T([(50, 12), (50, 90), (32, 84)] + bez((32, 84), (30, 83), (18, 70), (18, 48)) + [(18, 24)]), fill=(255, 255, 255, 26))
    im.alpha_composite(Image.composite(hl, Image.new("RGBA", (S, S), (0, 0, 0, 0)), mask))
    cx, cy, r = KEY_C
    d.ellipse([ox + (cx - r) * g, oy + (cy - r) * g, ox + (cx + r) * g, oy + (cy + r) * g], fill=BG)
    d.polygon(T(KEY_P), fill=BG)
    return im.resize((size, size), Image.LANCZOS)

def legacy(size, round_):
    k = 4
    S = size * k
    bg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(bg)
    if round_:
        d.ellipse([0, 0, S - 1, S - 1], fill=BG)
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=S * 0.22, fill=BG)
    bg = bg.resize((size, size), Image.LANCZOS)
    bg.alpha_composite(glyph(size, 0.70))
    return bg

def foreground(size):
    return glyph(size, 0.58)    # keeps the shield inside the adaptive-icon safe zone

dens = {"mdpi": (48, 108), "hdpi": (72, 162), "xhdpi": (96, 216), "xxhdpi": (144, 324), "xxxhdpi": (192, 432)}
for name, (l, f) in dens.items():
    d = os.path.join(RES, "mipmap-" + name)
    os.makedirs(d, exist_ok=True)
    legacy(l, False).save(os.path.join(d, "ic_launcher.png"))
    legacy(l, True).save(os.path.join(d, "ic_launcher_round.png"))
    foreground(f).save(os.path.join(d, "ic_launcher_foreground.png"))

v = os.path.join(RES, "values")
os.makedirs(v, exist_ok=True)
with open(os.path.join(v, "ic_launcher_background.xml"), "w") as fh:
    fh.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#0F172A</color>\n</resources>\n')
print("icons written")

# App name shown under the icon (Myanmar)
import re
APP_NAME = "လျှို့ဝှက်သော့"
sp = os.path.join(RES, "values", "strings.xml")
if os.path.exists(sp):
    with open(sp, encoding="utf-8") as fh:
        x = fh.read()
    x = re.sub(r'(<string name="app_name">).*?(</string>)', lambda m: m.group(1) + APP_NAME + m.group(2), x)
    x = re.sub(r'(<string name="title_activity_main">).*?(</string>)', lambda m: m.group(1) + APP_NAME + m.group(2), x)
    with open(sp, "w", encoding="utf-8") as fh:
        fh.write(x)
    print("app name set:", APP_NAME)
else:
    print("strings.xml not found - app name unchanged")

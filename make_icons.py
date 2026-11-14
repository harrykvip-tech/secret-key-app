# Generates the launcher icons and writes them into the freshly generated android/ project.
import os
from PIL import Image, ImageDraw

BG = (15, 23, 42, 255)       # #0f172a
FG = (59, 130, 246, 255)     # #3b82f6
RES = "android/app/src/main/res"

def lock(size, scale):
    """Draw the lock glyph on a transparent size x size canvas; scale = glyph size / canvas size."""
    k = 4
    S = size * k
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    g = S * scale
    cx, cy = S / 2, S / 2
    bw, bh = g * 0.62, g * 0.46
    bx0, by0 = cx - bw / 2, cy - g * 0.02
    d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=g * 0.09, fill=FG)
    t = g * 0.085
    sw = g * 0.40
    top = cy - g * 0.40
    d.arc([cx - sw / 2, top, cx + sw / 2, top + sw * 1.15], 180, 360, fill=FG, width=int(t))
    d.rectangle([cx - sw / 2, top + sw * 0.575, cx - sw / 2 + t, by0 + 2], fill=FG)
    d.rectangle([cx + sw / 2 - t, top + sw * 0.575, cx + sw / 2, by0 + 2], fill=FG)
    kr = g * 0.06
    kcy = by0 + bh * 0.38
    d.ellipse([cx - kr, kcy - kr, cx + kr, kcy + kr], fill=BG)
    d.rounded_rectangle([cx - kr * 0.45, kcy, cx + kr * 0.45, kcy + g * 0.15], radius=kr * 0.4, fill=BG)
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
    bg.alpha_composite(lock(size, 0.62))
    return bg

def foreground(size):
    return lock(size, 0.40)   # keeps the glyph inside the adaptive-icon safe zone

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

"""Paint a top-down koi-pond backdrop matching the reference video."""
from PIL import Image, ImageDraw, ImageFilter
import math, random, os

W, H = 1920, 1200
CX, CY = 0.50 * W, 0.465 * H
RX, RY = 0.372 * W, 0.355 * H
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "pond-scene.png")

rng = random.Random(31)

def lerp(a, b, t):
    return a + (b - a) * t

def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def in_pond(x, y, s=1.0):
    dx = (x - CX) / (RX * s)
    dy = (y - CY) / (RY * s)
    n = math.sin(x * 0.012) * 0.06 + math.cos(y * 0.014) * 0.05
    return dx * dx + dy * dy + n < 1.0

def shade_rock(draw, x, y, r, seed):
    local = random.Random(seed)
    pts = []
    for i in range(14):
        a = i / 14 * math.tau + local.random() * 0.2
        rr = r * (0.72 + local.random() * 0.34)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.78))
    # shadow
    sp = [(p[0] + 7, p[1] + 10) for p in pts]
    draw.polygon(sp, fill=(48, 62, 40, 70))
    body = (108 + seed % 18, 114 + seed % 12, 78 + seed % 16)
    draw.polygon(pts, fill=body)
    # moss patch
    moss = [(x + local.uniform(-r * 0.4, r * 0.3), y + local.uniform(-r * 0.45, r * 0.1)) for _ in range(8)]
    if len(moss) >= 3:
        draw.polygon(moss, fill=(122, 148, 86, 180))
    # highlight
    hx, hy = x - r * 0.22, y - r * 0.28
    draw.ellipse((hx - r * 0.22, hy - r * 0.14, hx + r * 0.22, hy + r * 0.14), fill=(186, 190, 150, 90))

def canopy(draw, x, y, r, seed):
    local = random.Random(seed)
    # trunk
    draw.line((x, y + r * 0.15, x - r * 0.04, y + r * 0.95), fill=(92, 62, 48), width=max(6, int(r * 0.06)))
    for k in range(6):
        a = -1.2 + k * 0.45
        draw.line((x, y + r * 0.2, x + math.cos(a) * r * 0.55, y + math.sin(a) * r * 0.35), fill=(110, 76, 58), width=3)
    colors = [(244, 168, 196), (238, 140, 176), (252, 196, 214), (232, 120, 160), (255, 210, 222)]
    for _ in range(int(r * 1.6)):
        a = local.random() * math.tau
        rr = (local.random() ** 0.55) * r
        px = x + math.cos(a) * rr
        py = y + math.sin(a) * rr * 0.72
        rad = r * local.uniform(0.07, 0.16)
        col = colors[_ % len(colors)]
        draw.ellipse((px - rad, py - rad * 0.8, px + rad, py + rad * 0.8), fill=col)

img = Image.new("RGBA", (W, H), (186, 214, 102, 255))
px = img.load()

# grass noise
for y in range(H):
    for x in range(0, W, 2):
        n = (math.sin(x * 0.035 + y * 0.02) + math.cos(x * 0.01 - y * 0.03)) * 8
        g = 214 + int(n) + (x * 3 + y * 7) % 11
        r = 170 + (x * 5 + y) % 18
        b = 88 + (y * 3) % 16
        px[x, y] = (min(210, r), min(230, g), min(120, b), 255)
        if x + 1 < W:
            px[x + 1, y] = px[x, y]

# grass blades
d = ImageDraw.Draw(img, "RGBA")
for i in range(9000):
    x = rng.randrange(W)
    y = rng.randrange(H)
    if in_pond(x, y, 1.08):
        continue
    col = (96 + rng.randrange(50), 140 + rng.randrange(50), 50 + rng.randrange(30), 140)
    ang = rng.uniform(-0.4, 0.4)
    L = rng.uniform(6, 16)
    d.line((x, y, x + math.sin(ang) * 3, y - L), fill=col, width=1)

# sand ring then water
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
for y in range(H):
    for x in range(W):
        dx = (x - CX) / RX
        dy = (y - CY) / RY
        n = math.sin(x * 0.011) * 0.055 + math.cos(y * 0.013) * 0.045
        dist = dx * dx + dy * dy + n
        if dist < 1.18:
            t = max(0, min(255, int((1.18 - dist) / 0.18 * 255)))
            if dist < 1.0:
                t = 255
            mask.putpixel((x, y), t)

sand = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sand)
sd.ellipse((CX - RX * 1.22, CY - RY * 1.22, CX + RX * 1.22, CY + RY * 1.22), fill=(214, 196, 140, 255))
for i in range(2400):
    a = rng.random() * math.tau
    rr = rng.uniform(0.82, 1.12)
    x = CX + math.cos(a) * RX * rr
    y = CY + math.sin(a) * RY * rr
    c = (200 + rng.randrange(40), 180 + rng.randrange(30), 110 + rng.randrange(30), 160)
    sd.ellipse((x - 3, y - 2, x + 3, y + 2), fill=c)
img.paste(sand, (0, 0), mask.filter(ImageFilter.GaussianBlur(6)))

water = Image.new("RGBA", (W, H), (0, 0, 0, 0))
wp = water.load()
wmask = Image.new("L", (W, H), 0)
for y in range(H):
    for x in range(W):
        dx = (x - CX) / RX
        dy = (y - CY) / RY
        n = math.sin(x * 0.011) * 0.055 + math.cos(y * 0.013) * 0.045
        dist = dx * dx + dy * dy + n
        if dist < 1.0:
            rim = max(0.0, dist)
            deep = (26, 168, 176)
            shallow = (120, 222, 210)
            t = rim ** 0.85
            caust = 0.5 + 0.5 * math.sin(x * 0.08 + y * 0.07)
            col = (
                int(lerp(deep[0], shallow[0], t) + caust * 12),
                int(lerp(deep[1], shallow[1], t) + caust * 10),
                int(lerp(deep[2], shallow[2], t) + caust * 8),
                255,
            )
            wp[x, y] = col
            wmask.putpixel((x, y), 255)
water.putalpha(wmask.filter(ImageFilter.GaussianBlur(3)))
img = Image.alpha_composite(img.convert("RGBA"), water)
d = ImageDraw.Draw(img, "RGBA")

# in-water rocks
for spec in [(0.33, 0.40, 58, 4), (0.71, 0.58, 64, 9), (0.62, 0.33, 42, 2)]:
    shade_rock(d, spec[0] * W, spec[1] * H, spec[2], spec[3])

# rim rocks (matching video placement)
rim = [
    (0.28, 0.16, 70), (0.40, 0.12, 48), (0.52, 0.10, 56), (0.64, 0.13, 44),
    (0.78, 0.22, 62), (0.86, 0.38, 50), (0.84, 0.70, 58), (0.70, 0.84, 46),
    (0.50, 0.86, 40), (0.22, 0.78, 66), (0.14, 0.60, 52), (0.16, 0.38, 60),
    (0.20, 0.24, 48), (0.34, 0.82, 44), (0.78, 0.80, 38),
]
for i, (u, v, r) in enumerate(rim):
    shade_rock(d, u * W, v * H, r, 20 + i)

# ferns along lower bank
for i in range(90):
    x = rng.uniform(0.08, 0.92) * W
    y = rng.uniform(0.68, 0.96) * H
    if in_pond(x, y, 0.92):
        continue
    col = (40 + rng.randrange(30), 100 + rng.randrange(40), 48)
    for k in range(5):
        a = -1.4 + k * 0.55
        d.line((x, y, x + math.cos(a) * 22, y + math.sin(a) * 16 - 8), fill=col, width=2)

# cherry trees
canopy(d, 0.13 * W, 0.16 * H, 230, 1)
canopy(d, 0.90 * W, 0.42 * H, 250, 2)
canopy(d, 0.08 * W, 0.22 * H, 90, 3)

# tiny white flowers
for i in range(80):
    x = rng.uniform(0.05, 0.95) * W
    y = rng.uniform(0.05, 0.95) * H
    if in_pond(x, y, 1.05):
        continue
    d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 248, 220, 200))

img = img.convert("RGB")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print("wrote", OUT, img.size)

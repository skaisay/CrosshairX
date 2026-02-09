"""
Generate 4 wallpaper background images for CrosshairX themes.
High-quality themed backgrounds (700x900).

Themes:
  midnight — Dark blue with Windows-style glowing quadrants and light rays
  purple   — Purple pixel-art night sky, mountains, clouds, moon
  ocean    — Deep blue Win11-style abstract bloom shapes
  sakura   — Pink gradient with pixel ghost character and hearts
"""

import os
import sys
import math
import random

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "--quiet"])
    from PIL import Image, ImageDraw, ImageFilter

W, H = 700, 900
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "themes")
os.makedirs(OUT_DIR, exist_ok=True)


def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def vgrad(draw, y0, y1, c1, c2, w=W):
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        draw.line([(0, y), (w, y)], fill=lerp(c1, c2, t))


def px(draw, x, y, s, color):
    draw.rectangle([x, y, x + s - 1, y + s - 1], fill=color)


# ═════════════════════════════════════════════════════════════════
#  MIDNIGHT — Deep blue Windows-inspired, light beams from center
# ═════════════════════════════════════════════════════════════════
def gen_midnight():
    img = Image.new("RGB", (W, H), (4, 8, 24))
    draw = ImageDraw.Draw(img, "RGBA")

    # Deep blue gradient background
    vgrad(draw, 0, H, (4, 8, 28), (2, 4, 16))

    cx, cy = W // 2, int(H * 0.42)

    # Light rays radiating outward
    random.seed(42)
    for _ in range(80):
        angle = random.uniform(0, 2 * math.pi)
        length = random.randint(250, 650)
        x2 = cx + math.cos(angle) * length
        y2 = cy + math.sin(angle) * length
        alpha = random.randint(4, 18)
        w = random.randint(2, 15)
        draw.line([(cx, cy), (x2, y2)], fill=(20, 80, 220, alpha), width=w)

    # Concentric glow
    for r in range(350, 0, -2):
        a = max(1, int(18 * (1 - r / 350)))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(15, 60, 180, a))
    for r in range(150, 0, -2):
        a = max(1, int(25 * (1 - r / 150)))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(30, 100, 255, a))

    # Windows 10 logo — 4 blue quadrants
    gap = 8
    sz = 60
    ox, oy = cx - sz - gap // 2, cy - sz - gap // 2
    for dy in [0, sz + gap]:
        for dx in [0, sz + gap]:
            x1, y1 = ox + dx, oy + dy
            # Each pane is a gradient
            for row in range(sz):
                t = row / sz
                c = lerp((25, 90, 230), (18, 65, 190), t)
                draw.line([(x1, y1 + row), (x1 + sz, y1 + row)], fill=(*c, 55))
            # Border glow
            for i in range(6):
                draw.rectangle([x1+i, y1+i, x1+sz-i, y1+sz-i],
                              outline=(40, 120, 255, max(1, 25 - i * 4)))

    # Scattered stars
    random.seed(123)
    for _ in range(200):
        x = random.randint(0, W)
        y = random.randint(0, H)
        brightness = random.randint(60, 200)
        s = random.choice([1, 1, 1, 2])
        draw.ellipse([x, y, x+s, y+s], fill=(brightness, brightness + 20, 255, random.randint(40, 150)))

    # Bottom glow
    for y in range(H - 200, H):
        t = (y - (H - 200)) / 200
        draw.line([(0, y), (W, y)], fill=(8, 30, 90, int(t * 30)))

    img = img.filter(ImageFilter.GaussianBlur(1.2))
    img.save(os.path.join(OUT_DIR, "midnight.png"), "PNG")
    print("  -> midnight.png")


# ═════════════════════════════════════════════════════════════════
#  PURPLE — Pixel art purple night: mountains, moon, clouds, stars
# ═════════════════════════════════════════════════════════════════
def gen_purple():
    img = Image.new("RGB", (W, H), (45, 30, 80))
    draw = ImageDraw.Draw(img, "RGBA")

    # Sky gradient: deep purple top → lighter purple bottom
    vgrad(draw, 0, int(H * 0.55), (25, 12, 55), (70, 45, 110))
    vgrad(draw, int(H * 0.55), H, (70, 45, 110), (35, 20, 65))

    PS = 6  # pixel size for pixel-art look

    # Stars (scattered pixelated)
    random.seed(77)
    for _ in range(150):
        x = random.randint(0, W // PS) * PS
        y = random.randint(0, int(H * 0.5) // PS) * PS
        s = PS if random.random() < 0.7 else PS * 2
        bright = random.randint(140, 255)
        px(draw, x, y, s, (bright, bright, min(255, bright + 40), random.randint(60, 200)))

    # Moon (large, upper right)
    mx, my, mr = W - 140, 110, 55
    # Glow
    for r in range(mr + 60, 0, -2):
        a = max(1, int(20 * (1 - r / (mr + 60))))
        draw.ellipse([mx-r, my-r, mx+r, my+r], fill=(180, 160, 225, a))
    # Moon body (pixel art — draw as pixelated circle)
    for dy in range(-mr, mr + 1, PS):
        for dx in range(-mr, mr + 1, PS):
            if dx*dx + dy*dy <= mr*mr:
                b = 200 + random.randint(-10, 10)
                px(draw, mx + dx, my + dy, PS, (b, b, min(255, b + 20)))

    # Mountains (3 layers, front darker)
    mountain_layers = [
        # (y_base, height_range, color_dark, color_light, seed)
        (int(H * 0.55), 180, (50, 30, 75), (65, 40, 95), 10),
        (int(H * 0.62), 140, (35, 20, 55), (50, 30, 75), 20),
        (int(H * 0.70), 100, (22, 12, 40), (35, 20, 55), 30),
    ]
    for y_base, h_range, c_dark, c_light, seed in mountain_layers:
        random.seed(seed)
        heights = []
        for i in range(W // PS + 2):
            heights.append(random.randint(30, h_range))
        # Smooth
        for _ in range(4):
            heights = [(heights[max(0,i-1)] + heights[i] + heights[min(len(heights)-1,i+1)]) // 3
                       for i in range(len(heights))]
        for i, h in enumerate(heights):
            x = i * PS
            peak_y = y_base - h
            for y in range(peak_y, H, PS):
                t = min(1.0, (y - peak_y) / max(1, H - peak_y))
                c = lerp(c_light, c_dark, t)
                px(draw, x, y, PS, c)

    # Pixel clouds
    random.seed(55)
    cloud_data = [(100, int(H*0.25), 30), (350, int(H*0.18), 40), (550, int(H*0.30), 25)]
    for ccx, ccy, count in cloud_data:
        for _ in range(count):
            ox = ccx + random.randint(-60, 60)
            oy = ccy + random.randint(-12, 12)
            s = PS * random.randint(1, 4)
            a = random.randint(40, 100)
            px(draw, ox, oy, s, (160, 130, 200, a))

    img.save(os.path.join(OUT_DIR, "purple.png"), "PNG")
    print("  -> purple.png")


# ═════════════════════════════════════════════════════════════════
#  OCEAN — Win11 deep blue abstract bloom / petal shapes
# ═════════════════════════════════════════════════════════════════
def gen_ocean():
    img = Image.new("RGB", (W, H), (6, 18, 50))
    draw = ImageDraw.Draw(img, "RGBA")

    # Background gradient
    vgrad(draw, 0, H, (4, 14, 45), (8, 25, 60))

    # Win11-style large abstract bloom petals
    bloom_shapes = [
        # (cx, cy, rx, ry, rotation, color)
        (W * 0.35, H * 0.3, 200, 280, -20, (20, 80, 200)),
        (W * 0.65, H * 0.45, 180, 250, 15, (25, 100, 230)),
        (W * 0.5, H * 0.7, 220, 200, -10, (15, 65, 180)),
        (W * 0.25, H * 0.6, 150, 200, 30, (18, 75, 190)),
        (W * 0.75, H * 0.25, 160, 220, -25, (30, 110, 240)),
    ]

    for bcx, bcy, rx, ry, rot, base_c in bloom_shapes:
        # Draw as concentric ellipses with rotation
        for r_factor in range(100, 0, -2):
            f = r_factor / 100.0
            a = max(1, int(12 * (1 - f)))
            crx = int(rx * f)
            cry = int(ry * f)
            c = tuple(min(255, int(v * (0.8 + 0.4 * (1 - f)))) for v in base_c)
            # Create a temporary image, draw ellipse, rotate, composite
            if crx > 2 and cry > 2:
                draw.ellipse([bcx - crx, bcy - cry, bcx + crx, bcy + cry],
                            fill=(*c, a))

    # Inner bright glow in center
    for r in range(200, 0, -2):
        a = max(1, int(15 * (1 - r / 200)))
        draw.ellipse([W*0.5-r, H*0.45-r, W*0.5+r, H*0.45+r],
                    fill=(30, 120, 255, a))

    # Light streaks
    random.seed(11)
    for _ in range(30):
        x1 = random.randint(0, W)
        y1 = random.randint(0, H)
        angle = random.uniform(0, 2 * math.pi)
        length = random.randint(100, 400)
        x2 = x1 + math.cos(angle) * length
        y2 = y1 + math.sin(angle) * length
        draw.line([(x1, y1), (x2, y2)],
                  fill=(30, 100, 240, random.randint(3, 12)),
                  width=random.randint(1, 6))

    # Sparkles
    for _ in range(100):
        x = random.randint(0, W)
        y = random.randint(0, H)
        s = random.choice([1, 2, 3])
        draw.ellipse([x, y, x+s, y+s],
                    fill=(80, 180, 255, random.randint(30, 100)))

    img = img.filter(ImageFilter.GaussianBlur(2.5))
    img.save(os.path.join(OUT_DIR, "ocean.png"), "PNG")
    print("  -> ocean.png")


# ═════════════════════════════════════════════════════════════════
#  SAKURA — Pink with pixel ghost character, hearts, sparkles
# ═════════════════════════════════════════════════════════════════
def gen_sakura():
    img = Image.new("RGB", (W, H), (255, 185, 210))
    draw = ImageDraw.Draw(img, "RGBA")

    # Pink gradient
    vgrad(draw, 0, H, (255, 200, 220), (245, 170, 200))

    PS = 8

    # Pixel ghost character (center of image)
    gx = W // 2 - 6 * PS
    gy = H // 2 - 7 * PS

    # Ghost sprite (12 wide x 13 tall)
    ghost = [
        "    XXXX    ",
        "   XXXXXX   ",
        "  XXXXXXXX  ",
        " XXXXXXXXXX ",
        " XX  XX  XX ",
        " XX  XX  XX ",
        " XXXXXXXXXX ",
        " XX XXXX XX ",
        " XXXXXXXXXX ",
        " XXXXXXXXXX ",
        " XXXXXXXXXX ",
        " X XX  XX X ",
        "  X  XX  X  ",
    ]
    ghost_body = (255, 245, 250)
    ghost_eye = (25, 15, 25)
    cheek_color = (255, 160, 180)

    for ri, row in enumerate(ghost):
        for ci, ch in enumerate(row):
            ppx = gx + ci * PS
            ppy = gy + ri * PS
            if ch == 'X':
                px(draw, ppx, ppy, PS, ghost_body)

    # Eyes (row 4-5, columns 2-3 and 7-8 within ghost)
    for r in [4, 5]:
        for c in [2, 3, 7, 8]:
            pxx = gx + c * PS
            pyy = gy + r * PS
            px(draw, pxx, pyy, PS, ghost_eye)

    # Cheeks (blush)
    px(draw, gx + 1 * PS, gy + 6 * PS, PS, cheek_color)
    px(draw, gx + 10 * PS, gy + 6 * PS, PS, cheek_color)

    # Shadow under ghost
    shadow_y = gy + 13 * PS + 6
    draw.ellipse([gx + PS, shadow_y, gx + 11 * PS, shadow_y + 14],
                fill=(230, 140, 170, 80))

    # Pixel hearts scattered around
    random.seed(33)
    heart_positions = [
        (80, 120), (550, 100), (120, 700), (530, 650),
        (60, 400), (600, 350), (300, 100), (400, 780),
        (200, 500), (500, 200),
    ]
    for hx, hy in heart_positions:
        s = PS
        c = (255, random.randint(70, 140), random.randint(120, 180))
        # Heart shape made of pixel blocks
        #  X X
        # XXXXX
        #  XXX
        #   X
        px(draw, hx, hy, s, c)
        px(draw, hx + 2*s, hy, s, c)
        px(draw, hx - s//2, hy + s, s * 3 + s, c)  # wide middle
        px(draw, hx, hy + 2*s, s * 2 + s, c)
        px(draw, hx + s//2, hy + 3*s, s + s, c)

    # Sparkle effect — small white/yellow pixel dots
    sparkle_positions = [
        (110, 130), (560, 90), (140, 690), (540, 640),
        (320, 110), (80, 410), (610, 340), (350, 760),
    ]
    for sx, sy in sparkle_positions:
        for dd in [(0, -PS), (0, PS), (-PS, 0), (PS, 0)]:
            px(draw, sx + dd[0], sy + dd[1], PS // 2, (255, 255, 220, 200))
        px(draw, sx, sy, PS // 2, (255, 255, 255, 255))

    # Floating petals
    random.seed(88)
    for _ in range(30):
        fx = random.randint(0, W)
        fy = random.randint(0, H)
        fs = random.randint(4, 8)
        draw.ellipse([fx, fy, fx + fs, fy + fs * 2],
                    fill=(255, random.randint(170, 220), random.randint(190, 230), random.randint(60, 140)))

    img.save(os.path.join(OUT_DIR, "sakura.png"), "PNG")
    print("  -> sakura.png")


if __name__ == "__main__":
    print("Generating CrosshairX wallpapers (700x900)...")
    gen_midnight()
    gen_purple()
    gen_ocean()
    gen_sakura()
    print(f"\nDone! Saved to {OUT_DIR}")
    print("Tip: Replace any image with your own, keeping the same filename.")

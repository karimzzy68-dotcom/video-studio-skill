"""Renders a looping Halloween overlay (bats, sparkles, ember glow) as RGBA frames piped into ffmpeg."""
import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 540, 960, 30
SECONDS = float(sys.argv[2]) if len(sys.argv) > 2 else 21
out = sys.argv[1]
random.seed(7)

def bat(size, flap):
    im = Image.new("RGBA", (size * 2, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = size, size // 2
    w = 1 - 0.55 * abs(math.sin(flap))
    for s in (-1, 1):
        pts = [(cx, cy), (cx + s * size * 0.35, cy - size * 0.38 * w), (cx + s * size * 0.55, cy - size * 0.2 * w),
               (cx + s * size * 0.75, cy - size * 0.32 * w), (cx + s * size * 0.95, cy + size * 0.12),
               (cx + s * size * 0.65, cy + size * 0.02), (cx + s * size * 0.45, cy + size * 0.18),
               (cx + s * size * 0.2, cy + size * 0.06)]
        d.polygon(pts, fill=(12, 6, 18, 235))
    d.ellipse((cx - size * 0.1, cy - size * 0.14, cx + size * 0.1, cy + size * 0.2), fill=(12, 6, 18, 240))
    d.polygon([(cx - size * 0.09, cy - size * 0.1), (cx - size * 0.06, cy - size * 0.24), (cx - size * 0.01, cy - size * 0.12)], fill=(12, 6, 18, 240))
    d.polygon([(cx + size * 0.09, cy - size * 0.1), (cx + size * 0.06, cy - size * 0.24), (cx + size * 0.01, cy - size * 0.12)], fill=(12, 6, 18, 240))
    return im

bats = [dict(y=random.uniform(50, 170), speed=random.uniform(70, 130) * random.choice((1, -1)),
             x0=random.uniform(0, W), size=random.choice((36, 46, 58)), phase=random.uniform(0, 6),
             bob=random.uniform(10, 28)) for _ in range(4)]
sparks = [dict(x=random.uniform(0, W), y=random.uniform(0, H), r=random.uniform(1.5, 4.2),
               drift=random.uniform(-14, 14), rise=random.uniform(12, 40), tw=random.uniform(0, 6),
               col=random.choice(((255, 150, 40), (255, 205, 90), (190, 110, 255), (255, 120, 170)))) for _ in range(38)]

# static soft ember glow at the edges (orange bottom, violet top), baked once
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for i in range(120):
    a = int(70 * (1 - i / 120) ** 2)
    gd.rectangle((0, H - i * 3, W, H - i * 3 + 3), fill=(255, 110, 20, a))
    gd.rectangle((0, i * 2, W, i * 2 + 2), fill=(120, 40, 190, int(a * 0.8)))
glow = glow.filter(ImageFilter.GaussianBlur(10))

ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-vf", "scale=1080:1920:flags=bicubic,format=argb",
                       "-c:v", "qtrle", out], stdin=subprocess.PIPE)
n = int(SECONDS * FPS)
for f in range(n):
    t = f / FPS
    fr = glow.copy()
    sp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sp)
    for s in sparks:
        x = (s["x"] + s["drift"] * t + 8 * math.sin(t * 1.3 + s["tw"])) % W
        y = (s["y"] - s["rise"] * t) % H
        tw = 0.35 + 0.65 * abs(math.sin(t * 2.2 + s["tw"]))
        r = s["r"] * (0.6 + tw)
        c = s["col"]
        sd.ellipse((x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2), fill=c + (int(55 * tw),))
        sd.ellipse((x - r, y - r, x + r, y + r), fill=c + (int(230 * tw),))
        if s["r"] > 3.2:  # 4-point star glints on the bigger ones
            L = r * 4.5
            sd.line((x - L, y, x + L, y), fill=(255, 235, 200, int(160 * tw)), width=1)
            sd.line((x, y - L, x, y + L), fill=(255, 235, 200, int(160 * tw)), width=1)
    fr = Image.alpha_composite(fr, sp)
    for b in bats:
        x = (b["x0"] + b["speed"] * t) % (W + 240) - 120
        y = b["y"] + b["bob"] * math.sin(t * 2 + b["phase"])
        im = bat(b["size"], t * 9 + b["phase"])
        if b["speed"] < 0:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        fr.paste(im, (int(x - im.width / 2), int(y - im.height / 2)), im)
    ff.stdin.write(fr.tobytes())
ff.stdin.close()
ff.wait()
print("overlay done", out)

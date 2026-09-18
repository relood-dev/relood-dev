from PIL import Image, ImageDraw, ImageFont
import random

W, H  = 980, 1120
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY  = (125, 125, 125)
DARK  = (48, 48, 48)
FONT  = "lanapixel.ttf"

img = Image.new("RGB", (W, H), BLACK)
d   = ImageDraw.Draw(img)
_fc = {}


JP = "/System/Library/Fonts/Hiragino Sans GB.ttc"   # LanaPixel n'a pas les kana


def _f(size, path=None):
    key = (size, path or FONT)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(path or FONT, size)
    return _fc[key]


def render(s, size, fill, track=0, font=None):
    """Rend du texte en masque binaire, recadre au pixel pres, avec interlettrage."""
    f = _f(size, font)
    pad = size * 3
    m = Image.new("L", (len(s) * size + pad * 2, size * 3), 0)
    dm = ImageDraw.Draw(m)
    if track:
        x = pad
        for ch in s:
            dm.text((x, pad // 2), ch, font=f, fill=255)
            x += dm.textlength(ch, font=f) + track
    else:
        dm.text((pad, pad // 2), s, font=f, fill=255)
    m = m.point(lambda v: 255 if v > 110 else 0)
    b = m.getbbox()
    if not b:
        return None
    m = m.crop(b)                                  # recadrage serre
    return Image.new("RGB", m.size, fill), m


def text(xy, s, size=26, fill=WHITE, track=0, right=False, center=None, font=None):
    r = render(s, size, fill, track, font)
    if not r:
        return 0
    layer, mask = r
    x = center - mask.width // 2 if center is not None else (xy[0] - mask.width if right else xy[0])
    img.paste(layer, (x, xy[1]), mask)
    return mask.width


def ticks(x0, y0, x1, y1, n=20):
    for cx, cy, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx, cy), (cx + dx * n, cy)], fill=WHITE, width=3)
        d.line([(cx, cy), (cx, cy + dy * n)], fill=WHITE, width=3)


d.rectangle([26, 26, W - 26, H - 26], outline=DARK, width=2)
FR = (46, 46, W - 46, H - 46)
d.rectangle(FR, outline=WHITE, width=2)
ticks(*FR)
L, R = 72, W - 72

# ---------- bandeau ----------
text((L, 74), ">RELOOD_ID_CARD", 26, WHITE, track=1)
bx, by = R - 96, 72
d.rectangle([bx, by, bx + 72, by + 30], outline=WHITE, width=3)
d.rectangle([bx + 72, by + 9, bx + 79, by + 21], fill=WHITE)
for i in range(4):
    d.rectangle([bx + 8 + i * 16, by + 8, bx + 19 + i * 16, by + 22], fill=WHITE)
text((bx - 22, 76), "LVL 20", 22, GREY, track=1, right=True)
d.line([(L, 126), (R, 126)], fill=WHITE, width=2)

# ---------- identite ----------
BIN = " ".join(format(ord(c), "08b") for c in "RELOOD")   # encode vraiment le nom
text((L, 146), BIN, 20, GREY, track=1)
text((L, 186), "RELOOD", 72, WHITE, track=5)
# --- blocs de corruption facon glitch ---
random.seed(23)
gx = R
for _ in range(14):
    w = random.choice((4, 6, 9, 14))
    h = random.choice((4, 7, 11))
    gx -= w + random.choice((3, 4, 6))
    d.rectangle([gx, 146 + (14 - h) // 2, gx + w, 146 + (14 - h) // 2 + h],
                fill=random.choice((GREY, GREY, DARK, WHITE)))
text((R, 190), "ACCESS ******", 26, WHITE, track=1, right=True)
d.line([(L, 268), (R, 268)], fill=WHITE, width=2)

# ---------- panneau gauche : portrait ASCII ----------
P = (L, 292, 448, 664)
d.rectangle(P, outline=WHITE, width=2)

from PIL import ImageOps, ImageEnhance
CW, CH = 5, 7                                   # grille imposee (police non monospace)
IX0, IY0 = P[0] + 5, P[1] + 5
COLS = (P[2] - P[0] - 10) // CW
ROWS = (P[3] - P[1] - 48) // CH
RAMP = " .,:;i1tfLCG08@"

photo = Image.open("avatar.jpg").convert("L").crop((150, 0, 460, 400))
photo = photo.resize((COLS, ROWS), Image.LANCZOS)
photo = ImageOps.autocontrast(photo, cutoff=2)
photo = ImageEnhance.Contrast(photo).enhance(1.25)
ppx = photo.load()

fasc = _f(11)
for ry in range(ROWS):
    for rx in range(COLS):
        ch = RAMP[min(len(RAMP) - 1, ppx[rx, ry] * len(RAMP) // 256)]
        if ch == " ":
            continue
        m = Image.new("L", (CW + 6, CH + 8), 0)
        ImageDraw.Draw(m).text((0, 0), ch, font=fasc, fill=255)
        m = m.point(lambda v: 255 if v > 110 else 0)
        b = m.getbbox()
        if not b:
            continue
        m = m.crop(b)
        img.paste(Image.new("RGB", m.size, WHITE), (IX0 + rx * CW, IY0 + ry * CH), m)

# --- reticule facon lunette ---
rcx, rcy = (P[0] + P[2]) // 2, (P[1] + P[3]) // 2 - 16
GAP, ARM = 16, 46
for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    d.line([(rcx + dx * GAP, rcy + dy * GAP),
            (rcx + dx * (GAP + ARM), rcy + dy * (GAP + ARM))], fill=WHITE, width=3)
d.ellipse([rcx - 4, rcy - 4, rcx + 4, rcy + 4], fill=WHITE)
d.ellipse([rcx - 84, rcy - 84, rcx + 84, rcy + 84], outline=WHITE, width=2)
for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):          # crochets d'accroche
    bx, by, n = rcx + sx * 116, rcy + sy * 116, 22
    d.line([(bx, by), (bx - sx * n, by)], fill=WHITE, width=3)
    d.line([(bx, by), (bx, by - sy * n)], fill=WHITE, width=3)

d.rectangle([P[0] + 3, P[3] - 42, P[2] - 3, P[3] - 3], fill=BLACK)
text((P[0] + 16, P[3] - 34), ">TARGET_LOCKED", 22, GREY, track=1)

# ---------- panneau droit : attributs ----------
d.line([(472, 292), (472, 664)], fill=WHITE, width=2)
AX = 500
text((0, 312), "ATTRIBUTES", 26, WHITE, track=3, center=(AX + R) // 2)
ATTRS = [("AIM", 9), ("REFLEX", 8), ("SYSTEMS", 9), ("CREATIVITY", 10), ("CODE", 3)]
BX0, SEG, GAP = 676, 21, 4
for i, (name, val) in enumerate(ATTRS):
    y = 386 + i * 56
    text((AX, y + 2), name, 24, WHITE, track=1)
    for s in range(10):
        x = BX0 + s * (SEG + GAP)
        box = [x, y, x + SEG, y + 26]
        d.rectangle(box, fill=WHITE) if s < val else d.rectangle(box, outline=DARK, width=2)
d.line([(L, 688), (R, 688)], fill=WHITE, width=2)

# ---------- bio ----------
text((L, 706), ">BIO:", 26, WHITE, track=1)
BIO = [("SYSTEMS AND NETWORKS TECHNICIAN (TSSR). PASSIONATE ABOUT", WHITE),
       ("IT AND VIDEO GAMES. I DABBLE IN A LOT OF THINGS, AND WHAT", WHITE),
       ("ALWAYS COMES BACK IS THE URGE TO CREATE.", WHITE),
       ("", WHITE),
       ("I NEVER HAD THE CHANCE TO LEARN HOW TO CODE, SO I BUILD", WHITE),
       ("WITH AI. IT LETS ME BRING MY IDEAS TO LIFE AND HAVE FUN", WHITE),
       ("DOING IT. BUT I FULLY INTEND TO LEARN PROPERLY.", WHITE),
       ("", WHITE),
       ("PS: HUGE RESPECT FOR THOSE WHO ALREADY KNOW HOW_", GREY)]
for i, (line, col) in enumerate(BIO):
    if line:
        text((L, 744 + i * 27), line, 24, col, track=2)
d.line([(L, H - 128), (R, H - 128)], fill=WHITE, width=2)

# ---------- pied ----------
text((0, H - 100), ">FRANCE", 24, WHITE, track=2, center=W // 2)
for sx in (L + 4, R - 60):
    d.rectangle([sx, H - 108, sx + 56, H - 64], outline=WHITE, width=2)
    d.line([(sx, H - 108), (sx + 28, H - 92)], fill=WHITE, width=2)
    d.line([(sx + 56, H - 108), (sx + 28, H - 92)], fill=WHITE, width=2)
    d.line([(sx + 28, H - 92), (sx + 28, H - 64)], fill=WHITE, width=2)

img.save("card-v2.png")
print(f"card-v2.png  {img.width}x{img.height}")

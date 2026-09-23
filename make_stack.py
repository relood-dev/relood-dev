from PIL import Image, ImageDraw, ImageFont
import re

W       = 980
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
GREY    = (188, 188, 188)     # mots-cles
DIM     = (118, 118, 118)     # commentaires
PUNCT   = (105, 105, 105)     # ponctuation
NUM     = (72, 72, 72)        # numeros de ligne
DARK    = (48, 48, 48)
FONT    = "lanapixel.ttf"
SIZE    = 24
CELL    = 10          # chasse imposee : LanaPixel n'est pas monospace
LH      = 29          # interligne

_fc = {}
def _f(size):
    if size not in _fc:
        _fc[size] = ImageFont.truetype(FONT, size)
    return _fc[size]


KEYWORDS = {"public", "class", "static", "string", "int", "bool", "void", "new", "partial"}

def tokenize(line):
    if line.strip().startswith("//"):
        return [(line, DIM)]
    out, i = [], 0
    for m in re.finditer(r'"[^"]*"|\b[A-Za-z_][A-Za-z0-9_]*\b|[^\sA-Za-z0-9_"]+|\s+', line):
        tok = m.group(0)
        if tok.startswith('"'):
            col = WHITE
        elif tok in KEYWORDS:
            col = GREY
        elif re.fullmatch(r'[A-Z][A-Z0-9_]*', tok):
            col = WHITE
        elif re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', tok):
            col = GREY
        elif tok.strip() == "":
            col = PUNCT
        else:
            col = PUNCT
        out.append((tok, col))
    return out


def make(games, out_path="stack-v1.png"):
    CODE = [
        "/// <summary>",
        "/// Systems and networks technician.",
        "/// Learning to code, building with AI meanwhile.",
        "/// </summary>",
        "",
        "public class RELOOD",
        "{",
        '    public string[] TOOLS = {',
        '        "Proxmox", "VMware", "VS Code",',
        '        "Ansible", "Claude"',
        "    };",
        "",
        "    public string[] LEARNING = {",
        '        "Python", "Bash", "PowerShell",',
        '        "JavaScript"',
        "    };",
        "",
        "    public string[] GAMES = {",
    ]
    for chunk in games:
        CODE.append(f'        {chunk}')
    CODE += [
        "    };",
        "}",
        "",
        "public static class HARDWARE",
        "{",
        '    public string DESKTOP = "Ryzen 7 5700X @ 4.8 GHz";',
        '    public string     GPU = "RTX 3060 12 GB / 32 GB DDR4";',
        '    public string  LAPTOP = "MacBook Air M4 / 16 GB";',
        '    public string  BACKUP = "ThinkPad T480 / i7-8650U";',
        "",
        '    public string[] OS = { "macOS", "Windows", "Linux" };',
        "}",
        "",
        "public static class CONTACT",
        "{",
        '    public string DISCORD = "bekindorfail";',
        '    public string  GITHUB = "relood-dev";',
        "}",
    ]

    top, bot = 118, 96
    H = top + len(CODE) * LH + bot
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    def glyph(ch, col, x, y):
        if ch == " ":
            return
        m = Image.new("L", (SIZE + 10, SIZE + 12), 0)
        ImageDraw.Draw(m).text((0, 0), ch, font=_f(SIZE), fill=255)
        m = m.point(lambda v: 255 if v > 110 else 0)
        b = m.getbbox()
        if not b:
            return
        m = m.crop((b[0], 0, b[2], m.height))          # recadrage horizontal seul
        img.paste(Image.new("RGB", m.size, col),
                  (x + max(0, (CELL - m.width) // 2), y), m)   # centre dans la cellule

    def label(xy, s, size, col, track=0, right=False, center=None):
        f = _f(size)
        m = Image.new("L", (len(s) * size + 80, size * 3), 0)
        dm = ImageDraw.Draw(m)
        if track:
            x = 40
            for ch in s:
                dm.text((x, size // 2), ch, font=f, fill=255)
                x += dm.textlength(ch, font=f) + track
        else:
            dm.text((40, size // 2), s, font=f, fill=255)
        m = m.point(lambda v: 255 if v > 110 else 0)
        b = m.getbbox()
        if not b:
            return 0
        m = m.crop(b)
        px = center - m.width // 2 if center is not None else (xy[0] - m.width if right else xy[0])
        img.paste(Image.new("RGB", m.size, col), (px, xy[1]), m)
        return m.width

    # --- cadre identique a la premiere carte ---
    d.rectangle([26, 26, W - 26, H - 26], outline=DARK, width=2)
    FR = (46, 46, W - 46, H - 46)
    d.rectangle(FR, outline=WHITE, width=2)
    for cx, cy, dx, dy in ((FR[0], FR[1], 1, 1), (FR[2], FR[1], -1, 1),
                           (FR[0], FR[3], 1, -1), (FR[2], FR[3], -1, -1)):
        d.line([(cx, cy), (cx + dx * 20, cy)], fill=WHITE, width=3)
        d.line([(cx, cy), (cx, cy + dy * 20)], fill=WHITE, width=3)

    L, R = 72, W - 72
    label((L, 74), ">RELOOD_STACK", 26, WHITE, track=1)
    label((R, 78), "READ ONLY", 22, GREY, track=1, right=True)
    d.line([(L, 112), (R, 112)], fill=WHITE, width=2)

    # --- le code ---
    for row, line in enumerate(CODE):
        y = top + row * LH
        label((L + 22, y + 4), f"{row + 1:>2}", 20, NUM, right=True)
        col_x = 0
        for tok, col in tokenize(line):
            for ch in tok:
                glyph(ch, col, L + 40 + col_x * CELL, y)
                col_x += 1

    d.line([(L + 30, top - 6), (L + 30, H - 86)], fill=DARK, width=2)
    d.line([(L, H - 74), (R, H - 74)], fill=WHITE, width=2)
    label((0, H - 62), ">END_OF_FILE", 22, GREY, track=2, center=W // 2)

    img.save(out_path)
    print(f"{out_path}  {img.width}x{img.height}  ({len(CODE)} lignes)")


if __name__ == "__main__":
    make([
        '"KovaaK\'s", "Valorant", "Counter-Strike 2",',
        '"Rainbow Six Siege", "Overwatch", "Apex Legends"',
    ])

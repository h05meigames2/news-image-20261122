#!/usr/bin/env python3
"""Render the 22 November 2026 world-news front page (1024x1024 PNG).

Original editorial illustration drawn procedurally with Pillow: no photos,
no copied artwork. Every story is a real event first reported on
22 November 2026 (a few dated 21 Nov where noted). Deterministic: fixed
layout, fixed palette, no randomness, no clock, no network.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))

NAVY = (13, 27, 62)
NAVY2 = (24, 44, 92)
GOLD = (212, 175, 55)
PAPER = (250, 247, 240)
INK = (18, 18, 18)
GREY = (90, 90, 90)
RED = (178, 34, 34)
TEAL = (0, 128, 128)
WHITE = (255, 255, 255)
BORDER = (200, 195, 185)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


F_TITLE = lambda s: font("DejaVuSans-Bold.ttf", s)
F_BODY = lambda s: font("DejaVuSans.ttf", s)
F_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, fnt_name, size, max_w, min_size=10):
    """Shrink font until text fits max_w; return (font, text)."""
    s = size
    while s > min_size:
        f = font(fnt_name, s)
        if draw.textlength(text, font=f) <= max_w:
            return f, text
        s -= 1
    return font(fnt_name, min_size), text


def draw_tag(draw, x, y, label, color):
    f = F_BOLD(13)
    tw = draw.textlength(label, font=f)
    pad = 7
    draw.rounded_rectangle([x, y, x + tw + 2 * pad, y + 20], radius=4, fill=color)
    draw.text((x + pad, y + 3), label, font=f, fill=WHITE)
    return tw + 2 * pad + 8


# ---------------------------------------------------------------- scenes
def scene_gulf(draw, x, y, w, h):
    """Gulf at night: dark sea, Bahrain island, missile arcs, bursts."""
    draw.rectangle([x, y, x + w, y + h], fill=(16, 32, 64))
    for i in range(5):
        yy = y + 8 + i * (h // 5)
        draw.line([(x, yy), (x + w, yy)], fill=(28, 52, 96), width=1)
    # island
    draw.ellipse([x + w // 2 - 26, y + h - 46, x + w // 2 + 26, y + h - 6],
                 fill=(212, 175, 55))
    draw.ellipse([x + w // 2 - 14, y + h - 38, x + w // 2 + 14, y + h - 14],
                 fill=(150, 120, 40))
    # missile arcs (low, flat trajectories)
    for sx, ex, peak in [(x + 20, x + w // 2 - 10, y + h // 2),
                         (x + w - 20, x + w // 2 + 10, y + h // 2 + 6)]:
        pts = []
        for t in range(21):
            tt = t / 20.0
            px = sx + (ex - sx) * tt
            py = y + h - 10 + (peak - (y + h - 10)) * (1 - (2 * tt - 1) ** 2)
            pts.append((px, py))
        draw.line(pts, fill=(255, 200, 80), width=2)
    # bursts
    for cx, cy in [(x + w // 2 - 8, y + h - 30), (x + w // 2 + 16, y + h - 22)]:
        for r, c in [(12, (255, 120, 40)), (7, (255, 220, 120))]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)


def scene_mountains(draw, x, y, w, h, sky, rock, snow=True):
    draw.rectangle([x, y, x + w, y + h], fill=sky)
    draw.ellipse([x + w - 34, y + 8, x + w - 10, y + 32], fill=(255, 240, 180))
    pts = [(x, y + h), (x + w * 0.25, y + h * 0.25), (x + w * 0.45, y + h * 0.7),
           (x + w * 0.65, y + h * 0.2), (x + w * 0.85, y + h * 0.6),
           (x + w, y + h * 0.45), (x + w, y + h)]
    draw.polygon(pts, fill=rock)
    if snow:
        for px, py in [(x + w * 0.25, y + h * 0.25), (x + w * 0.65, y + h * 0.2)]:
            draw.polygon([(px - 14, py + 16), (px, py), (px + 14, py + 16)],
                         fill=WHITE)


def scene_flags3(draw, x, y, w, h):
    """Three simplified flags on poles: US, China, Russia."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 236, 242))
    flags = [((178, 34, 52), (255, 255, 255), "us"),
             ((222, 41, 16), (255, 222, 0), "cn"),
             ((255, 255, 255), (0, 57, 166), "ru")]
    fw, fh = w // 4, h // 2
    for i, (c1, c2, _) in enumerate(flags):
        fx = x + 12 + i * (fw + 10)
        fy = y + h // 2 - fh // 2
        draw.rectangle([fx, fy, fx + fw, fy + fh], fill=c1, outline=(120, 120, 120))
        draw.rectangle([fx, fy + fh // 3, fx + fw, fy + 2 * fh // 3], fill=c2)
        draw.line([(fx + fw // 2, fy + fh), (fx + fw // 2, y + h - 4)],
                  fill=(80, 80, 80), width=2)


def scene_chart(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(245, 240, 235))
    for i in range(4):
        yy = y + 10 + i * (h - 20) // 3
        draw.line([(x + 6, yy), (x + w - 6, yy)], fill=(220, 215, 205), width=1)
    pts = []
    vals = [0.15, 0.25, 0.2, 0.45, 0.4, 0.65, 0.6, 0.85]
    for i, v in enumerate(vals):
        pts.append((x + 8 + i * (w - 16) / 7, y + 10 + v * (h - 20)))
    draw.line(pts, fill=RED, width=3)
    draw.polygon(pts + [(pts[-1][0], y + h - 4), (pts[0][0], y + h - 4)],
                 fill=(178, 34, 34, 40))
    draw.text((x + 8, y + 4), "-2.4%", font=F_BOLD(15), fill=RED)


def scene_shield(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(18, 32, 58))
    cx, cy = x + w // 2, y + h // 2 - 4
    draw.polygon([(cx - 26, cy - 18), (cx + 26, cy - 18), (cx + 26, cy + 6),
                  (cx, cy + 26), (cx - 26, cy + 6)], fill=(212, 175, 55))
    draw.polygon([(cx - 20, cy - 13), (cx + 20, cy - 13), (cx + 20, cy + 4),
                  (cx, cy + 20), (cx - 20, cy + 4)], fill=NAVY)
    draw.text((cx - 16, cy - 12), "FBI", font=F_BOLD(13), fill=WHITE)
    for i in range(3):
        draw.line([(x + 8, y + h - 10 - i * 5), (x + w - 8, y + h - 10 - i * 5)],
                  fill=(60, 90, 140), width=1)


def scene_skyline(draw, x, y, w, h):
    """Neon sunset skyline (Vice City mood)."""
    for i, c in enumerate([(255, 140, 90), (255, 90, 120), (120, 60, 160)]):
        draw.rectangle([x, y + i * h // 3, x + w, y + (i + 1) * h // 3], fill=c)
    draw.ellipse([x + w // 2 - 16, y + 8, x + w // 2 + 16, y + 40],
                 fill=(255, 230, 150))
    base = y + h
    heights = [0.45, 0.7, 0.55, 0.85, 0.6, 0.75, 0.5, 0.65]
    bw = w / len(heights)
    for i, hf in enumerate(heights):
        bx = x + i * bw + 2
        draw.rectangle([bx, base - hf * h * 0.7, bx + bw - 4, base],
                       fill=(30, 20, 50))
        for wy in range(2):
            draw.rectangle([bx + 4, base - hf * h * 0.7 + 6 + wy * 12,
                            bx + 8, base - hf * h * 0.7 + 10 + wy * 12],
                           fill=(255, 220, 100))


def scene_quake(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 232, 214))
    scene_mountains(draw, x, y, w, h // 2 + 10, (240, 232, 214),
                    (140, 110, 80), snow=False)
    # crack
    pts = [(x + w // 2, y + h // 2 - 6), (x + w // 2 - 8, y + h // 2 + 8),
           (x + w // 2 + 6, y + h // 2 + 20), (x + w // 2 - 4, y + h - 6)]
    draw.line(pts, fill=(60, 40, 20), width=3)
    # seismograph
    pts = [(x + 8, y + h - 18)]
    import math
    for i in range(1, 20):
        px = x + 8 + i * (w - 16) / 19
        py = y + h - 18 + (math.sin(i * 1.7) * 8 if 6 < i < 14 else 0)
        pts.append((px, py))
    draw.line(pts, fill=RED, width=2)


def scene_trade(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(235, 240, 245))
    # EU circle of stars
    cx, cy = x + w // 4, y + h // 2
    draw.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(0, 51, 153))
    for k in range(12):
        import math
        a = k * math.pi / 6
        draw.ellipse([cx + 18 * math.cos(a) - 2, cy + 18 * math.sin(a) - 2,
                      cx + 18 * math.cos(a) + 2, cy + 18 * math.sin(a) + 2],
                     fill=(255, 204, 0))
    # Indonesia red/white
    ix, iy = x + 3 * w // 4 - 26, y + h // 2 - 18
    draw.rectangle([ix, iy, ix + 52, iy + 18], fill=(222, 41, 16))
    draw.rectangle([ix, iy + 18, ix + 52, iy + 36], fill=WHITE)
    # arrows between
    draw.line([(cx + 30, cy), (ix - 8, cy)], fill=TEAL, width=3)
    draw.polygon([(ix - 8, cy - 5), (ix - 8, cy + 5), (ix + 2, cy)], fill=TEAL)


def scene_ship(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(170, 205, 225))
    for i in range(3):
        yy = y + h - 14 - i * 10
        draw.arc([x - 10, yy - 6, x + w + 10, yy + 10], 0, 180,
                 fill=(255, 255, 255), width=2)
    # cargo ship
    draw.rectangle([x + w // 2 - 46, y + h // 2, x + w // 2 + 46, y + h // 2 + 22],
                   fill=(120, 40, 40))
    for i in range(3):
        draw.rectangle([x + w // 2 - 38 + i * 26, y + h // 2 - 14,
                        x + w // 2 - 18 + i * 26, y + h // 2],
                       fill=(30, 90, 140))
    # drone above
    dx, dy = x + w - 30, y + 16
    draw.ellipse([dx - 8, dy - 4, dx + 8, dy + 4], fill=(40, 40, 40))
    draw.line([(dx - 14, dy - 6), (dx + 14, dy - 6)], fill=(40, 40, 40), width=2)


def scene_cop(draw, x, y, w, h):
    """COP31: globe, sun, and a stalled clock."""
    draw.rectangle([x, y, x + w, y + h], fill=(215, 235, 225))
    cx, cy = x + w // 2, y + h // 2
    draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=(40, 120, 90))
    draw.arc([cx - 28, cy - 28, cx + 28, cy + 28], 200, 340, fill=(180, 230, 200),
             width=3)
    draw.arc([cx - 28, cy - 28, cx + 28, cy + 28], 20, 110, fill=(180, 230, 200),
             width=3)
    draw.ellipse([x + w - 30, y + 6, x + w - 12, y + 24], fill=(255, 200, 60))
    # clock hands at overtime
    draw.line([(cx, cy), (cx, cy - 18)], fill=WHITE, width=2)
    draw.line([(cx, cy), (cx + 14, cy + 6)], fill=WHITE, width=2)


def scene_badge(draw, x, y, w, h):
    """Sheriff star badge for the cartel capture."""
    draw.rectangle([x, y, x + w, y + h], fill=(245, 235, 210))
    scene_mountains(draw, x, y, w, h, (245, 235, 210), (170, 140, 100),
                    snow=False)
    cx, cy = x + w // 2, y + h // 2
    import math
    pts = []
    for k in range(10):
        r = 26 if k % 2 == 0 else 12
        a = -math.pi / 2 + k * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=(212, 175, 55), outline=(140, 100, 20))
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(140, 100, 20))


# ---------------------------------------------------------------- page
PANELS = [
    ("MEXICO", RED, "Cartel boss 'El Chapo Isidro' captured; 11 killed in Sinaloa",
     "Fausto Isidro Meza Flores seized in Guasave; gunbattles followed the arrest. 22 Nov",
     scene_badge),
    ("CLIMATE", TEAL, "COP31 runs into overtime over fossil fuels",
     "Antalya talks stall a second day as nations split on a phaseout. 22 Nov",
     scene_cop),
    ("DIPLOMACY", NAVY2, "Trump, Xi and Putin meet in Shenzhen",
     "Trilateral talks open on nuclear risk reduction. 22 Nov",
     scene_flags3),
    ("UKRAINE", (90, 40, 40), "Russia hits Zelenskyy's hometown; Kyiv hits ship in Baltic",
     "Kryvyi Rih strike kills 2; drone hits a Russian cargo vessel. 22 Nov",
     scene_ship),
    ("MARKETS", (120, 60, 0), "US stocks slide into correction in AI sell-off",
     "Dow and S&P 500 fall sharply as chip shares tumble. 21 Nov",
     scene_chart),
    ("CYBER", (40, 40, 90), "FBI crime database breached, Trump confirms",
     "NCIC system hit; fingerprints and wanted-person records exposed. 22 Nov",
     scene_shield),
    ("CULTURE", (150, 40, 120), "GTA 6 sets $3.79bn launch-day record",
     "Biggest entertainment debut ever as players hunt for secrets. 22 Nov",
     scene_skyline),
    ("DISASTER", (110, 80, 40), "Strong 6.8 quake shakes Peru's Andes",
     "Tremors felt in Lima; no major damage reported yet. 22 Nov",
     scene_quake),
    ("TRADE", (0, 90, 90), "EU and Indonesia sign trade deal after a decade",
     "Ten years of talks end in a pact covering goods and services. 22 Nov",
     scene_trade),
]

TICKER = [
    "Bolsonaro in intensive care",
    "Leeds stun Chelsea 4-1",
    "Amazon nears $7.5bn Decart deal",
    "IBM unveils 520-qubit Nighthawk r3",
    "UN agrees draft autonomous-weapons rules",
    "24 dead in Nigeria boat capsize",
    "EU plastic-waste export ban begins",
    "Modi opens Nitish Setu bridge",
    "Houthis strike after Saudi-led op",
    "China renews UN bid to blacklist BLA",
]


def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # masthead
    d.rectangle([0, 0, W, 92], fill=NAVY)
    d.rectangle([0, 92, W, 96], fill=GOLD)
    f, _ = fit_text(d, "THE WORLD IN ONE PICTURE", "DejaVuSans-Bold.ttf", 46, 940)
    d.text(((W - d.textlength("THE WORLD IN ONE PICTURE", font=f)) / 2, 8),
           "THE WORLD IN ONE PICTURE", font=f, fill=WHITE)
    sub = "SUNDAY, 22 NOVEMBER 2026  ·  20 STORIES  ·  9 REGIONS"
    fs = F_BOLD(19)
    d.text(((W - d.textlength(sub, font=fs)) / 2, 62), sub, font=fs, fill=GOLD)

    # lead panel
    lx, ly, lw, lh = 24, 104, 976, 192
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=WHITE, outline=BORDER, width=2)
    scene_gulf(d, lx + 2, ly + 2, 330, lh - 4)
    tx = lx + 348
    draw_tag(d, tx, ly + 14, "GULF — LEAD", RED)
    f, _ = fit_text(d, "Iran strikes Bahrain industrial site as Gulf war widens",
                    "DejaVuSans-Bold.ttf", 30, lw - 364)
    lines = wrap(d, "Iran strikes Bahrain industrial site as Gulf war widens",
                 F_BOLD(30), lw - 364)
    yy = ly + 44
    for ln in lines[:2]:
        d.text((tx, yy), ln, font=F_BOLD(30), fill=INK)
        yy += 36
    sub_lines = wrap(
        d, "Tehran says it hit US Navy positions; Bahrain says civilian property "
           "was damaged. Hormuz blockade fears grow. 22 Nov",
        F_BODY(17), lw - 364)
    for ln in sub_lines[:3]:
        d.text((tx, yy + 4), ln, font=F_BODY(17), fill=GREY)
        yy += 22

    # 3x3 panel grid
    px = [24, 356, 688]
    pw, ph = 312, 188
    py = [304, 500, 696]
    for i, (tag, color, head, sub, scene) in enumerate(PANELS):
        r, c = divmod(i, 3)
        x, y = px[c], py[r]
        d.rectangle([x, y, x + pw, y + ph], fill=WHITE, outline=BORDER, width=2)
        draw_tag(d, x + 10, y + 10, tag, color)
        lines = wrap(d, head, F_BOLD(20), pw - 20)
        yy = y + 36
        for ln in lines[:3]:
            d.text((x + 10, yy), ln, font=F_BOLD(20), fill=INK)
            yy += 23
        slines = wrap(d, sub, F_BODY(13), pw - 20)
        for ln in slines[:2]:
            d.text((x + 10, yy + 2), ln, font=F_BODY(13), fill=GREY)
            yy += 16
        scene(d, x + 2, y + ph - 46, pw - 4, 44)

    # ticker: greedy-wrap items into lines that fit the band
    ty = 892
    d.rectangle([24, ty, 1000, ty + 76], fill=NAVY)
    d.text((40, ty + 6), "ALSO TODAY", font=F_BOLD(14), fill=GOLD)
    f = F_BODY(13)
    lines, cur = [], ""
    for item in TICKER:
        trial = (cur + "  ·  " + item).strip("  ·  ") if cur else item
        if d.textlength(trial, font=f) <= 940:
            cur = trial
        else:
            lines.append(cur)
            cur = item
    if cur:
        lines.append(cur)
    for i, ln in enumerate(lines[:3]):
        d.text((40, ty + 26 + i * 16), ln, font=f, fill=WHITE)

    # footer
    foot = ("All events dated 22 Nov 2026 unless noted  ·  Front page drawn from "
            "public reporting  ·  make.fun news-image-20261122")
    ff = F_BODY(13)
    d.text(((W - d.textlength(foot, font=ff)) / 2, 984), foot, font=ff, fill=GREY)

    img.save(path, "PNG", optimize=True)


if __name__ == "__main__":
    render(os.path.join(HERE, "entry.png"))
    print("wrote", os.path.join(HERE, "entry.png"))

# Builds animation frames that KEEP her glasses on: blink, her own raised hand waving (rotated +/- around the wrist), and an anime lens glint.
# usage: python3 make_anim.py   (reads ../assets/face_<k>.png, writes face_<k>_blink / _wave1 / _wave2 / _glint)
import os
from collections import Counter
from PIL import Image, ImageDraw
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets") + "/"
def common(im, box):
    px = [p[:3] for p in im.crop(box).getdata() if p[3] > 200]; return Counter(px).most_common(1)[0][0]
def dark(im, box):
    px = [p[:3] for p in im.crop(box).getdata() if p[3] > 200]; return min(px, key=sum)
for k in ("default", "smile", "happy", "sad", "angry"):
    base = Image.open(A + f"face_{k}.png").convert("RGBA")
    skin, ink = common(base, (212, 150, 236, 172)), dark(base, (200, 118, 256, 190)); sleeve = common(base, (220, 225, 238, 245))
    def draw(im): return ImageDraw.Draw(im)
    if k != "happy":                                                      # blink: cover the eyeball, draw a lash line, glasses rims untouched
        b = base.copy(); d = draw(b); fill = common(base, (106, 86, 118, 94))
        for cx, cy, rx in ((91, 82, 8), (131, 80, 9)): d.ellipse([cx-rx, cy-5, cx+rx, cy+6], fill=fill+(255,))
        d.line([(81,83),(86,86),(92,87),(98,85),(101,82)], fill=ink+(255,), width=2); d.line([(121,81),(126,84),(132,85),(138,83),(142,79)], fill=ink+(255,), width=2)
        b.save(A + f"face_{k}_blink.png")
    hand = base.crop((198, 116, 256, 190))
    for n, ang in ((1, 9), (2, -9)):                                       # wave: tilt the hand around the wrist
        p = base.copy(); p.paste((0, 0, 0, 0), (198, 116, 256, 190))
        big = Image.new("RGBA", (116, 148), (0, 0, 0, 0)); big.paste(hand, (29, 37)); r = big.rotate(ang, center=(29 + 28, 37 + 70), resample=Image.NEAREST)
        p.alpha_composite(r, (198 - 29, 116 - 37)); p.save(A + f"face_{k}_wave{n}.png")
    g = base.copy(); d = draw(g)                                           # glint on both lenses
    for a_, b_ in (((82, 87), (90, 77)), ((86, 91), (92, 83)), ((122, 85), (130, 75)), ((126, 89), (132, 81))): d.line([a_, b_], fill=(255, 255, 255, 255), width=2)
    g.save(A + f"face_{k}_glint.png")
# contact sheet for checking
names = ["default", "sad", "angry"]; sh = Image.new("RGBA", (256*4, 256*3), (60, 60, 90, 255))
for r, k in enumerate(names):
    for c, s in enumerate(["", "_blink", "_wave1", "_glint"]): sh.alpha_composite(Image.open(A + f"face_{k}{s}.png"), (c*256, r*256))
sh.save("/tmp/anim_sheet.png")

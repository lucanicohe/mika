# Builds the PC-98 look: 16-colour palette (4 bit per channel), hand-style 2x2 dither, outlines, perspective rooms, pillar frame.
# usage: python3 make_assets.py "<VN Sprite Pack folder>/girlB"   (any folder with default.png smile.png happy.png sad.png angry.png works)
import numpy as np, os, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC = sys.argv[1].rstrip("/") + "/"; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets") + "/"
B4 = np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]) / 16 - .5; B2 = np.array([[0,2],[3,1]]) / 4 - .375
lerp = lambda a, b, t: a + (b - a) * t
def pal_from(img, n, mask=None):
    a = np.array(img.convert("RGB")); px = a[mask] if mask is not None else a.reshape(-1, 3)
    q = Image.fromarray(px.reshape(-1, 1, 3).astype(np.uint8)).quantize(n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    return (np.round(np.array(q.getpalette()[:n*3]).reshape(-1, 3) / 17) * 17).astype(int)
def dither(img, pal, B, amp):
    a = np.array(img.convert("RGB")).astype(float); h, w, _ = a.shape
    a += np.tile(B, (h//B.shape[0]+1, w//B.shape[1]+1))[:h, :w, None] * amp
    return pal[((a[:, :, None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)].astype(np.uint8)
# ---------- character: painterly sprite -> PC-98 bust
def prep(path, box, size):
    im = Image.open(path).convert("RGBA").crop(box).resize(size, Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.UnsharpMask(1.4, 170, 2))
    return rgb, np.array(im)[:, :, 3] > 128
BOX, SIZE = (250, 200, 2000, 1950), (256, 256)
rgb0, m0 = prep(SRC + "default.png", BOX, SIZE); P = pal_from(rgb0, 15, m0); dark = P[P.sum(1).argmin()]
def pc98(rgb, m):
    q = dither(rgb, P, B2, 30)
    L = np.array(rgb.convert("L")).astype(float); gy, gx = np.gradient(L)
    loc = L - np.array(rgb.convert("L").filter(ImageFilter.BoxBlur(2))).astype(float)
    q[(np.hypot(gx, gy) > 14) & (loc < -7) & m] = dark                      # inked line work
    ed = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1)); q[ed] = dark   # silhouette outline
    return Image.fromarray(np.dstack([q, m.astype(np.uint8) * 255]), "RGBA")
for k in ("default", "smile", "happy", "sad", "angry"):
    pc98(*prep(SRC + k + ".png", BOX, SIZE)).save(OUT + f"face_{k}.png")   # (the old *_t talking frames had NO glasses -> removed; run make_anim.py next)
# ---------- backgrounds 480x256: perspective rooms
def room(sky, glow, C, seed=3):
    W, H = 480, 256; im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im); random.seed(seed); ol = (22, 18, 44)
    bx0, by0, bx1, by1 = 118, 66, 262, 150
    top = lambda t: (lerp(0, bx0, t), lerp(W, bx1, t)); P = lambda pts, f: d.polygon([(int(x), int(y)) for x, y in pts], fill=f, outline=ol)
    cp = lambda u, t: (lerp(top(t)[0], top(t)[1], u), lerp(0, by0, t)); fp = lambda u, t: (lerp(top(t)[0], top(t)[1], u), lerp(H, by1, t))
    P([(bx0,by0),(bx1,by0),(bx1,by1),(bx0,by1)], C["back"]); P([(0,0),(W,0),(bx1,by0),(bx0,by0)], C["ceil"]); P([(0,H),(W,H),(bx1,by1),(bx0,by1)], C["floor"])
    P([(0,0),(bx0,by0),(bx0,by1),(0,H)], C["left"]); P([(W,0),(bx1,by0),(bx1,by1),(W,H)], C["right"])
    for u in np.linspace(0, 1, 9):                                          # ceiling tiles, floor tiles
        d.line([cp(u, 0), cp(u, 1)], fill=C["cl"]); d.line([fp(u, 0), fp(u, 1)], fill=C["fl"])
    for t in (.3, .52, .7, .84, .93): d.line([cp(0, t), cp(1, t)], fill=C["cl"]); d.line([fp(0, t), fp(1, t)], fill=C["fl"])
    for (u0, u1, t0, t1) in ((.25,.5,.3,.52),(.55,.8,.3,.52),(.25,.5,.7,.84),(.55,.8,.7,.84)): P([cp(u0,t0),cp(u1,t0),cp(u1,t1),cp(u0,t1)], C["light"])
    lw = lambda t, v: (lerp(0, bx0, t), lerp(lerp(0, by0, t), lerp(H, by1, t), v))
    for (t0, t1) in ((.1, .4), (.5, .8)):                                    # windows on the left wall
        x0, x1 = int(lw(t0, 0)[0]), int(lw(t1, 0)[0])
        for x in range(x0, x1):
            t = x / bx0; ya, yb = lw(t, .16)[1], lw(t, .6)[1]
            for y in range(int(ya), int(yb)): d.point((x, y), fill=tuple(int(lerp(sky[0][i], sky[1][i], (y-ya)/max(1, yb-ya))) for i in range(3)))
            if (x // 7) % 2 == 0 or True:
                hgt = (hash((x // 7, seed)) % 9) / 9 * .55 + .15
                d.line([(x, yb - (yb-ya)*hgt), (x, yb)], fill=(24, 22, 52))
                if x % 7 in (2, 3) and random.random() < .5: d.point((x, yb - (yb-ya)*hgt*random.random()), fill=glow)
        P([lw(t0,.16),lw(t1,.16),lw(t1,.6),lw(t0,.6)], None) if False else d.polygon([lw(t0,.16),lw(t1,.16),lw(t1,.6),lw(t0,.6)], outline=C["frame"], width=3)
        d.line([lw((t0+t1)/2, .16), lw((t0+t1)/2, .6)], fill=C["frame"], width=2); d.line([lw(t0,.38), lw(t1,.38)], fill=C["frame"], width=2)
    d.rectangle([bx0+14,by0+12,bx0+84,by0+48], fill=(228,232,238), outline=ol, width=2)                      # whiteboard
    for k in range(4): d.line([(bx0+20,by0+20+k*8),(bx0+20+random.randint(20,56),by0+20+k*8)], fill=(70,90,160))
    d.rectangle([bx1-34,by0+14,bx1-8,by1], fill=C["door"], outline=ol, width=2); d.ellipse([bx1-60,by0+8,bx1-42,by0+26], fill=(235,235,230), outline=ol, width=2)
    for t in (.0, .3, .58):                                                  # desks with glowing CRTs along the left
        t2 = t + .2; A, Bq, Cq, D2 = fp(.02, t), fp(.3, t), fp(.3, t2), fp(.02, t2); hh = lerp(50, 14, t)
        up = lambda p: (p[0], p[1] - hh)
        P([A, Bq, up(Bq), up(A)], C["desk2"]); P([up(A), up(Bq), up(Cq), up(D2)], C["desk"])
        mw, mh = lerp(56, 18, t), lerp(46, 15, t); cx = (up(A)[0] + up(Bq)[0]) / 2; cy = (up(A)[1] + up(D2)[1]) / 2
        P([(cx-mw/2, cy-mh), (cx+mw/2, cy-mh), (cx+mw/2, cy), (cx-mw/2, cy)], (206, 200, 186)); d.rectangle([cx-mw/2+4, cy-mh+4, cx+mw/2-4, cy-5-mh*.12], fill=(10, 38, 24))
        for k in range(3): d.line([(cx-mw/2+7, cy-mh+9+k*max(3, mh/6)), (cx-mw/2+7+random.randint(8, int(mw*.5)), cy-mh+9+k*max(3, mh/6))], fill=(90,255,150))
    ys = np.linspace(-1, 1, H)[:, None, None]; xs = np.linspace(-1, 1, W)[None, :, None]
    return Image.fromarray(np.clip(np.array(im) * (1 - .22 * (xs**2 + ys**2)), 0, 255).astype(np.uint8))   # vignette
sets = {"dusk": room(((20,20,70),(100,80,150)), (255,230,120), dict(back=(92,100,152),ceil=(58,64,112),floor=(76,66,98),left=(80,88,140),right=(70,76,126),cl=(80,88,140),fl=(100,90,124),light=(206,214,244),frame=(220,220,236),door=(110,80,90),desk=(150,112,92),desk2=(92,70,70))),
        "dawn": room(((244,120,108),(255,214,150)), (255,255,200), dict(back=(206,148,146),ceil=(150,100,124),floor=(140,96,106),left=(196,134,138),right=(176,116,126),cl=(170,118,134),fl=(160,112,120),light=(255,238,206),frame=(250,240,230),door=(130,88,84),desk=(170,124,98),desk2=(104,76,72)), seed=5)}
for n, im in sets.items(): Image.fromarray(dither(im, pal_from(im, 16), B4, 40)).save(OUT + f"bg_{n}.png")
# ---------- frame 640x400: twisted pillars + ornate window borders (image window transparent)
fr = np.zeros((400, 640, 3)); y, x = np.mgrid[0:368, 0:52]
shade = .25 + .55 * np.sin(np.pi * (x + .5) / 52) + .12 * np.sin((y + x * 1.6) / 4.5)
for x0 in (12, 576): fr[16:384, x0:x0+52] = np.clip(shade, 0, 1)[:, :, None] * np.array([205, 190, 215])
for x0 in (6, 570):
    for y0 in (16, 366): fr[y0:y0+18, x0:x0+64] = np.array([190, 175, 200]); fr[y0:y0+3, x0:x0+64] = 235
im = Image.fromarray(fr.astype(np.uint8)); d = ImageDraw.Draw(im)
d.rectangle([76,12,563,275], outline=(205,195,220), width=3); d.rectangle([76,284,563,387], fill=(0,0,0), outline=(205,195,220), width=4); d.rectangle([83,291,556,380], outline=(120,110,150))
for (cx, cy) in ((76,284),(563,284),(76,387),(563,387)): d.ellipse([cx-6,cy-6,cx+6,cy+6], fill=(235,225,240))
Pg = np.array([(0,0,0),(34,30,51),(68,60,85),(102,90,119),(136,125,153),(170,160,187),(204,195,221),(238,235,245)])
out = np.dstack([dither(im, Pg, B4, 30), np.full((400, 640), 255, np.uint8)]); out[16:272, 80:560, 3] = 0
Image.fromarray(out, "RGBA").save(OUT + "frame.png")

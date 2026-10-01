"""Minimal SVG drafting kit (pure standard library).

All coordinates are paper millimetres (the viewBox is 420 x 297 user units = mm), so a viewer shows
true size.  Styling is done through a fixed set of line-weight classes plus fill attributes; hatch
patterns live in <defs>.
"""
import math

W, H = 420.0, 297.0
FRAME = (10.0, 5.0, 415.0, 292.0)          # sheet border (x0, y0, x1, y1)
TB = (235.0, 252.0, 415.0, 292.0)          # title block

FONT = "Arial, Helvetica, 'DejaVu Sans', sans-serif"

CSS = """
.t{font-family:%s;fill:#111}
.b{font-weight:bold}.i{font-style:italic}
.h{stroke:#111;stroke-width:.5;stroke-linejoin:round;stroke-linecap:round}
.m{stroke:#1a1a1a;stroke-width:.25;stroke-linejoin:round;stroke-linecap:round}
.n{stroke:#2a2a2a;stroke-width:.18;stroke-linejoin:round}
.f{stroke:#333;stroke-width:.13;stroke-linejoin:round}
.x{stroke:#555;stroke-width:.07}
.g{stroke:#9a9a9a;stroke-width:.1}
.gg{stroke:#c4c4c4;stroke-width:.08}
.d{stroke:#1d3c6e;stroke-width:.1}
.dsh{stroke:#222;stroke-width:.18;stroke-dasharray:1.6 .8}
.dot{stroke:#444;stroke-width:.14;stroke-dasharray:.25 .55;stroke-linecap:round}
.hid{stroke:#777;stroke-width:.12;stroke-dasharray:1 .7}
.cl{stroke:#b03030;stroke-width:.12;stroke-dasharray:5 1 1 1}
.cut{stroke:#b03030;stroke-width:.35;stroke-dasharray:6 1.2 1.2 1.2}
.red{stroke:#b03030;stroke-width:.13;stroke-dasharray:1.2 .7}
.none{stroke:none}
.halo{paint-order:stroke;stroke:#fff;stroke-width:.8;stroke-linejoin:round}
""" % FONT

PATTERNS = """<defs>
<pattern id="hSlab" width="1.4" height="1.4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="1.4" height="1.4" fill="#ececec"/><line x1="0" y1="0" x2="0" y2="1.4" stroke="#222" stroke-width=".13"/></pattern>
<pattern id="hHull" width="1" height="1" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="1" height="1" fill="#c9d0da"/><line x1="0" y1="0" x2="0" y2="1" stroke="#111" stroke-width=".2"/><line x1="0" y1="0" x2="1" y2="0" stroke="#111" stroke-width=".1"/></pattern>
<pattern id="hHole" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><line x1="0" y1="0" x2="0" y2="1.6" stroke="#444" stroke-width=".12"/></pattern>
<pattern id="hZone" width="1.8" height="1.8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.8" stroke="#d08080" stroke-width=".1"/></pattern>
<pattern id="hPlen" width="1.6" height="1.6" patternUnits="userSpaceOnUse"><circle cx=".4" cy=".4" r=".12" fill="#888"/><circle cx="1.2" cy="1.2" r=".12" fill="#888"/></pattern>
<pattern id="hGlass" width="2" height="2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="2" height="2" fill="#d6ecf7"/><line x1="0" y1="0" x2="0" y2="2" stroke="#5a9abb" stroke-width=".08"/></pattern>
<pattern id="hFloor" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><rect width="1.2" height="1.2" fill="#f2f2f2"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="#555" stroke-width=".1"/></pattern>
</defs>"""


def fmt(v):
    s = "%.2f" % v
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def text_w(s, size):
    """Approximate rendered width (mm) of a string in Arial."""
    return 0.54 * size * len(s)


def trunc(s, maxw, size):
    n = max(1, int(maxw / (0.54 * size)))
    s = str(s)
    return s if len(s) <= n else (s[:max(1, n - 1)] + "~" if n > 1 else s[:1])


class Sheet:
    def __init__(self, num, title, subtitle="", scale="", deck="", room="", room_name="", slug=None):
        self.num, self.title, self.subtitle = num, title, subtitle
        self.scale, self.deck, self.room, self.room_name = scale, deck, room, room_name
        self.slug = slug
        self.out = []
        self.busy = []       # occupied label boxes (x0, y0, x1, y1)

    # ------------------------------------------------------------ primitives
    def line(self, x1, y1, x2, y2, c="m"):
        self.out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="%s"/>' % (fmt(x1), fmt(y1), fmt(x2), fmt(y2), c))

    def poly(self, pts, c="m", fill="none", close=True, op=None):
        tag = "polygon" if close else "polyline"
        o = ' fill-opacity="%s"' % op if op is not None else ""
        self.out.append('<%s points="%s" class="%s" fill="%s"%s/>' % (
            tag, " ".join("%s,%s" % (fmt(x), fmt(y)) for x, y in pts), c, fill, o))

    def rect(self, x, y, w, h, c="m", fill="none", op=None):
        o = ' fill-opacity="%s"' % op if op is not None else ""
        self.out.append('<rect x="%s" y="%s" width="%s" height="%s" class="%s" fill="%s"%s/>' % (
            fmt(x), fmt(y), fmt(w), fmt(h), c, fill, o))

    def circ(self, x, y, r, c="m", fill="none"):
        self.out.append('<circle cx="%s" cy="%s" r="%s" class="%s" fill="%s"/>' % (fmt(x), fmt(y), fmt(r), c, fill))

    def path(self, d, c="m", fill="none", op=None, rule=None):
        o = ' fill-opacity="%s"' % op if op is not None else ""
        r = ' fill-rule="%s"' % rule if rule else ""
        self.out.append('<path d="%s" class="%s" fill="%s"%s%s/>' % (d, c, fill, o, r))

    def text(self, x, y, s, size=2.2, anchor="start", bold=False, rot=0, fill=None, ital=False, maxw=None, halo=False):
        s = str(s)
        if maxw is not None:
            s = trunc(s, maxw, size)
        if not s:
            return
        cl = "t" + (" b" if bold else "") + (" i" if ital else "") + (" halo" if halo else "")
        tr = ' transform="rotate(%s %s %s)"' % (fmt(rot), fmt(x), fmt(y)) if rot else ""
        fl = ' style="fill:%s"' % esc(fill) if fill else ""      # a presentation attribute loses against the `.t{fill}` rule
        a = ' text-anchor="%s"' % anchor if anchor != "start" else ""
        self.out.append('<text x="%s" y="%s" font-size="%s" class="%s"%s%s%s>%s</text>' % (
            fmt(x), fmt(y), fmt(size), cl, a, tr, fl, esc(s)))

    def open_g(self, clip=None, transform=None, extra=""):
        a = ""
        if clip:
            a += ' clip-path="url(#%s)"' % clip
        if transform:
            a += ' transform="%s"' % transform
        self.out.append("<g%s%s>" % (a, extra))

    def close_g(self):
        self.out.append("</g>")

    def clip_def(self, cid, x, y, w, h):
        self.out.append('<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (
            cid, fmt(x), fmt(y), fmt(w), fmt(h)))

    # ------------------------------------------------------------ label placement
    def box_free(self, b, pad=0.3):
        for o in self.busy:
            if b[0] < o[2] + pad and b[2] > o[0] - pad and b[1] < o[3] + pad and b[3] > o[1] - pad:
                return False
        return True

    def reserve(self, b):
        self.busy.append(b)

    def label(self, x, y, s, size=1.8, anchor="start", bold=False, tries=None, fill=None, ital=False):
        """Text at (x, y) (baseline); nudges up/down/sideways to avoid earlier labels; drops it if no luck."""
        w = text_w(s, size)
        cand = tries or [(0, 0), (0, -size * 1.1), (0, size * 1.1), (0, -size * 2.2), (0, size * 2.2), (w * .6, 0), (-w * .6, 0)]
        for dx, dy in cand:
            xx, yy = x + dx, y + dy
            x0 = xx - (w / 2 if anchor == "middle" else (w if anchor == "end" else 0))
            b = (x0, yy - size * .85, x0 + w, yy + size * .25)
            if self.box_free(b):
                self.busy.append(b)
                self.text(xx, yy, s, size, anchor, bold, fill=fill, ital=ital)
                return True
        return False

    # ------------------------------------------------------------ furniture of a sheet
    def frame(self):
        x0, y0, x1, y1 = FRAME
        self.rect(0.5, 0.5, W - 1, H - 1, "x")
        self.rect(x0, y0, x1 - x0, y1 - y0, "h")
        # zone reference marks
        nx, ny = 8, 6
        for i in range(nx):
            xm = x0 + (x1 - x0) * (i + .5) / nx
            self.text(xm, y0 - 1.0, str(i + 1), 1.8, "middle")
            self.text(xm, y1 + 3.2, str(i + 1), 1.8, "middle")
            if i:
                xe = x0 + (x1 - x0) * i / nx
                self.line(xe, y0 - 1.5, xe, y0, "f")
                self.line(xe, y1, xe, y1 + 1.5, "f")
        for j in range(ny):
            ym = y0 + (y1 - y0) * (j + .5) / ny
            self.text(x0 - 1.6, ym + .6, "ABCDEF"[j], 1.8, "middle")
            self.text(x1 + 2.6, ym + .6, "ABCDEF"[j], 1.8, "middle")

    def titleblock(self, extra_rows=None):
        x0, y0, x1, y1 = TB
        self.rect(x0, y0, x1 - x0, y1 - y0, "h", "#ffffff")
        # cells
        self.line(x0, y0 + 14, x1, y0 + 14, "m")
        self.line(x0 + 62, y0, x0 + 62, y0 + 14, "m")
        self.text(x0 + 2, y0 + 5.2, "STARSHIPGO", 4.4, bold=True)
        self.text(x0 + 2, y0 + 9.4, "Interior arrangement", 2.2)
        self.text(x0 + 2, y0 + 12.4, "Engineering drawings - generated", 1.7, fill="#444")
        self.text(x0 + 64, y0 + 3.6, "DRAWING TITLE", 1.4, fill="#666")
        self.text(x0 + 64, y0 + 8.8, self.title, 3.4 if len(self.title) < 34 else 2.7, bold=True, maxw=x1 - x0 - 66)
        self.text(x0 + 64, y0 + 12.6, self.subtitle, 2.0, maxw=x1 - x0 - 66)
        # grid of fields
        fields = [("SHEET", self.num), ("SCALE", self.scale), ("DECK", self.deck), ("ROOM", self.room),
                  ("UNITS", "mm"), ("REV", "A")]
        cw = (x1 - x0) / 3
        rh = 13
        for k, (lab, val) in enumerate(fields):
            cx, cy = x0 + (k % 3) * cw, y0 + 14 + (k // 3) * rh
            self.rect(cx, cy, cw, rh, "f")
            self.text(cx + 1.5, cy + 3.3, lab, 1.4, fill="#666")
            self.text(cx + 1.5, cy + 9.2, val or "-", 3.4 if len(str(val)) < 15 else 2.5, bold=True, maxw=cw - 3)
        self.text(x0 + 1.5, y1 - 0.9 - 0.0, "Drawn by: generated   |   Checked: -   |   Rev A   |   %s" % (self.room_name or ""), 1.3, fill="#555",
                  maxw=x1 - x0 - 3)

    def bow_arrow(self, x, y, label="BOW", r=6.5):
        self.circ(x, y, r, "m", "#fff")
        self.poly([(x, y - r + .8), (x + 2.2, y + 2.4), (x, y + 1.0), (x - 2.2, y + 2.4)], "f", "#111")
        self.line(x, y + 2.4, x, y + r - .7, "f")
        self.text(x, y - r - 1.2, label, 2.0, "middle", bold=True)

    def scalebar(self, x, y, mm_per_m, title="SCALE"):
        """Alternating black/white scale bar starting at (x, y) of a nice length in metres."""
        total = None
        for t in (1, 2, 5, 10, 20, 50, 100):
            if t * mm_per_m >= 28:
                total = t
                break
        if total is None:
            total = 100
        n = 5 if total in (5, 10, 50) else (4 if total in (2, 20) else 2)
        seg = total / n
        self.text(x, y - 3.2, title, 1.4, fill="#666")
        for k in range(n):
            xs = x + k * seg * mm_per_m
            self.rect(xs, y - 1.4, seg * mm_per_m, 1.4, "f", "#111" if k % 2 == 0 else "#fff")
        for k in range(n + 1):
            v = k * seg
            self.text(x + v * mm_per_m, y + 2.4, (("%g" % v) + (" m" if k == n else "")), 1.5, "middle")

    # ------------------------------------------------------------ dimensions
    def tick(self, x, y, size=1.0):
        self.line(x - size * .7, y + size * .7, x + size * .7, y - size * .7, "m")

    def dim_h(self, x1, x2, y, label, ext_y=None, size=2.0, ext2=None, above=True):
        """Horizontal dimension line between paper x1, x2 at height y with oblique ticks."""
        if x2 < x1:
            x1, x2 = x2, x1
        self.line(x1, y, x2, y, "d")
        self.tick(x1, y)
        self.tick(x2, y)
        for xx, ey in ((x1, ext_y), (x2, ext2 if ext2 is not None else ext_y)):
            if ey is not None:
                d = 1.2 if ey > y else -1.2
                self.line(xx, ey, xx, y - d, "d")
        w = text_w(label, size)
        ty = y - 0.7 if above else y + size + 0.3
        if x2 - x1 >= w + 0.6:
            self.text((x1 + x2) / 2, ty, label, size, "middle")
        else:
            self.label((x1 + x2) / 2, ty - (0 if above else 0), label, size, "middle")

    def dim_v(self, y1, y2, x, label, ext_x=None, size=2.0, ext2=None, left=True):
        if y2 < y1:
            y1, y2 = y2, y1
        self.line(x, y1, x, y2, "d")
        self.tick(x, y1)
        self.tick(x, y2)
        for yy, ex in ((y1, ext_x), (y2, ext2 if ext2 is not None else ext_x)):
            if ex is not None:
                d = 1.2 if ex > x else -1.2
                self.line(ex, yy, x - d, yy, "d")
        tx = x - 0.7 if left else x + size + 0.2
        w = text_w(label, size)
        if y2 - y1 >= w + 0.6:
            self.text(tx, (y1 + y2) / 2 + w / 2, label, size, "start", rot=-90)
        elif not any(self.label_rot(tx - k * (size + 0.4), (y1 + y2) / 2, label, size) for k in (0, 1, 2)):
            self.text(tx, (y1 + y2) / 2 + w / 2, label, size, "start", rot=-90)      # never drop a dimension
    def chain_h(self, xs, y, labels, ext_y=None, size=1.9):
        """Continuous horizontal chain through paper x positions `xs` (ascending) with segment labels."""
        self.line(xs[0], y, xs[-1], y, "d")
        for x in xs:
            self.tick(x, y)
            if ext_y is not None:
                d = 1.2 if ext_y > y else -1.2
                self.line(x, ext_y, x, y - d, "d")
        for k, lab in enumerate(labels):
            a, b = xs[k], xs[k + 1]
            w = text_w(lab, size)
            if b - a >= w + 0.5:
                self.text((a + b) / 2, y - 0.6, lab, size, "middle")
            else:
                self.label((a + b) / 2, y - 0.6 - (2.3 if k % 2 else 0), lab, size, "middle")

    def chain_v(self, ys, x, labels, ext_x=None, size=1.9):
        self.line(x, ys[0], x, ys[-1], "d")
        for y in ys:
            self.tick(x, y)
            if ext_x is not None:
                d = 1.2 if ext_x > x else -1.2
                self.line(ext_x, y, x - d, y, "d")
        for k, lab in enumerate(labels):
            a, b = ys[k], ys[k + 1]
            w = text_w(lab, size)
            cy = (a + b) / 2 + w / 2
            if b - a >= w + 0.5:
                self.text(x - 0.6, cy, lab, size, "start", rot=-90)
            else:
                self.label_rot(x - 0.6 - (2.3 if k % 2 else 0), (a + b) / 2, lab, size)

    def label_rot(self, x, y, s, size=1.9):
        w = text_w(s, size)
        b = (x - size * .9, y - w / 2, x + size * .3, y + w / 2)
        if self.box_free(b):
            self.busy.append(b)
            self.text(x, y + w / 2, s, size, "start", rot=-90)
            return True
        return False

    def level_mark(self, x, y, label, size=1.7, right=True):
        """Level mark: small triangle on a short horizontal line, text beside."""
        d = 1 if right else -1
        self.line(x, y, x + d * 9, y, "f")
        self.poly([(x, y), (x - 1.2, y - 2.1), (x + 1.2, y - 2.1)], "f", "#fff")
        self.poly([(x, y), (x + 1.2, y - 2.1), (x, y - 2.1)], "f", "#111")
        self.text(x + d * 1.8, y - 0.5, label, size, "start" if right else "end", bold=True)

    def arrow(self, x1, y1, x2, y2, c="f", head=1.6, fill="#111"):
        self.line(x1, y1, x2, y2, c)
        a = math.atan2(y2 - y1, x2 - x1)
        for s in (1,):
            p1 = (x2 - head * math.cos(a - .3), y2 - head * math.sin(a - .3))
            p2 = (x2 - head * math.cos(a + .3), y2 - head * math.sin(a + .3))
            self.poly([(x2, y2), p1, p2], "none", fill)

    def balloon(self, x, y, code, r=3.3):
        self.circ(x, y, r, "n", "#fff")
        self.text(x, y + .6, code, 2.0 if len(code) <= 5 else 1.6, "middle", bold=True)

    def break_line(self, x1, y1, x2, y2):
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        pts = [(x1, y1), (mx - ux * 1.2, my - uy * 1.2), (mx - ux * .4 + nx * 1.4, my - uy * .4 + ny * 1.4),
               (mx + ux * .4 - nx * 1.4, my + uy * .4 - ny * 1.4), (mx + ux * 1.2, my + uy * 1.2), (x2, y2)]
        self.poly(pts, "f", close=False)

    def table(self, x, y, colw, rows, header=None, rh=3.4, size=1.8, title=None, maxrows=None, zebra=True, bold_first=False):
        """Simple text table; returns the bottom y.  Cells are truncated to their column."""
        cy = y
        if title:
            self.text(x, cy - 1.2, title, 2.3, bold=True)
        tw = sum(colw)
        if header:
            self.rect(x, cy, tw, rh, "n", "#dfe3ea")
            cx = x
            for w, h in zip(colw, header):
                self.text(cx + 1, cy + rh - 1.05, h, size, bold=True, maxw=w - 1.5)
                cx += w
            cy += rh
        n = 0
        for r in rows:
            if maxrows is not None and n >= maxrows:
                self.rect(x, cy, tw, rh, "f", "#fff")
                self.text(x + 1, cy + rh - 1.05, "... +%d more" % (len(rows) - n), size, ital=True)
                cy += rh
                break
            self.rect(x, cy, tw, rh, "f", "#f4f6f9" if (zebra and n % 2) else "#ffffff")
            cx = x
            for k, (w, v) in enumerate(zip(colw, r)):
                self.text(cx + 1, cy + rh - 1.05, v, size, bold=(bold_first and k == 0), maxw=w - 1.5)
                cx += w
            cy += rh
            n += 1
        self.rect(x, y, tw, cy - y, "n")
        return cy

    # ------------------------------------------------------------ output
    def render(self):
        content = self.out
        self.out = list(content)          # frame and title block are drawn on a copy: render() twice gives the same sheet
        try:
            self.frame()
            self.titleblock()
            body = "\n".join(self.out)
        finally:
            self.out = content
        head = ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                'width="420mm" height="297mm" viewBox="0 0 420 297">\n<title>%s - %s</title>\n<style>%s</style>\n%s\n'
                '<rect x="0" y="0" width="420" height="297" fill="#ffffff"/>\n' % (esc(self.num), esc(self.title), CSS, PATTERNS))
        return head + body + "\n</svg>\n"


def wrap_words(text, mx):
    """Greedy word wrap to at most `mx` characters per line; a word longer than a line gets a line of its own (no empty lines)."""
    lines, cur = [], ""
    for w in str(text).split():
        if len(cur) + len(w) + (1 if cur else 0) <= mx or not cur:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def nice_scale(avail_w, avail_h, ext_w, ext_h, options=(20, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500)):
    """First (largest) scale 1:n whose drawing of ext_w x ext_h metres fits avail_w x avail_h paper mm."""
    for n in options:
        s = 1000.0 / n
        if ext_w * s <= avail_w and ext_h * s <= avail_h:
            return n
    return options[-1]

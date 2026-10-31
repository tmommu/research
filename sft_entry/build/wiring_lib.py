"""Tiny SVG library for pictorial wiring diagrams: drawn modules with gold pads, coloured wires and rail tags."""
import math

FONT = 'Helvetica, Arial, sans-serif'
INK = '#1b1b1b'
RAIL = {'12V': ('#c0392b', '12 V'), '5V': ('#e67e22', '5 V'), '3V3': ('#1e8449', '3.3 V')}
WIRE = dict(pwm='#2471a3', en='#8e44ad', isense='#e67e22', tx='#16a085', rx='#1e8449', sda='#d4ac0d', scl='#c0392b',
            trig='#d35400', echo='#2e86c1', pwr='#c0392b', gnd='#1b1b1b', sig='#2471a3', gate='#7d3c98', wireless='#1e8449')


def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class Diagram:
    def __init__(self, w, h, title, subtitle=''):
        self.w, self.h = w, h
        self.comps, self.wires, self.tags = [], [], []
        self.title, self.subtitle = title, subtitle

    # ---------------- primitives ----------------
    def rect(self, x, y, w, h, fill, stroke=INK, sw=1.6, rx=6, layer=None, extra=''):
        (layer if layer is not None else self.comps).append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" fill="%s" stroke="%s" stroke-width="%s" %s/>' % (x, y, w, h, rx, fill, stroke, sw, extra))

    def circle(self, cx, cy, r, fill, stroke=INK, sw=1.4, layer=None):
        (layer if layer is not None else self.comps).append(
            '<circle cx="%.1f" cy="%.1f" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (cx, cy, r, fill, stroke, sw))

    def text(self, x, y, s, size=12, fill=INK, weight='normal', anchor='start', layer=None, rot=None):
        tr = ' transform="rotate(%s %.1f %.1f)"' % (rot, x, y) if rot else ''
        (layer if layer is not None else self.comps).append(
            '<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" font-weight="%s" text-anchor="%s"%s>%s</text>' % (x, y, FONT, size, fill, weight, anchor, tr, esc(s)))

    def line(self, x1, y1, x2, y2, stroke=INK, sw=2, layer=None, extra=''):
        (layer if layer is not None else self.comps).append(
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s" stroke-linecap="round" %s/>' % (x1, y1, x2, y2, stroke, sw, extra))

    def poly(self, pts, stroke, sw=3.2, fill='none', layer=None, dash=False, close=False):
        d = ' '.join('%.1f,%.1f' % p for p in pts)
        tag = 'polygon' if close else 'polyline'
        (layer if layer is not None else self.wires).append(
            '<%s points="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round" stroke-linecap="round"%s/>' % (
                tag, d, fill, stroke, sw, ' stroke-dasharray="9 7"' if dash else ''))

    def pad(self, x, y, r=7.5):
        self.circle(x, y, r, '#e8b923', stroke='#7a5d00', sw=1.4)
        self.circle(x, y, r * 0.38, '#1b1b1b', stroke='none', sw=0)

    # ---------------- wires and tags ----------------
    def wire(self, pts, color, label=None, lpos=None, dash=False, lsize=12, lanchor='middle', sw=3.2):
        self.poly(pts, color, sw=sw, dash=dash)
        if label:
            if lpos is None:
                # label on the longest horizontal segment
                best = None
                for a, b in zip(pts, pts[1:]):
                    ln = abs(a[0] - b[0])
                    if best is None or ln > best[0]:
                        best = (ln, a, b)
                _, a, b = best
                lpos = ((a[0] + b[0]) / 2, a[1] - 6)
            self.text(lpos[0], lpos[1], label, size=lsize, fill=color, weight='bold', anchor=lanchor, layer=self.tags)

    def hvh(self, p, q, mx, color, label=None, **k):
        self.wire([p, (mx, p[1]), (mx, q[1]), q], color, label, **k)

    def vhv(self, p, q, my, color, label=None, **k):
        self.wire([p, (p[0], my), (q[0], my), q], color, label, **k)

    def junction(self, x, y):
        self.circle(x, y, 4.6, INK, stroke='none', sw=0, layer=self.tags)

    def pill(self, x, y, s, color, anchor='left'):
        w = 8.2 * len(s) + 24
        x0 = x if anchor == 'left' else (x - w if anchor == 'right' else x - w / 2)
        self.rect(x0, y - 12, w, 24, color, stroke='none', sw=0, rx=12, layer=self.tags)
        self.text(x0 + w / 2, y + 4.5, s, size=12.5, fill='white', weight='bold', anchor='middle', layer=self.tags)
        return w

    def ground(self, x, y, d='d'):
        ang = {'d': 0, 'r': -90, 'l': 90, 'u': 180}[d]
        g = []
        g.append('<g transform="translate(%.1f %.1f) rotate(%s)" stroke="%s" stroke-width="2.6" stroke-linecap="round">' % (x, y, ang, INK))
        g.append('<line x1="0" y1="0" x2="0" y2="8"/><line x1="-14" y1="8" x2="14" y2="8"/><line x1="-9" y1="14" x2="9" y2="14"/><line x1="-4" y1="20" x2="4" y2="20"/></g>')
        self.tags.append(''.join(g))

    def rail(self, pad, kind, d='r', text=None, stub=26):
        """Short wire from a pad to a rail tag (12 V, 5 V, 3.3 V) or to a ground symbol."""
        x, y = pad
        dx, dy = {'r': (1, 0), 'l': (-1, 0), 'd': (0, 1), 'u': (0, -1)}[d]
        ex, ey = x + dx * stub, y + dy * stub
        if kind == 'GND':
            self.wire([(x, y), (ex, ey)], INK, sw=3)
            self.ground(ex, ey, d)
            return
        col, lab = RAIL[kind]
        self.wire([(x, y), (ex, ey)], col, sw=3.2)
        s = text or lab
        w = 8.2 * len(s) + 24
        if d == 'r':
            self.pill(ex - 2, ey, s, col, 'left')
        elif d == 'l':
            self.pill(ex + 2, ey, s, col, 'right')
        else:
            self.pill(ex, ey + (14 if d == 'd' else -14), s, col, 'center')

    # ---------------- output ----------------
    def svg(self):
        head = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n'
                '<rect width="100%%" height="100%%" fill="white"/>\n') % (self.w, self.h, self.w, self.h)
        t = ['<text x="30" y="46" font-family="%s" font-size="30" font-weight="bold" fill="#0b5d8f">%s</text>' % (FONT, esc(self.title))]
        if self.subtitle:
            t.append('<text x="30" y="72" font-family="%s" font-size="15" fill="#4d646b">%s</text>' % (FONT, esc(self.subtitle)))
        return head + '\n'.join(t + self.comps + self.wires + self.tags) + '\n</svg>\n'

    def save(self, path_svg, path_png=None, scale=1.0):
        s = self.svg()
        open(path_svg, 'w', encoding='utf-8').write(s)
        if path_png:
            import cairosvg
            cairosvg.svg2png(bytestring=s.encode('utf-8'), write_to=path_png, scale=scale)

    def title_under(self, cx, y, s, sub=None):
        self.text(cx, y, s, size=15, weight='bold', anchor='middle')
        if sub:
            self.text(cx, y + 18, sub, size=12, fill='#4d646b', anchor='middle')


# ====================================================================== components
def devkit(d, x, y, w, title, left, right, pitch=28, sub=None, camera=None):
    """ESP32 board. camera: None, 'cam' (ESP32-CAM style) or 'cam_s3'. Returns pad anchors (pad centre on the board edge)."""
    n = max(len(left), len(right))
    h = n * pitch + 96
    d.rect(x, y, w, h, '#171717', stroke='#000', sw=2, rx=10)
    d.rect(x + w / 2 - 28, y - 8, 56, 26, '#c8ccd0', stroke='#6b6f73', sw=1.4, rx=4)       # USB
    d.rect(x + w / 2 - 38, y + 22, 76, 50, '#aeb4ba', stroke='#6b6f73', sw=1.4, rx=3)      # metal can
    d.text(x + w / 2, y + 44, 'ESP32', size=12, weight='bold', anchor='middle', fill='#2b2b2b')
    d.text(x + w / 2, y + 60, 'WROOM' if not camera else 'S3' if camera == 'cam_s3' else 'WROVER', size=10, anchor='middle', fill='#2b2b2b')
    if camera:
        d.rect(x + w - 66, y + 6, 46, 46, '#0e0e0e', stroke='#555', sw=1.2, rx=4)
        d.circle(x + w - 43, y + 29, 14, '#2a2f36', stroke='#777', sw=1.6)
        d.circle(x + w - 43, y + 29, 7, '#0a0c10', stroke='#444', sw=1)
        d.rect(x + 14, y + 8, 40, 14, '#b9bfc5', stroke='#6b6f73', sw=1, rx=2)                  # microSD slot
    a = {}
    top = y + 88
    for i, nm in enumerate(left):
        py = top + i * pitch
        d.pad(x, py)
        d.text(x + 15, py + 4, nm, size=11.5, fill='white')
        a[nm] = (x, py)
    for i, nm in enumerate(right):
        py = top + i * pitch
        d.pad(x + w, py)
        d.text(x + w - 15, py + 4, nm, size=11.5, fill='white', anchor='end')
        a[nm] = (x + w, py)
    d.title_under(x + w / 2, y + h + 24, title, sub)
    return a, h


def bts7960(d, x, y, label, right, left, bottom, w=250, pitch=26):
    """BTS7960 module: control pads on the right, motor pads on the left, supply pads on the bottom."""
    n = max(len(right), 1)
    h = max(n * pitch + 64, 184)
    d.rect(x, y, w, h, '#1f5fae', stroke='#0b2a55', sw=2, rx=8)
    d.rect(x + 62, y + 14, 112, h - 28, '#b8bec5', stroke='#5d6368', sw=1.5, rx=4)         # heat sink
    for i in range(1, 10):
        d.line(x + 62 + i * 11.2, y + 18, x + 62 + i * 11.2, y + h - 18, stroke='#7c848b', sw=1.4)
    d.rect(x + 86, y + h / 2 - 15, 64, 30, '#1b1b1b', stroke='#000', sw=1, rx=3)
    d.text(x + 118, y + h / 2 + 4, 'BTS7960', size=10.5, fill='white', anchor='middle', weight='bold')
    a = {}
    for i, nm in enumerate(right):
        py = y + 40 + i * pitch
        d.pad(x + w, py); d.text(x + w - 14, py + 4, nm, size=11.5, fill='white', anchor='end'); a[nm] = (x + w, py)
    for nm, yo in left:
        py = y + yo
        d.pad(x, py); d.text(x + 14, py + 4, nm, size=11.5, fill='white'); a[nm] = (x, py)
    for i, nm in enumerate(bottom):
        px = x + 60 + i * 130
        d.pad(px, y + h); d.text(px, y + h - 10, nm, size=11.5, fill='white', anchor='middle'); a[nm] = (px, y + h)
    d.title_under(x + w / 2, y + h + 78, label)
    return a, h


def buck(d, x, y, label, w=150, h=96):
    d.rect(x, y, w, h, '#2166b3', stroke='#0b2a55', sw=2, rx=8)
    d.circle(x + w / 2, y + h / 2, 26, '#c3c8ce', stroke='#5d6368', sw=1.6)
    d.circle(x + w / 2, y + h / 2, 9, '#8a9097', stroke='#444', sw=1)
    d.rect(x + w - 44, y + 12, 28, 18, '#eadf8b', stroke='#7a6d20', sw=1, rx=2)
    a = {}
    for nm, px, py in (('IN+', x, y + 26), ('IN-', x, y + h - 26), ('OUT+', x + w, y + 26), ('OUT-', x + w, y + h - 26)):
        d.pad(px, py)
        d.text(px + (14 if px == x else -14), py + 4, nm, size=11.5, fill='white', anchor='start' if px == x else 'end')
        a[nm] = (px, py)
    d.title_under(x + w / 2, y + h + 24, label)
    return a


def solar(d, x, y, w, h, label, cols=6, rows=4, fr=(0.35, 0.65), tleft=False):
    d.rect(x, y, w, h, '#c9ced4', stroke='#555', sw=2, rx=5)
    cw, ch = (w - 16) / cols, (h - 16) / rows
    for r in range(rows):
        for c in range(cols):
            d.rect(x + 8 + c * cw + 2, y + 8 + r * ch + 2, cw - 4, ch - 4, '#1d3d86', stroke='#0b1f4d', sw=1, rx=2)
    a = {'-': (x + w * fr[0], y + h), '+': (x + w * fr[1], y + h)}
    d.pad(*a['-']); d.pad(*a['+'])
    if tleft:
        d.text(x, y + h + 26, label, size=15, weight='bold')
    else:
        d.title_under(x + w / 2, y + h + 28, label)
    return a


def charge_ctrl(d, x, y, w, h, label, fr=(0.35, 0.65), tleft=False):
    d.rect(x, y, w, h, '#1b8a6b', stroke='#0b3d2e', sw=2, rx=8)
    d.rect(x + 24, y + h / 2 - 16, 70, 32, '#101a14', stroke='#000', sw=1, rx=3)
    d.text(x + 59, y + h / 2 + 5, '12 V', size=14, fill='#7CFC9a', anchor='middle', weight='bold')
    for i, c in enumerate(('#e74c3c', '#f1c40f', '#2ecc71')):
        d.circle(x + 120 + i * 24, y + h / 2, 7, c, stroke='#333', sw=1)
    a = {'PV-': (x + w * fr[0], y), 'PV+': (x + w * fr[1], y), 'BAT-': (x + w * fr[0], y + h), 'BAT+': (x + w * fr[1], y + h)}
    for nm, p in a.items():
        d.pad(*p)
        d.text(p[0], p[1] + (18 if p[1] == y else -10), nm, size=11, fill='white', anchor='middle')
    if tleft:
        d.text(x, y + h + 26, label, size=15, weight='bold')
    else:
        d.title_under(x + w / 2, y + h + 28, label)
    return a


def battery(d, x, y, w, h, label, fr=(0.35, 0.65), tleft=False):
    d.rect(x, y, w, h, '#2a2a2e', stroke='#000', sw=2, rx=8)
    d.text(x + w / 2, y + h / 2 + 2, label, size=17, fill='white', anchor='middle', weight='bold')
    d.text(x + w / 2, y + h / 2 + 24, 'sealed lead-acid', size=12, fill='#b8bcc2', anchor='middle')
    a = {'-': (x + w * fr[0], y), '+': (x + w * fr[1], y)}
    d.rect(a['-'][0] - 10, y - 8, 20, 10, '#555', stroke='#222', sw=1, rx=2)
    d.rect(a['+'][0] - 10, y - 8, 20, 10, '#c0392b', stroke='#5a1a12', sw=1, rx=2)
    d.pad(*a['-']); d.pad(*a['+'])
    if tleft:
        d.text(x, y + h + 26, '12 V 12 Ah battery', size=15, weight='bold')
    else:
        d.title_under(x + w / 2, y + h + 26, '12 V 12 Ah battery')
    return a


def fuse(d, cx, cy, label, vertical=True):
    d.rect(cx - 9, cy - 22, 18, 44, '#e9f3f7', stroke='#4a5a63', sw=1.6, rx=4, layer=d.tags)
    d.rect(cx - 10, cy - 24, 20, 8, '#b08d57', stroke='#5b4620', sw=1, rx=2, layer=d.tags)
    d.rect(cx - 10, cy + 16, 20, 8, '#b08d57', stroke='#5b4620', sw=1, rx=2, layer=d.tags)
    d.line(cx, cy - 15, cx, cy + 15, stroke='#8a8f93', sw=1.6, layer=d.tags)
    d.text(cx + 18, cy + 4, label, size=12.5, weight='bold', layer=d.tags)
    return (cx, cy - 24), (cx, cy + 24)


def switch(d, cx, cy, label):
    d.rect(cx - 15, cy - 24, 30, 48, '#2f3338', stroke='#000', sw=1.4, rx=5, layer=d.tags)
    d.rect(cx - 7, cy - 18, 14, 18, '#d6dadd', stroke='#555', sw=1.2, rx=3, layer=d.tags)
    d.circle(cx, cy - 6, 4, '#e74c3c', stroke='#600', sw=1, layer=d.tags)
    d.text(cx + 24, cy + 4, label, size=12.5, weight='bold', layer=d.tags)
    return (cx, cy - 24), (cx, cy + 24)


def motor(d, x, y, label, kind='thruster', w=118, h=62, above=False):
    d.rect(x + 26, y, w - 26, h, '#5b6b7b', stroke='#1f2a34', sw=2, rx=8)
    d.rect(x + 40, y + 6, 14, h - 12, '#f39c12', stroke='#7a4a00', sw=1, rx=2)
    d.rect(x + 62, y + 6, 8, h - 12, '#f39c12', stroke='#7a4a00', sw=1, rx=2)
    if kind == 'thruster':
        d.circle(x + 14, y + h / 2, 18, 'none', stroke='#2a3540', sw=3)
        for k in range(3):
            a = math.radians(90 + k * 120)
            d.line(x + 14, y + h / 2, x + 14 + 15 * math.cos(a), y + h / 2 - 15 * math.sin(a), stroke='#2a3540', sw=5)
    else:
        d.rect(x, y + 8, 30, h - 16, '#e1b12c', stroke='#6a5410', sw=1.6, rx=4)
        d.circle(x + 15, y + h / 2, 7, '#a07d10', stroke='#3d2f00', sw=1)
    a = {'M+': (x + w, y + 18), 'M-': (x + w, y + h - 18)}
    d.pad(*a['M+']); d.pad(*a['M-'])
    if above:
        d.text(x + w / 2 + 8, y - 10, label, size=15, weight='bold', anchor='middle')
    else:
        d.title_under(x + w / 2 + 8, y + h + 22, label)
    return a


def servo(d, x, y, label):
    w, h = 140, 74
    d.rect(x + 30, y, w - 30, h, '#2f3a4a', stroke='#000', sw=2, rx=6)
    d.rect(x + 8, y + 16, 26, h - 32, '#2f3a4a', stroke='#000', sw=1.6, rx=3)
    d.circle(x + w - 28, y + h / 2, 17, '#e8e8e8', stroke='#555', sw=1.6)
    d.rect(x + w - 70, y + h / 2 - 7, 80, 14, '#e8e8e8', stroke='#555', sw=1.4, rx=7)
    d.text(x + 82, y + h / 2 + 5, 'MG996R', size=11, fill='white', weight='bold', anchor='middle')
    a = {}
    for i, (nm, col) in enumerate((('SIG', '#e67e22'), ('V+', '#c0392b'), ('GND', '#6e4b2a'))):
        py = y + 14 + i * 23
        d.line(x + 8, py, x - 22, py, stroke=col, sw=5)
        d.pad(x - 22, py)
        d.text(x - 10, py - 8, nm, size=11, fill=INK, anchor='middle', weight='bold')
        a[nm] = (x - 22, py)
    d.title_under(x + w / 2, y + h + 24, label)
    return a


def mosfet(d, x, y, label):
    d.rect(x + 6, y, 78, 14, '#aeb4ba', stroke='#555', sw=1.4, rx=3)
    d.rect(x + 6, y + 14, 78, 62, '#1b1b1b', stroke='#000', sw=1.8, rx=4)
    d.circle(x + 45, y + 7, 4.5, 'white', stroke='#555', sw=1)
    d.text(x + 45, y + 52, 'IRLZ44N', size=11, fill='white', anchor='middle', weight='bold')
    a = {}
    for i, nm in enumerate(('G', 'D', 'S')):
        px = x + 21 + i * 24
        d.line(px, y + 76, px, y + 98, stroke='#c9ced3', sw=4)
        d.pad(px, y + 98, 6.5)
        a[nm] = (px, y + 98)
    d.title_under(x + 45, y + 124, label)
    return a


def led_strip(d, x, y, w, label):
    d.rect(x, y, w, 30, '#f4f4ee', stroke='#777', sw=1.6, rx=4)
    for i in range(7):
        d.rect(x + 22 + i * ((w - 44) / 6) - 9, y + 7, 18, 16, '#ffe680', stroke='#a88a10', sw=1, rx=2)
    a = {'+': (x, y + 8), '-': (x, y + 22)}
    d.pad(*a['+']); d.pad(*a['-'])
    d.title_under(x + w / 2, y + 54, label)
    return a


def sensor(d, x, y, label, pads, color, chip, w=132, pitch=24, probe=False):
    h = len(pads) * pitch + 28
    d.rect(x, y, w, h, color, stroke='#222', sw=1.8, rx=6)
    d.rect(x + w - 56, y + h / 2 - 14, 34, 28, '#1b1b1b', stroke='#000', sw=1, rx=3)
    d.text(x + w - 39, y + h / 2 + 4, chip, size=8.5, fill='white', anchor='middle')
    a = {}
    for i, nm in enumerate(pads):
        py = y + 22 + i * pitch
        d.pad(x, py)
        d.text(x + 14, py + 4, nm, size=11.5, fill='white')
        a[nm] = (x, py)
    if probe:
        d.line(x + w, y + h / 2, x + w + 34, y + h / 2, stroke='#1b1b1b', sw=4)
        d.circle(x + w + 64, y + h / 2, 30, '#1b1b1b', stroke='#000', sw=2)
        d.circle(x + w + 64, y + h / 2, 17, '#33383d', stroke='#666', sw=1.5)
        d.circle(x + w + 64, y + h / 2, 7, '#111', stroke='#666', sw=1)
    d.title_under(x + (w + (96 if probe else 0)) / 2, y + h + 24, label)
    return a, h


def microswitch(d, x, y, label):
    w, h = 96, 46
    d.rect(x, y, w, h, '#c0392b', stroke='#5a1a12', sw=1.8, rx=6)
    d.line(x + 12, y, x + 70, y - 18, stroke='#9aa0a6', sw=4)
    d.rect(x + 36, y + 14, 24, 18, '#1b1b1b', stroke='#000', sw=1, rx=2)
    a = {'A': (x, y + h / 2), 'B': (x + w, y + h / 2)}
    d.pad(*a['A']); d.pad(*a['B'])
    d.title_under(x + w / 2, y + h + 24, label)
    return a


def resistor(d, cx, cy, label, vertical=False):
    if not vertical:
        d.rect(cx - 24, cy - 8, 48, 16, '#d9b779', stroke='#6b5320', sw=1.4, rx=4, layer=d.tags)
        for dx, c in ((-12, '#8e44ad'), (-3, '#c0392b'), (6, '#e67e22')):
            d.rect(cx + dx - 2, cy - 8, 4, 16, c, stroke='none', sw=0, rx=0, layer=d.tags)
        d.text(cx, cy - 14, label, size=12, weight='bold', anchor='middle', layer=d.tags)
        return (cx - 24, cy), (cx + 24, cy)
    d.rect(cx - 8, cy - 24, 16, 48, '#d9b779', stroke='#6b5320', sw=1.4, rx=4, layer=d.tags)
    for dy, c in ((-12, '#8e44ad'), (-3, '#c0392b'), (6, '#e67e22')):
        d.rect(cx - 8, cy + dy - 2, 16, 4, c, stroke='none', sw=0, rx=0, layer=d.tags)
    d.text(cx + 14, cy + 4, label, size=12, weight='bold', layer=d.tags)
    return (cx, cy - 24), (cx, cy + 24)

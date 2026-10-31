"""SAGIP skimmer boat: parametric 3D model (millimetres).

Writes ../SAGIP_Boat_3D_Model.stl (import into Tinkercad with Import > upload, units mm)
and ../SAGIP_Boat_3D_Model.png (numbered preview that matches the parts table in the
prototype design document).

All sizes are planning values. Edit the numbers in the PARAMETERS block and re-run.
Needs: numpy, trimesh, pillow.
"""
import math, sys
import numpy as np
import trimesh
from trimesh import transformations as tf
from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ PARAMETERS (mm)
FLOAT_R = 80            # 6-inch PVC pipe, about 160 mm outside diameter
FLOAT_L = 1500          # one 1.5 m pipe per float
FLOAT_Y = 320           # float centre line, left and right
WATERLINE = 96          # about 60 percent submerged at the planning load
DECK_Z = 190            # underside of the deck
DECK = (1400, 760, 6)
PANEL = (600, 350, 18)  # 30 W panel, flat on the deck
BELT_L, BELT_W, BELT_ANGLE = 600, 220, 24
BELT_LOW = np.array([640.0, 0.0, 150.0])

# ------------------------------------------------------------------ helpers
parts = []   # dict(name, mesh, color, no, alpha, near)


def add(name, mesh, color, no=None, alpha=1.0, near=False, model=True):
    parts.append(dict(name=name, mesh=mesh, color=np.array(color, float), no=no, alpha=alpha, near=near, model=model))


def box(center, size, rot=None):
    m = trimesh.creation.box(extents=size)
    if rot is not None:
        m.apply_transform(rot)
    m.apply_translation(center)
    return m


def cyl(center, r, h, axis='x', sections=48):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=sections)   # along z
    if axis == 'x':
        m.apply_transform(tf.rotation_matrix(math.pi / 2, [0, 1, 0]))
    elif axis == 'y':
        m.apply_transform(tf.rotation_matrix(math.pi / 2, [1, 0, 0]))
    m.apply_translation(center)
    return m


def local_frame(origin, direction_up_angle):
    """Frame whose +x points up the belt (toward the stern) and whose +z is the belt normal."""
    th = math.radians(direction_up_angle)
    R = tf.rotation_matrix(math.pi + th, [0, 1, 0])
    T = R.copy()
    T[:3, 3] = origin
    return T


def in_frame(T, local_center, size):
    m = trimesh.creation.box(extents=size)
    m.apply_translation(local_center)
    m.apply_transform(T)
    return m


C_ORANGE = (0.93, 0.52, 0.16)
C_STEEL = (0.62, 0.64, 0.68)
C_DARK = (0.12, 0.12, 0.14)
C_WOOD = (0.82, 0.66, 0.42)
C_PANEL = (0.10, 0.20, 0.45)
C_BOX = (0.78, 0.80, 0.82)

# ------------------------------------------------------------------ 11 floats, deck, clamps
for sgn, nm in ((-1, 'float_near'), (1, 'float_far')):
    y = sgn * FLOAT_Y
    add(nm, cyl([0, y, FLOAT_R], FLOAT_R, FLOAT_L, 'x'), C_ORANGE, 11, near=(sgn < 0))
    for xs in (-1, 1):
        add(nm + '_cap', cyl([xs * (FLOAT_L / 2 + 4), y, FLOAT_R], FLOAT_R + 4, 8, 'x'), (0.85, 0.46, 0.12), 11, near=(sgn < 0))
    for x in (-450, 0, 450):
        add('clamp', box([x, y, 2 * FLOAT_R + (DECK_Z - 2 * FLOAT_R) / 2], (40, 50, DECK_Z - 2 * FLOAT_R)), C_STEEL, 11, near=(sgn < 0))
add('deck', box([0, 0, DECK_Z + DECK[2] / 2], DECK), C_WOOD, 11, alpha=0.5)

# ------------------------------------------------------------------ 7 solar panel
pz = DECK_Z + DECK[2] + 12 + PANEL[2] / 2
add('panel', box([-390, 0, pz], PANEL), C_PANEL, 7)
for dx in (-270, 270):
    for dy in (-140, 140):
        add('panel_leg', box([-390 + dx, dy, DECK_Z + DECK[2] + 6], (20, 20, 12)), C_STEEL, 7)

# ------------------------------------------------------------------ 6 electronics box
add('electronics_box', box([-250, 275, DECK_Z + DECK[2] + 40], (220, 160, 80)), C_BOX, 6)
add('electronics_lid', box([-250, 275, DECK_Z + DECK[2] + 82], (226, 166, 6)), (0.9, 0.9, 0.92), 6)

# ------------------------------------------------------------------ 8 battery, low between the floats
add('battery', box([-120, 0, 128], (240, 150, 100)), (0.55, 0.12, 0.12), 8)

# ------------------------------------------------------------------ 9 thrusters
for sgn in (-1, 1):
    y = sgn * FLOAT_Y
    add('thruster', cyl([-FLOAT_L / 2 - 55, y, WATERLINE], 28, 100, 'x'), C_DARK, 9, near=(sgn < 0))
    add('thruster_shroud', cyl([-FLOAT_L / 2 - 110, y, WATERLINE], 42, 40, 'x'), (0.2, 0.2, 0.24), 9, near=(sgn < 0))

# ------------------------------------------------------------------ 10 side sensors and compass
for sgn in (-1, 1):
    add('side_sensor', cyl([300, sgn * (FLOAT_Y + FLOAT_R + 11), 130], 14, 22, 'y'), (0.1, 0.45, 0.2), 10, near=(sgn < 0))
add('compass_module', box([480, -250, DECK_Z + DECK[2] + 4], (30, 30, 8)), (0.1, 0.45, 0.2), 10, near=True)

# ------------------------------------------------------------------ 2 scoop, 3 belt, cleats
T = local_frame(BELT_LOW + np.array([-BELT_L / 2 * math.cos(math.radians(BELT_ANGLE)), 0, BELT_L / 2 * math.sin(math.radians(BELT_ANGLE))]), BELT_ANGLE)
add('belt', in_frame(T, [0, 0, 0], (BELT_L, BELT_W, 14)), (0.22, 0.22, 0.25), 3)
for sy in (-1, 1):
    add('belt_rail', in_frame(T, [0, sy * (BELT_W / 2 + 5), 18], (BELT_L, 10, 40)), C_STEEL, 3)
for lx in range(-270, 300, 70):
    add('cleat', in_frame(T, [lx, 0, 16], (6, BELT_W - 20, 18)), (0.05, 0.05, 0.06), 3)
scoop = box([BELT_LOW[0] + 70, 0, BELT_LOW[2] - 28], (170, 300, 6), tf.rotation_matrix(math.radians(18), [0, 1, 0]))
add('scoop', scoop, (0.75, 0.77, 0.8), 2)

# ------------------------------------------------------------------ 4 hood and belt camera
add('hood', in_frame(T, [BELT_L / 2 - 110, 0, 82], (260, 250, 150)), (0.08, 0.08, 0.1), 4)
add('hood_lip', in_frame(T, [BELT_L / 2 - 110, 0, 9], (266, 256, 10)), (0.3, 0.3, 0.32), 4)

# ------------------------------------------------------------------ 5 gate and bins
up = BELT_LOW + np.array([-BELT_L * math.cos(math.radians(BELT_ANGLE)), 0, BELT_L * math.sin(math.radians(BELT_ANGLE))])
add('gate_servo', box([up[0] + 10, 0, up[1] * 0 + 372], (60, 40, 40)), (0.15, 0.15, 0.6), 5)
for y, col in ((-95, (0.2, 0.45, 0.8)), (95, (0.25, 0.65, 0.35))):
    add('bin', box([110, y, DECK_Z + DECK[2] + 75], (150, 170, 150)), col, 5)

# ------------------------------------------------------------------ 1 bow camera on a short post
add('bow_post', box([690, 300, DECK_Z + DECK[2] + 130], (20, 20, 260)), C_STEEL, 1)
add('bow_camera', box([700, 300, DECK_Z + DECK[2] + 275], (60, 40, 32), tf.rotation_matrix(math.radians(-12), [0, 1, 0])), C_DARK, 1)

# ------------------------------------------------------------------ 12 flood node on the bank (context only)
BANK_Y = 1200
add('bank', box([200, BANK_Y + 80, WATERLINE + 8], (1100, 440, 24)), (0.45, 0.55, 0.32), None)
add('staff_gauge', box([200, BANK_Y - 190, 280], (30, 12, 560)), (0.95, 0.95, 0.95), 12)
for z in (150, 240, 330):
    add('float_switch', cyl([200, BANK_Y - 190 - 14, z], 12, 16, 'y'), (0.9, 0.2, 0.2), 12)
add('node_box', box([200, BANK_Y + 20, WATERLINE + 20 + 55], (170, 120, 110)), C_BOX, 12)
add('node_panel', box([200, BANK_Y + 20, WATERLINE + 20 + 125], (150, 100, 6), tf.rotation_matrix(math.radians(-25), [1, 0, 0])), C_PANEL, 12)

# water for the preview only
add('water', box([-50, 450, WATERLINE - 1], (1900, 2100, 2)), (0.55, 0.78, 0.9), None, alpha=0.4, model=False)

# ------------------------------------------------------------------ STL export
if __name__ == '__main__' and '--no-stl' not in sys.argv:
    solid = [p['mesh'] for p in parts if p['model']]
    merged = trimesh.util.concatenate(solid)
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else '../SAGIP_Boat_3D_Model.stl'
    merged.export(out)
    ext = merged.bounds
    print('stl', out, 'triangles', len(merged.faces), 'bounds mm', ext[0].round(0), ext[1].round(0))


# ------------------------------------------------------------------ renderer (numpy z-buffer)
def render(view, W, H, margin=0.07, exclude_near=False, exclude_tags=(), cx_cy_scale=None, ss=2):
    f, r, u = view
    sel = [p for p in parts if not (exclude_near and p['near']) and p['name'] not in exclude_tags]
    allv = np.vstack([p['mesh'].vertices for p in sel if p['no'] is not None or p['name'] in ('bank',)])
    sx, sy = allv @ r, allv @ u
    w, h = sx.max() - sx.min(), sy.max() - sy.min()
    scale = min(W * (1 - 2 * margin) / w, H * (1 - 2 * margin) / h)
    ox = W / 2 - (sx.max() + sx.min()) / 2 * scale
    oy = H / 2 + (sy.max() + sy.min()) / 2 * scale
    Ws, Hs = W * ss, H * ss
    zbuf = np.full((Hs, Ws), np.inf)
    img = np.ones((Hs, Ws, 3))
    idb = np.full((Hs, Ws), -1, dtype=int)
    light = np.array([0.35, -0.45, 0.82]); light /= np.linalg.norm(light)

    def project(V):
        X = (V @ r) * scale + ox
        Y = oy - (V @ u) * scale
        D = V @ f
        return X * ss, Y * ss, D

    def raster(p, pid, blend=None):
        m = p['mesh']
        X, Y, D = project(m.vertices)
        for fi, tri in enumerate(m.faces):
            n = m.face_normals[fi]
            shade = 0.42 + 0.58 * abs(float(n @ light))
            col = np.clip(p['color'] * shade, 0, 1)
            x0, y0, x1, y1, x2, y2 = X[tri[0]], Y[tri[0]], X[tri[1]], Y[tri[1]], X[tri[2]], Y[tri[2]]
            minx, maxx = int(max(0, math.floor(min(x0, x1, x2)))), int(min(Ws - 1, math.ceil(max(x0, x1, x2))))
            miny, maxy = int(max(0, math.floor(min(y0, y1, y2)))), int(min(Hs - 1, math.ceil(max(y0, y1, y2))))
            if minx > maxx or miny > maxy:
                continue
            den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(den) < 1e-9:
                continue
            gx, gy = np.meshgrid(np.arange(minx, maxx + 1) + 0.5, np.arange(miny, maxy + 1) + 0.5)
            a = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / den
            b = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / den
            c = 1 - a - b
            inside = (a >= -1e-6) & (b >= -1e-6) & (c >= -1e-6)
            if not inside.any():
                continue
            d = a * D[tri[0]] + b * D[tri[1]] + c * D[tri[2]]
            sub_z = zbuf[miny:maxy + 1, minx:maxx + 1]
            if blend is None:
                ok = inside & (d < sub_z)
                sub_z[ok] = d[ok]
                img[miny:maxy + 1, minx:maxx + 1][ok] = col
                idb[miny:maxy + 1, minx:maxx + 1][ok] = pid
            else:
                ok = inside & (d < sub_z)
                reg = img[miny:maxy + 1, minx:maxx + 1]
                reg[ok] = reg[ok] * (1 - blend) + col * blend

    opaque = [(i, p) for i, p in enumerate(sel) if p['alpha'] >= 1.0]
    trans = [(i, p) for i, p in enumerate(sel) if p['alpha'] < 1.0]
    for i, p in opaque:
        raster(p, i)
    # outlines where the part id changes
    edge = np.zeros((Hs, Ws), bool)
    edge[:, 1:] |= idb[:, 1:] != idb[:, :-1]
    edge[1:, :] |= idb[1:, :] != idb[:-1, :]
    img[edge] *= 0.55
    for i, p in sorted(trans, key=lambda t: 0 if t[1]['name'] == 'water' else 1):
        raster(p, i, blend=p['alpha'])
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)

    def to_px(P):
        P = np.asarray(P, float)
        return (float(P @ r) * scale + ox, oy - float(P @ u) * scale)
    return im, to_px


def make_view(az_deg, el_deg):
    az, el = math.radians(az_deg), math.radians(el_deg)
    cam = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])   # direction to camera
    f = -cam
    z = np.array([0, 0, 1.0])
    r = np.cross(f, z)
    if np.linalg.norm(r) < 1e-6:
        r = np.array([1.0, 0, 0]) if abs(el_deg) > 80 else np.array([0, 1.0, 0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return f, r, u


ANCHORS = {
    1: (700, 300, 480), 2: (790, 0, 112), 3: (365, 0, 290), 4: (150, 0, 420), 5: (110, -95, 350),
    6: (-250, 275, 282), 7: (-390, 0, 238), 8: (-120, 0, 128), 9: (-840, 320, 96), 10: (300, 411, 130),
    11: (-300, -320, 168), 12: (200, 1230, 245),
}
NAMES = {1: 'Bow camera (navigation)', 2: 'Scoop', 3: 'Cleated conveyor belt', 4: 'Belt camera under hood (sorting)',
         5: 'Servo gate and two bins', 6: 'Electronics box', 7: '30 W solar panel', 8: '12 V 12 Ah battery',
         9: 'Two thrusters', 10: 'Side sensors and compass', 11: 'Twin 6-inch PVC floats and deck', 12: 'Flood node on the bank'}


def font(size, bold=True):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else ''), size)


def label(im, to_px, offsets, only=None, rad=22):
    d = ImageDraw.Draw(im)
    fnt = font(int(rad * 1.1))
    for n, (dx, dy) in offsets.items():
        if only and n not in only:
            continue
        ax, ay = to_px(ANCHORS[n])
        lx, ly = ax + dx, ay + dy
        d.line([(ax, ay), (lx, ly)], fill=(30, 30, 30), width=3)
        d.ellipse([ax - 5, ay - 5, ax + 5, ay + 5], fill=(30, 30, 30))
        d.ellipse([lx - rad, ly - rad, lx + rad, ly + rad], fill=(255, 255, 255), outline=(30, 30, 30), width=3)
        d.text((lx, ly), str(n), fill=(30, 30, 30), font=fnt, anchor='mm')


if __name__ == '__main__':
    W1, H1 = 1800, 980
    iso, px1 = render(make_view(-35, 28), W1, H1)
    label(iso, px1, {1: (110, -60), 2: (150, 50), 3: (170, -130), 4: (60, -210), 5: (-200, 40), 6: (-30, -170), 7: (-200, -40),
                     9: (-50, -120), 10: (170, 40), 11: (-40, 150), 12: (140, -90)})
    side, px2 = render(make_view(-90, 0), 1100, 560, margin=0.1, exclude_near=True, exclude_tags=('bank', 'staff_gauge', 'float_switch', 'node_box', 'node_panel'))
    label(side, px2, {1: (-40, -90), 2: (-10, 90), 3: (70, -120), 4: (-10, -120), 5: (-120, -70), 6: (-70, -110), 7: (-70, -90),
                      8: (50, 105), 9: (-60, 90), 11: (-90, 100)}, rad=20)
    top, px3 = render(make_view(-90, 89.9), 1100, 700, margin=0.1, exclude_tags=('bank', 'staff_gauge', 'float_switch', 'node_box', 'node_panel'))
    label(top, px3, {1: (-20, -80), 2: (60, -70), 3: (-30, -90), 4: (40, 110), 5: (-60, 100), 6: (-40, -80), 7: (0, 110), 9: (-60, -80),
                     10: (50, -80), 11: (-120, 90)}, rad=20)
    pad = 24
    CW = W1
    legend_h = 150
    canvas = Image.new('RGB', (CW, 90 + H1 + 560 + pad * 3 + legend_h), (255, 255, 255))
    dr = ImageDraw.Draw(canvas)
    dr.text((pad, 22), 'SAGIP autonomous solar skimmer boat: 3D model (planning sizes in mm)', fill=(11, 93, 143), font=font(40))
    canvas.paste(iso, (0, 90))
    y2 = 90 + H1 + pad
    side_s = side.resize((int(1100 * 0.72), int(560 * 0.72) + 0)).resize((CW // 2 - pad, int((CW // 2 - pad) * 560 / 1100)))
    top_s = top.resize((CW // 2 - pad, int((CW // 2 - pad) * 700 / 1100)))
    canvas.paste(side_s, (0, y2))
    canvas.paste(top_s, (CW // 2 + pad // 2, y2))
    dr.text((pad, y2 + side_s.size[1] + 4), 'Side view, near float removed to show the battery', fill=(60, 60, 60), font=font(26, False))
    dr.text((CW // 2 + pad, y2 + top_s.size[1] + 4), 'Top view, deck shown see-through', fill=(60, 60, 60), font=font(26, False))
    ly = y2 + max(side_s.size[1], top_s.size[1]) + 50
    cols = 3
    for i, n in enumerate(sorted(NAMES)):
        x = pad + (i % cols) * (CW // cols)
        y = ly + (i // cols) * 34
        dr.ellipse([x, y, x + 28, y + 28], fill=(255, 255, 255), outline=(30, 30, 30), width=2)
        dr.text((x + 14, y + 14), str(n), fill=(30, 30, 30), font=font(18), anchor='mm')
        dr.text((x + 40, y + 14), NAMES[n], fill=(30, 30, 30), font=font(22, False), anchor='lm')
    canvas = canvas.crop((0, 0, CW, ly + 4 * 34 + 10))
    out = '../SAGIP_Boat_3D_Model.png'
    canvas.save(out)
    print('png', out, canvas.size)

    # compact figure for the prototype design document: isometric view plus the numbered legend
    LH = 4 * 34 + 20
    small = Image.new('RGB', (CW, H1 + LH), (255, 255, 255))
    small.paste(iso, (0, 0))
    sd = ImageDraw.Draw(small)
    for i, n in enumerate(sorted(NAMES)):
        x = pad + (i % cols) * (CW // cols)
        y = H1 + 10 + (i // cols) * 34
        sd.ellipse([x, y, x + 28, y + 28], fill=(255, 255, 255), outline=(30, 30, 30), width=2)
        sd.text((x + 14, y + 14), str(n), fill=(30, 30, 30), font=font(18), anchor='mm')
        sd.text((x + 40, y + 14), NAMES[n], fill=(30, 30, 30), font=font(22, False), anchor='lm')
    small = small.crop((0, 90, CW, H1 + LH))
    small.save('fig_3d_iso.png')
    print('png fig_3d_iso.png', small.size)

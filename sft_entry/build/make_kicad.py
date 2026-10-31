"""Generate the SAGIP KiCad 7 schematic (boat plus flood node) into ../kicad/SAGIP.kicad_sch.

Every connection is a net label on a short wire stub, so the sheet reads like a pin map and the
netlist can be checked with `kicad-cli sch export netlist`. Module symbols list only the pins this
design uses. All values are planning values to confirm against the parts actually bought.
"""
import math, uuid, os, json, sys

ROOT_UUID = str(uuid.uuid4())
PROJECT = "SAGIP"
FS = 1.27
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kicad')
os.makedirs(out_dir, exist_ok=True)


def uid():
    return str(uuid.uuid4())


def g(v):
    return ('%.3f' % v).rstrip('0').rstrip('.')


def effects(size=FS, hide=False, justify=None, bold=False):
    j = ' (justify %s)' % justify if justify else ''
    return '(effects (font (size %s %s)%s)%s%s)' % (g(size), g(size), ' bold' if bold else '', j, ' hide' if hide else '')


# ------------------------------------------------------------------ symbol library
LIB = {}   # name -> dict(sexpr, pins={number: (name, x, y, side)}, w, h, kind)


def snap(v, step=2.54):
    return math.ceil(v / step - 1e-9) * step


def box_symbol(name, left, right, top=(), bottom=(), ref='U', min_w=12.7):
    rows = max(len(left), len(right), 1)
    maxl = max([len(p) for p in left] + [0]); maxr = max([len(p) for p in right] + [0])
    w = max(min_w, snap(1.15 * (maxl + maxr) + 4))
    ncols = max(len(top), len(bottom), 0)
    if ncols:
        w = max(w, snap(ncols * 7.62 + 2.54))
    h = rows * 2.54 + 2.54
    if top or bottom:
        h += 2.54
    hw, hh = w / 2, h / 2
    pins = {}
    items = []
    num = 1
    y0 = (rows - 1) * 1.27
    for i, p in enumerate(left):
        y = y0 - i * 2.54
        items.append('(pin passive line (at %s %s 0) (length 2.54) (name "%s" %s) (number "%d" %s))' % (g(-hw - 2.54), g(y), p, effects(), num, effects()))
        pins[num] = (p, -hw - 2.54, y, 'L'); num += 1
    for i, p in enumerate(right):
        y = y0 - i * 2.54
        items.append('(pin passive line (at %s %s 180) (length 2.54) (name "%s" %s) (number "%d" %s))' % (g(hw + 2.54), g(y), p, effects(), num, effects()))
        pins[num] = (p, hw + 2.54, y, 'R'); num += 1
    for i, p in enumerate(top):
        x = -((len(top) - 1) * 7.62) / 2 + i * 7.62
        items.append('(pin passive line (at %s %s 270) (length 2.54) (name "%s" %s) (number "%d" %s))' % (g(x), g(hh + 2.54), p, effects(), num, effects()))
        pins[num] = (p, x, hh + 2.54, 'T'); num += 1
    for i, p in enumerate(bottom):
        x = -((len(bottom) - 1) * 7.62) / 2 + i * 7.62
        items.append('(pin passive line (at %s %s 90) (length 2.54) (name "%s" %s) (number "%d" %s))' % (g(x), g(-hh - 2.54), p, effects(), num, effects()))
        pins[num] = (p, x, -hh - 2.54, 'B'); num += 1
    body = '(rectangle (start %s %s) (end %s %s) (stroke (width 0.254) (type default)) (fill (type background)))' % (g(-hw), g(hh), g(hw), g(-hh))
    LIB[name] = dict(gfx=[body], pins_sx=items, pins=pins, w=w + 5.08, h=h + (5.08 if (top or bottom) else 0), ref=ref, hide_names=False)


def two_pin_symbol(name, gfx, ref, pin_names=('1', '2'), horizontal=False):
    items, pins = [], {}
    if not horizontal:
        items.append('(pin passive line (at 0 3.81 270) (length 1.27) (name "%s" %s) (number "1" %s))' % (pin_names[0], effects(0.8), effects(0.8)))
        items.append('(pin passive line (at 0 -3.81 90) (length 1.27) (name "%s" %s) (number "2" %s))' % (pin_names[1], effects(0.8), effects(0.8)))
        pins[1] = (pin_names[0], 0, 3.81, 'T'); pins[2] = (pin_names[1], 0, -3.81, 'B')
    LIB[name] = dict(gfx=gfx, pins_sx=items, pins=pins, w=5.08, h=7.62, ref=ref, hide_names=True)


STK = '(stroke (width 0.254) (type default))'
two_pin_symbol('R', ['(rectangle (start -1.016 2.54) (end 1.016 -2.54) %s (fill (type none)))' % STK], 'R')
two_pin_symbol('Fuse', ['(rectangle (start -1.016 2.54) (end 1.016 -2.54) %s (fill (type none)))' % STK,
                        '(polyline (pts (xy 0 2.54) (xy 0 -2.54)) %s (fill (type none)))' % STK], 'F')
two_pin_symbol('C', ['(polyline (pts (xy -1.905 0.635) (xy 1.905 0.635)) %s (fill (type none)))' % STK,
                     '(polyline (pts (xy -1.905 -0.635) (xy 1.905 -0.635)) %s (fill (type none)))' % STK,
                     '(polyline (pts (xy 0 2.54) (xy 0 0.635)) %s (fill (type none)))' % STK,
                     '(polyline (pts (xy 0 -0.635) (xy 0 -2.54)) %s (fill (type none)))' % STK], 'C', ('+', '-'))
two_pin_symbol('Diode', ['(polyline (pts (xy -1.27 1.27) (xy 1.27 1.27) (xy 0 -1.27) (xy -1.27 1.27)) %s (fill (type none)))' % STK,
                         '(polyline (pts (xy -1.27 -1.27) (xy 1.27 -1.27)) %s (fill (type none)))' % STK,
                         '(polyline (pts (xy 0 2.54) (xy 0 1.27)) %s (fill (type none)))' % STK], 'D', ('A', 'K'))
two_pin_symbol('Switch', ['(circle (center 0 2.54) (radius 0.508) %s (fill (type none)))' % STK,
                          '(circle (center 0 -2.54) (radius 0.508) %s (fill (type none)))' % STK,
                          '(polyline (pts (xy 0 2.03) (xy 1.524 -1.905)) %s (fill (type none)))' % STK], 'SW')
two_pin_symbol('Battery', ['(polyline (pts (xy -2.54 0.635) (xy 2.54 0.635)) %s (fill (type none)))' % STK,
                           '(polyline (pts (xy -1.27 -0.635) (xy 1.27 -0.635)) %s (fill (type none)))' % STK,
                           '(polyline (pts (xy 0 2.54) (xy 0 0.635)) %s (fill (type none)))' % STK,
                           '(polyline (pts (xy 0 -0.635) (xy 0 -2.54)) %s (fill (type none)))' % STK], 'BT', ('+', '-'))


def lib_symbol_sexpr(name):
    s = LIB[name]
    hide = '(pin_names (offset 0.254) hide) (pin_numbers hide) ' if s['hide_names'] else '(pin_names (offset 1.016)) '
    ref_y = s['h'] / 2 + 1.5
    out = '(symbol "%s:%s" %s(in_bom yes) (on_board yes)\n' % (PROJECT, name, hide)
    out += '  (property "Reference" "%s" (at 0 %s 0) %s)\n' % (s['ref'], g(ref_y), effects())
    out += '  (property "Value" "%s" (at 0 %s 0) %s)\n' % (name, g(-ref_y), effects())
    out += '  (property "Footprint" "" (at 0 0 0) %s)\n' % effects(hide=True)
    out += '  (property "Datasheet" "" (at 0 0 0) %s)\n' % effects(hide=True)
    out += '  (symbol "%s_0_1"\n    %s\n  )\n' % (name, '\n    '.join(s['gfx']))
    out += '  (symbol "%s_1_1"\n    %s\n  )\n)' % (name, '\n    '.join(s['pins_sx']))
    return out


# ------------------------------------------------------------------ module symbol definitions
box_symbol('PV_Panel', ['+', '-'], [], ref='PV')
box_symbol('Charge_Controller_20A', ['PV+', 'PV-'], ['BAT+', 'BAT-'], ref='U')
box_symbol('Buck_5V_3A', ['IN+', 'IN-'], ['OUT+', 'OUT-'], ref='U')
box_symbol('Motor', ['+', '-'], [], ref='M')
box_symbol('Servo_MG996R', ['SIG', 'V+', 'GND'], [], ref='M')
box_symbol('BTS7960_Module', ['RPWM', 'LPWM', 'R_EN', 'L_EN', 'R_IS', 'L_IS', 'VCC', 'GND'], ['B+', 'B-', 'M+', 'M-'], ref='U')
box_symbol('ESP32_DevKit_Controller',
           ['VIN 5V', 'GND', '3V3', 'IO4 MOTOR_EN', 'IO13 THR_L_PWM', 'IO14 THR_R_PWM', 'IO18 BELT_RPWM', 'IO19 BELT_LPWM',
            'IO34 IS_THR_L', 'IO35 IS_THR_R', 'IO36 IS_BELT', 'IO39 VBAT'],
           ['IO21 SDA', 'IO22 SCL', 'IO23 TRIG_L', 'IO5 TRIG_R', 'IO25 ECHO_L', 'IO26 ECHO_R', 'IO27 BUMP',
            'IO16 RX2 (bow)', 'IO17 TX2 (bow)', 'IO32 RX (S3)', 'IO33 TX (S3)'], ref='U')
box_symbol('ESP32_S3_CAM_N16R8', ['5V', 'GND', '3V3', 'TX', 'RX', 'SERVO_PWM', 'LED_GATE', 'SDA', 'SCL'], [], ref='U')
box_symbol('ESP32_CAM_TypeC', ['5V', 'GND', 'U0T TX', 'U0R RX'], [], ref='U')
box_symbol('MPU6050_Module', ['VCC', 'GND', 'SCL', 'SDA'], [], ref='U')
box_symbol('QMC5883L_Module', ['VCC', 'GND', 'SCL', 'SDA'], [], ref='U')
box_symbol('DS3231_RTC_Module', ['VCC', 'GND', 'SCL', 'SDA'], [], ref='U')
box_symbol('JSN_SR04T', ['VCC 5V', 'GND', 'TRIG', 'ECHO'], [], ref='U')
box_symbol('N_MOSFET', ['G'], ['D', 'S'], ref='Q', min_w=10.16)
box_symbol('NPN', ['B'], ['C', 'E'], ref='Q', min_w=10.16)
box_symbol('LED_Strip_12V', ['+', '-'], [], ref='LED')
box_symbol('Buzzer_Active_5V', ['+', '-'], [], ref='BZ')
box_symbol('TP4056_Protected', ['IN+', 'IN-', 'B+', 'B-'], ['OUT+', 'OUT-'], ref='U')
box_symbol('Boost_MT3608', ['IN+', 'IN-'], ['OUT+', 'OUT-'], ref='U')
box_symbol('ESP32_DevKit_FloodNode', ['VIN 5V', 'GND', '3V3', 'IO32 WATCH', 'IO33 ALERT', 'IO25 DANGER', 'IO26 BUZZER', 'IO27 LED'], [], ref='U')

# ------------------------------------------------------------------ placement
sheet = []     # sexpr strings
nets = {}      # net -> list of (ref, pin name)
placed = {}    # ref -> dict(x, y, lib)
STUB = 5.08


def place(lib, ref, value, cx, cy, conns):
    s = LIB[lib]
    cx, cy = round(cx / 1.27) * 1.27, round(cy / 1.27) * 1.27
    placed[ref] = dict(x=cx, y=cy, lib=lib, w=s['w'], h=s['h'])
    refy = cy - s['h'] / 2 - 1.5
    valy = cy + s['h'] / 2 + 1.5
    out = '(symbol (lib_id "%s:%s") (at %s %s 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)\n' % (PROJECT, lib, g(cx), g(cy))
    out += '  (uuid %s)\n' % uid()
    if s['hide_names']:
        out += '  (property "Reference" "%s" (at %s %s 0) %s)\n' % (ref, g(cx + 4), g(cy - 1.5), effects(justify='left'))
        out += '  (property "Value" "%s" (at %s %s 0) %s)\n' % (value, g(cx + 4), g(cy + 1.5), effects(justify='left'))
    else:
        out += '  (property "Reference" "%s" (at %s %s 0) %s)\n' % (ref, g(cx), g(refy), effects())
        out += '  (property "Value" "%s" (at %s %s 0) %s)\n' % (value, g(cx), g(valy), effects())
    out += '  (property "Footprint" "" (at %s %s 0) %s)\n' % (g(cx), g(cy), effects(hide=True))
    out += '  (property "Datasheet" "" (at %s %s 0) %s)\n' % (g(cx), g(cy), effects(hide=True))
    for n in s['pins']:
        out += '  (pin "%d" (uuid %s))\n' % (n, uid())
    out += '  (instances (project "%s" (path "/%s" (reference "%s") (unit 1))))\n)' % (PROJECT, ROOT_UUID, ref)
    sheet.append(out)
    # connections
    byname = {}
    for n, (pname, px, py, side) in s['pins'].items():
        byname.setdefault(pname, []).append((n, px, py, side))
    used = set()
    for pname, net in conns.items():
        if pname not in byname:
            raise SystemExit('%s has no pin %s' % (ref, pname))
        for (n, px, py, side) in byname[pname][:1]:
            used.add(pname)
            x, y = cx + px, cy - py          # library y is up, sheet y is down
            if side == 'L':
                x2, y2, ang, just = x - STUB, y, 180, 'right bottom'
            elif side == 'R':
                x2, y2, ang, just = x + STUB, y, 0, 'left bottom'
            elif side == 'T':
                x2, y2, ang, just = x, y - 2.54, 0, 'left bottom'
            else:
                x2, y2, ang, just = x, y + 2.54, 0, 'left top'
            sheet.append('(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid %s))' % (g(x), g(y), g(x2), g(y2), uid()))
            sheet.append('(label "%s" (at %s %s %d) %s (uuid %s))' % (net, g(x2), g(y2), ang, effects(justify=just), uid()))
            nets.setdefault(net, []).append((ref, pname))
    missing = [p for p in byname if p not in used]
    if missing:
        raise SystemExit('%s: unconnected pins %s' % (ref, missing))
    return placed[ref]


def note(text, x, y, size=2.0, bold=False):
    sheet.append('(text "%s" (at %s %s 0) %s (uuid %s))' % (text.replace('"', "'"), g(x), g(y), effects(size, justify='left bottom', bold=bold), uid()))


def frame_refs(refs, title, margin=30):
    xs1 = [placed[r]['x'] - placed[r]['w'] / 2 for r in refs]; xs2 = [placed[r]['x'] + placed[r]['w'] / 2 for r in refs]
    ys1 = [placed[r]['y'] - placed[r]['h'] / 2 for r in refs]; ys2 = [placed[r]['y'] + placed[r]['h'] / 2 for r in refs]
    frame(min(xs1) - margin, min(ys1) - 18, max(xs2) + margin, max(ys2) + 14, title)


def frame(x1, y1, x2, y2, title):
    sheet.append('(rectangle (start %s %s) (end %s %s) (stroke (width 0.3) (type dash)) (fill (type none)) (uuid %s))' % (g(x1), g(y1), g(x2), g(y2), uid()))
    note(title, x1 + 3, y1 + 7, 3.0, bold=True)


class Column:
    def __init__(self, x, y0, gap=14):
        self.x, self.y, self.gap = x, y0, gap

    def add(self, lib, ref, value, conns, dx=0):
        h = LIB[lib]['h']
        cy = self.y + h / 2
        place(lib, ref, value, self.x + dx, cy, conns)
        self.y += h + self.gap
        return cy


# ================================================================== BOAT
X0, Y0 = 20, 58
BOAT_START = len(placed)

# ---- column 1: charging and battery ----
c1 = Column(50, Y0 + 5)
c1.add('PV_Panel', 'PV1', '30 W solar panel', {'+': 'PV+', '-': 'GND'})
c1.add('Charge_Controller_20A', 'U1', '20 A charge controller', {'PV+': 'PV+', 'PV-': 'GND', 'BAT+': 'BAT+', 'BAT-': 'GND'})
c1.add('Battery', 'BT1', '12 V 12 Ah SLA', {'+': 'BAT+', '-': 'GND'})
c1.add('Fuse', 'F0', '15 A main', {'1': 'BAT+', '2': 'BAT_F'})
c1.add('Switch', 'SW1', 'Master switch', {'1': 'BAT_F', '2': '+12V'})
c1.add('C', 'C1', '1000 uF 25 V', {'+': '+12V', '-': 'GND'})
c1.add('R', 'R1', '100k', {'1': '+12V', '2': 'VBAT'})
c1.add('R', 'R2', '33k', {'1': 'VBAT', '2': 'GND'})
c1.add('C', 'C3', '100 nF', {'+': 'VBAT', '-': 'GND'})

# ---- column 2: branch fuses and 5 V rails ----
c2 = Column(125, Y0 + 5)
c2.add('Fuse', 'F1', '5 A left thruster', {'1': '+12V', '2': 'V_THR_L'})
c2.add('Fuse', 'F2', '5 A right thruster', {'1': '+12V', '2': 'V_THR_R'})
c2.add('Fuse', 'F3', '5 A belt motor', {'1': '+12V', '2': 'V_BELT'})
c2.add('Fuse', 'F4', '3 A electronics', {'1': '+12V', '2': 'V_ELEC'})
c2.add('Buck_5V_3A', 'U2', 'Buck 5 V 3 A (logic)', {'IN+': 'V_ELEC', 'IN-': 'GND', 'OUT+': '+5V', 'OUT-': 'GND'})
c2.add('Buck_5V_3A', 'U3', 'Buck 5 V 3 A (servo)', {'IN+': 'V_ELEC', 'IN-': 'GND', 'OUT+': '+5V_SERVO', 'OUT-': 'GND'})
c2.add('C', 'C2', '470 uF 10 V servo', {'+': '+5V_SERVO', '-': 'GND'})
c2.add('R', 'R3', '10k motor enable pull-down', {'1': 'MOTOR_EN', '2': 'GND'})

# ---- column 3: motor drivers and motors ----
c3 = Column(205, Y0 + 5, gap=18)
c3.add('BTS7960_Module', 'DRV1', 'BTS7960 left thruster',
       {'RPWM': 'THR_L_PWM', 'LPWM': 'GND', 'R_EN': 'MOTOR_EN', 'L_EN': 'MOTOR_EN', 'R_IS': 'IS_THR_L', 'L_IS': 'IS_THR_L', 'VCC': '+5V', 'GND': 'GND',
        'B+': 'V_THR_L', 'B-': 'GND', 'M+': 'THR_L+', 'M-': 'THR_L-'})
c3.add('BTS7960_Module', 'DRV2', 'BTS7960 right thruster',
       {'RPWM': 'THR_R_PWM', 'LPWM': 'GND', 'R_EN': 'MOTOR_EN', 'L_EN': 'MOTOR_EN', 'R_IS': 'IS_THR_R', 'L_IS': 'IS_THR_R', 'VCC': '+5V', 'GND': 'GND',
        'B+': 'V_THR_R', 'B-': 'GND', 'M+': 'THR_R+', 'M-': 'THR_R-'})
c3.add('BTS7960_Module', 'DRV3', 'BTS7960 belt motor',
       {'RPWM': 'BELT_RPWM', 'LPWM': 'BELT_LPWM', 'R_EN': 'MOTOR_EN', 'L_EN': 'MOTOR_EN', 'R_IS': 'IS_BELT', 'L_IS': 'IS_BELT', 'VCC': '+5V', 'GND': 'GND',
        'B+': 'V_BELT', 'B-': 'GND', 'M+': 'BELT+', 'M-': 'BELT-'})

# ---- column 4: motors, current-sense loads, controller ----
c4 = Column(290, Y0 + 5, gap=12)
c4.add('Motor', 'M1', 'Left thruster 12 V', {'+': 'THR_L+', '-': 'THR_L-'})
c4.add('Motor', 'M2', 'Right thruster 12 V', {'+': 'THR_R+', '-': 'THR_R-'})
c4.add('Motor', 'M3', 'Belt gear motor 12 V', {'+': 'BELT+', '-': 'BELT-'})
c4.add('R', 'R4', '1k IS left', {'1': 'IS_THR_L', '2': 'GND'})
c4.add('R', 'R5', '1k IS right', {'1': 'IS_THR_R', '2': 'GND'})
c4.add('R', 'R6', '1k IS belt', {'1': 'IS_BELT', '2': 'GND'})

c5 = Column(385, Y0 + 5, gap=14)
c5.add('ESP32_DevKit_Controller', 'U4', 'ESP32 DevKit (boat controller)',
       {'VIN 5V': '+5V', 'GND': 'GND', '3V3': '+3V3', 'IO4 MOTOR_EN': 'MOTOR_EN', 'IO13 THR_L_PWM': 'THR_L_PWM', 'IO14 THR_R_PWM': 'THR_R_PWM',
        'IO18 BELT_RPWM': 'BELT_RPWM', 'IO19 BELT_LPWM': 'BELT_LPWM', 'IO34 IS_THR_L': 'IS_THR_L', 'IO35 IS_THR_R': 'IS_THR_R',
        'IO36 IS_BELT': 'IS_BELT', 'IO39 VBAT': 'VBAT', 'IO21 SDA': 'SDA', 'IO22 SCL': 'SCL', 'IO23 TRIG_L': 'TRIG_L', 'IO5 TRIG_R': 'TRIG_R',
        'IO25 ECHO_L': 'ECHO_L_3V3', 'IO26 ECHO_R': 'ECHO_R_3V3', 'IO27 BUMP': 'BUMP', 'IO16 RX2 (bow)': 'BOW_TX', 'IO17 TX2 (bow)': 'BOW_RX',
        'IO32 RX (S3)': 'S3_TX', 'IO33 TX (S3)': 'S3_RX'})
c5.add('ESP32_CAM_TypeC', 'U5', 'ESP32-CAM Type C (bow, navigation)', {'5V': '+5V', 'GND': 'GND', 'U0T TX': 'BOW_TX', 'U0R RX': 'BOW_RX'})

# ---- column 6: sensors ----
c6 = Column(500, Y0 + 5, gap=14)
c6.add('MPU6050_Module', 'U6', 'MPU6050 tilt sensor', {'VCC': '+3V3', 'GND': 'GND', 'SCL': 'SCL', 'SDA': 'SDA'})
c6.add('QMC5883L_Module', 'U7', 'QMC5883L compass (optional)', {'VCC': '+3V3', 'GND': 'GND', 'SCL': 'SCL', 'SDA': 'SDA'})
c6.add('JSN_SR04T', 'U8', 'JSN-SR04T left side', {'VCC 5V': '+5V', 'GND': 'GND', 'TRIG': 'TRIG_L', 'ECHO': 'ECHO_L_5V'})
c6.add('JSN_SR04T', 'U9', 'JSN-SR04T right side', {'VCC 5V': '+5V', 'GND': 'GND', 'TRIG': 'TRIG_R', 'ECHO': 'ECHO_R_5V'})
c6.add('Switch', 'SW2', 'Bump switch left', {'1': 'BUMP', '2': 'GND'})
c6.add('Switch', 'SW3', 'Bump switch right', {'1': 'BUMP', '2': 'GND'})

c7 = Column(580, Y0 + 5, gap=12)
c7.add('R', 'R7', '1k echo divider L', {'1': 'ECHO_L_5V', '2': 'ECHO_L_3V3'})
c7.add('R', 'R8', '2k echo divider L', {'1': 'ECHO_L_3V3', '2': 'GND'})
c7.add('R', 'R9', '1k echo divider R', {'1': 'ECHO_R_5V', '2': 'ECHO_R_3V3'})
c7.add('R', 'R10', '2k echo divider R', {'1': 'ECHO_R_3V3', '2': 'GND'})
c7.add('R', 'R11', '10k bump pull-up', {'1': '+3V3', '2': 'BUMP'})
c7.add('C', 'C4', '100 nF bump debounce', {'+': 'BUMP', '-': 'GND'})

# ---- column 8: sorting camera board, gate, hood light ----
c8 = Column(665, Y0 + 5, gap=14)
c8.add('ESP32_S3_CAM_N16R8', 'U10', 'ESP32-S3 N16R8 CAM (sorting, logging)',
       {'5V': '+5V', 'GND': 'GND', '3V3': '+3V3_S3', 'TX': 'S3_TX', 'RX': 'S3_RX', 'SERVO_PWM': 'SERVO_PWM', 'LED_GATE': 'LED_GATE', 'SDA': 'SDA_S3', 'SCL': 'SCL_S3'})
c8.add('DS3231_RTC_Module', 'U11', 'DS3231 RTC (optional)', {'VCC': '+3V3_S3', 'GND': 'GND', 'SCL': 'SCL_S3', 'SDA': 'SDA_S3'})
c8.add('Servo_MG996R', 'M4', 'MG996R gate servo', {'SIG': 'SERVO_PWM', 'V+': '+5V_SERVO', 'GND': 'GND'})
c8.add('R', 'R12', '220 gate resistor', {'1': 'LED_GATE', '2': 'LED_G'})
c8.add('R', 'R13', '10k gate pull-down', {'1': 'LED_G', '2': 'GND'})
c8.add('N_MOSFET', 'Q1', 'Logic-level N-MOSFET', {'G': 'LED_G', 'D': 'LED-', 'S': 'GND'})
c8.add('LED_Strip_12V', 'LED1', '12 V LED strip (hood)', {'+': 'V_ELEC', '-': 'LED-'})

# ================================================================== FLOOD NODE
BOAT_REFS = list(placed)[BOAT_START:]
frame_refs(BOAT_REFS, 'BOAT: power, motor drivers, controller, sensors, cameras')
FY = max(placed[r]['y'] + placed[r]['h'] / 2 for r in BOAT_REFS) + 75
NODE_START = len(placed)
n1 = Column(50, FY + 5, gap=14)
n1.add('PV_Panel', 'PV2', '2 W 5 V solar panel', {'+': 'NPV+', '-': 'NGND'})
n1.add('TP4056_Protected', 'U20', 'TP4056 with protection',
       {'IN+': 'NPV+', 'IN-': 'NGND', 'B+': 'NBAT+', 'B-': 'NCELL-', 'OUT+': 'NOUT+', 'OUT-': 'NGND'})
n1.add('Battery', 'BT2', 'Protected 18650 in IP67 box', {'+': 'NBAT+', '-': 'NCELL-'})
n2 = Column(125, FY + 5, gap=14)
n2.add('Boost_MT3608', 'U21', 'MT3608 boost to 5 V', {'IN+': 'NOUT+', 'IN-': 'NGND', 'OUT+': 'N5V', 'OUT-': 'NGND'})
n2.add('ESP32_DevKit_FloodNode', 'U22', 'ESP32 DevKit (flood node)',
       {'VIN 5V': 'N5V', 'GND': 'NGND', '3V3': 'N3V3', 'IO32 WATCH': 'FS_WATCH', 'IO33 ALERT': 'FS_ALERT', 'IO25 DANGER': 'FS_DANGER',
        'IO26 BUZZER': 'BUZ_B', 'IO27 LED': 'LED_OUT'})
n3 = Column(205, FY + 5, gap=12)
n3.add('Switch', 'SW4', 'Float switch WATCH', {'1': 'N3V3', '2': 'FS_WATCH'})
n3.add('Switch', 'SW5', 'Float switch ALERT', {'1': 'N3V3', '2': 'FS_ALERT'})
n3.add('Switch', 'SW6', 'Float switch DANGER', {'1': 'N3V3', '2': 'FS_DANGER'})
n3.add('R', 'R20', '100k pull-down', {'1': 'FS_WATCH', '2': 'NGND'})
n3.add('R', 'R21', '100k pull-down', {'1': 'FS_ALERT', '2': 'NGND'})
n3.add('R', 'R22', '100k pull-down', {'1': 'FS_DANGER', '2': 'NGND'})
n4 = Column(290, FY + 5, gap=12)
n4.add('R', 'R23', '1k buzzer base', {'1': 'BUZ_B', '2': 'BUZ_BASE'})
n4.add('NPN', 'Q2', 'NPN S8050 or 2N2222', {'B': 'BUZ_BASE', 'C': 'BUZ-', 'E': 'NGND'})
n4.add('Buzzer_Active_5V', 'BZ1', 'Active buzzer 5 V', {'+': 'N5V', '-': 'BUZ-'})
n5 = Column(375, FY + 5, gap=12)
n5.add('R', 'R24', '330 LED resistor', {'1': 'LED_OUT', '2': 'LED_A'})
n5.add('Diode', 'LED2', 'Status LED', {'A': 'LED_A', 'K': 'NGND'})

NODE_REFS = list(placed)[NODE_START:]
frame_refs(NODE_REFS, 'FLOOD NODE on the bank: solar, protected 18650, ESP32 wakes on a float switch')
note('Boat power: 30 W panel > 20 A controller > 12 V 12 Ah battery > 15 A fuse > master switch > branch fuses > buck converters and BTS7960 drivers.', X0, 12, 2.0)
note('Drivers default off: MOTOR_EN has a 10k pull-down. Thrusters use RPWM only (steering by speed difference), the belt uses RPWM and LPWM so it can reverse on a jam.', X0, 17, 2.0)
note('Module symbols show only the pins used. Check pin labels and the ECHO divider against the modules you buy. All values are planning values.', X0, 22, 2.0)

# ------------------------------------------------------------------ write file
lib_syms = '\n'.join(lib_symbol_sexpr(n) for n in LIB)
head = ('(kicad_sch (version 20230121) (generator eeschema)\n  (uuid %s)\n  (paper "A1")\n'
        '  (title_block (title "SAGIP autonomous solar skimmer boat and flood node") (date "2026-10-31") (rev "1")\n'
        '    (company "Quezon City Science High School") (comment 1 "Planning schematic, not a PCB design. Values to be confirmed against bought parts."))\n'
        '  (lib_symbols\n%s\n  )\n') % (ROOT_UUID, lib_syms)
tail = '\n  (sheet_instances (path "/" (page "1")))\n)\n'
with open(os.path.join(out_dir, 'SAGIP.kicad_sch'), 'w') as f:
    f.write(head + '\n'.join(sheet) + tail)
with open(os.path.join(out_dir, 'SAGIP.kicad_pro'), 'w') as f:
    json.dump({"meta": {"filename": "SAGIP.kicad_pro", "version": 1}, "schematic": {"drawing": {"default_text_size": 50.0}}}, f, indent=2)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nets_expected.json'), 'w') as f:
    json.dump({k: v for k, v in sorted(nets.items())}, f, indent=1)
print('parts', len(placed), 'nets', len(nets), 'lib symbols', len(LIB))

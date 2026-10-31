"""Pictorial wiring diagrams (vector drawings of the modules joined by coloured wires).
Writes ../SAGIP_Wiring_Boat.svg/.png and ../SAGIP_Wiring_FloodNode.svg/.png. Needs cairosvg."""
import sys
sys.path.insert(0, '.')
from wiring_lib import *

RED, BLK = WIRE['pwr'], WIRE['gnd']


def legend(d, x, y, w, h, lines, pills=True):
    d.rect(x, y, w, h, '#f6f7f8', stroke='#b9c0c6', sw=1.6, rx=10)
    cy = y + 34
    if pills:
        px = x + 20
        for kind in ('12V', '5V', '3V3'):
            col, lab = RAIL[kind]
            wdt = d.pill(px, cy, lab, col)
            px += wdt + 12
        d.text(px + 4, cy + 5, 'same tag = connected to that rail', size=13, layer=d.tags)
        d.ground(x + 34, cy + 28, 'd')
        d.text(x + 64, cy + 50, 'common ground (all grounds are joined)', size=13, layer=d.tags)
        cy += 76
    for t in lines:
        d.text(x + 20, cy, t, size=12.5, fill='#33424a', layer=d.tags)
        cy += 21


# ====================================================================== BOAT
def boat():
    d = Diagram(2150, 1500, 'SAGIP boat wiring', 'Boat on the water. Full detail with every resistor and capacitor: kicad/SAGIP.kicad_sch')

    # ---- power chain ----
    sp = solar(d, 60, 110, 230, 130, '30 W solar panel', fr=(0.62, 0.86), tleft=True)
    cc = charge_ctrl(d, 60, 330, 230, 110, '20 A charge controller', fr=(0.62, 0.86), tleft=True)
    bt = battery(d, 60, 560, 230, 110, '12 V 12 Ah', fr=(0.62, 0.86), tleft=True)
    d.wire([sp['-'], cc['PV-']], BLK); d.wire([sp['+'], cc['PV+']], RED)
    d.wire([cc['BAT-'], bt['-']], BLK); d.wire([cc['BAT+'], bt['+']], RED)
    jx = bt['+'][0]
    d.junction(jx, 520)
    d.wire([(jx, 520), (330, 520), (330, 551)], RED)
    ft, fb = fuse(d, 330, 575, '15 A')
    d.wire([fb, (330, 626)], RED)
    st, sb = switch(d, 330, 650, 'master switch')
    d.rail(sb, '12V', 'd', text='12 V rail')
    d.junction(bt['-'][0], 520)
    d.rail((bt['-'][0], 520), 'GND', 'l', stub=60)

    b1 = buck(d, 170, 800, '5 V buck (logic)')
    d.rail(b1['IN+'], '12V', 'l', text='12 V · F4 3 A'); d.rail(b1['IN-'], 'GND', 'l')
    d.rail(b1['OUT+'], '5V', 'r'); d.rail(b1['OUT-'], 'GND', 'r')
    b2 = buck(d, 170, 960, '5 V buck (servo only)')
    d.rail(b2['IN+'], '12V', 'l', text='12 V · F4 3 A'); d.rail(b2['IN-'], 'GND', 'l')
    d.rail(b2['OUT+'], '5V', 'r', text='5 V servo'); d.rail(b2['OUT-'], 'GND', 'r')

    # ---- drivers and motors ----
    left = [('M+', 40), ('M-', 66), ('VCC', 112), ('GND', 138)]
    drv = []
    specs = [(110, ['RPWM', 'EN', 'IS'], 'BTS7960 left thruster', 'F1'),
             (440, ['RPWM', 'EN', 'IS'], 'BTS7960 right thruster', 'F2'),
             (770, ['RPWM', 'LPWM', 'EN', 'IS'], 'BTS7960 belt motor', 'F3')]
    for y, right, lab, fz in specs:
        a, h = bts7960(d, 580, y, lab, right, left, ['B+', 'B-'])
        d.rail(a['B+'], '12V', 'd', text='12 V · %s 5 A' % fz)
        d.rail(a['B-'], 'GND', 'd', stub=22)
        d.rail(a['VCC'], '5V', 'l'); d.rail(a['GND'], 'GND', 'l')
        drv.append(a)
    for (mx_, my_, lab, kind), a in zip(((400, 132, 'Left thruster', 'thruster'), (400, 462, 'Right thruster', 'thruster'), (400, 792, 'Conveyor motor', 'gear')), drv):
        m = motor(d, mx_, my_, lab, kind, above=True)
        d.wire([m['M+'], a['M+']], RED); d.wire([m['M-'], a['M-']], BLK)

    # ---- boat controller ----
    L = ['IO13 PWM', 'IO34 IS', 'IO14 PWM', 'IO35 IS', 'IO18 RPWM', 'IO19 LPWM', 'IO36 IS', 'IO4 EN']
    Rr = ['IO16 RX', 'IO17 TX', 'IO32 RX', 'IO33 TX', 'IO21 SDA', 'IO22 SCL', 'IO23 TRIG', 'IO25 ECHO', 'IO5 TRIG', 'IO26 ECHO',
          'IO27 BUMP', 'IO39 VBAT', 'VIN', 'GND', '3V3']
    c, ch = devkit(d, 940, 100, 190, 'ESP32 DevKit (boat controller)', L, Rr, sub='motors, safety, sensors, ESP-NOW to the bank')
    P, I, E = WIRE['pwm'], WIRE['isense'], WIRE['en']
    d.hvh(c['IO13 PWM'], drv[0]['RPWM'], 902, P)
    d.hvh(c['IO34 IS'], drv[0]['IS'], 892, I)
    d.hvh(c['IO14 PWM'], drv[1]['RPWM'], 882, P)
    d.hvh(c['IO35 IS'], drv[1]['IS'], 872, I)
    d.hvh(c['IO18 RPWM'], drv[2]['RPWM'], 862, P)
    d.hvh(c['IO19 LPWM'], drv[2]['LPWM'], 852, P)
    d.hvh(c['IO36 IS'], drv[2]['IS'], 842, I)
    bx = 924
    d.wire([c['IO4 EN'], (bx, c['IO4 EN'][1])], E)
    d.wire([(bx, drv[0]['EN'][1]), (bx, drv[2]['EN'][1])], E)
    for a in drv:
        d.wire([(bx, a['EN'][1]), a['EN']], E); d.junction(bx, a['EN'][1])
    d.junction(bx, c['IO4 EN'][1])
    d.text(900, 78, 'PWM (blue), enable (purple), current sense (orange)', size=12, fill='#4d646b', layer=d.tags)
    d.text(900, 94, 'EN is held low by a pull-down: drivers start OFF', size=12, fill='#4d646b', layer=d.tags)
    d.rail(c['IO39 VBAT'], '12V', 'r', text='12 V ÷')
    d.rail(c['VIN'], '5V', 'r'); d.rail(c['GND'], 'GND', 'r'); d.rail(c['3V3'], '3V3', 'r')

    # ---- bow camera ----
    bow, _ = devkit(d, 1400, 100, 170, 'ESP32-CAM Type C (bow camera)', ['U0T TX', 'U0R RX', '5V', 'GND'], [], camera='cam',
                    sub='object detector, navigation')
    d.wire([c['IO16 RX'], bow['U0T TX']], WIRE['tx'], 'bow TX → IO16 RX')
    d.wire([c['IO17 TX'], bow['U0R RX']], WIRE['rx'], 'IO17 TX → bow RX')
    d.rail(bow['5V'], '5V', 'l'); d.rail(bow['GND'], 'GND', 'l')

    # ---- sorting camera ----
    s3, _ = devkit(d, 1400, 340, 170, 'ESP32-S3 N16R8 CAM (belt camera)', ['TX', 'RX', '5V', 'GND', '3V3'],
                   ['SERVO', 'LED GATE', 'SDA', 'SCL'], camera='cam_s3', sub='CNN, sorting, microSD log, Wi-Fi page')
    d.hvh(c['IO32 RX'], s3['TX'], 1236, WIRE['tx'])
    d.hvh(c['IO33 TX'], s3['RX'], 1244, WIRE['rx'])
    d.rail(s3['5V'], '5V', 'l'); d.rail(s3['GND'], 'GND', 'l'); d.rail(s3['3V3'], '3V3', 'l')

    # ---- sensors on the controller ----
    mpu, _ = sensor(d, 1400, 640, 'MPU6050 tilt sensor', ['VCC', 'GND', 'SCL', 'SDA'], '#6c3483', 'MPU6050')
    qmc, _ = sensor(d, 1400, 830, 'QMC5883L compass (optional)', ['VCC', 'GND', 'SCL', 'SDA'], '#34495e', 'QMC')
    jl, _ = sensor(d, 1400, 1020, 'JSN-SR04T left sonar', ['VCC', 'TRIG', 'ECHO', 'GND'], '#1f5fae', 'JSN', probe=True)
    jr, _ = sensor(d, 1400, 1190, 'JSN-SR04T right sonar', ['VCC', 'TRIG', 'ECHO', 'GND'], '#1f5fae', 'JSN', probe=True)
    sw = microswitch(d, 1400, 1380, 'Bump switches (2, in parallel)')
    for s_ in (mpu, qmc):
        d.rail(s_['VCC'], '3V3', 'l'); d.rail(s_['GND'], 'GND', 'l')
    for s_ in (jl, jr):
        d.rail(s_['VCC'], '5V', 'l'); d.rail(s_['GND'], 'GND', 'l')
    d.rail(sw['B'], 'GND', 'r')
    sx, sc = 1252, 1260
    d.wire([c['IO21 SDA'], (sx, c['IO21 SDA'][1]), (sx, qmc['SDA'][1]), qmc['SDA']], WIRE['sda'], 'SDA', lpos=(1190, 292))
    d.wire([(sx, mpu['SDA'][1]), mpu['SDA']], WIRE['sda']); d.junction(sx, mpu['SDA'][1])
    d.wire([c['IO22 SCL'], (sc, c['IO22 SCL'][1]), (sc, qmc['SCL'][1]), qmc['SCL']], WIRE['scl'], 'SCL', lpos=(1190, 320))
    d.wire([(sc, mpu['SCL'][1]), mpu['SCL']], WIRE['scl']); d.junction(sc, mpu['SCL'][1])
    d.hvh(c['IO23 TRIG'], jl['TRIG'], 1268, WIRE['trig'])
    d.hvh(c['IO25 ECHO'], jl['ECHO'], 1276, WIRE['echo'])
    d.hvh(c['IO5 TRIG'], jr['TRIG'], 1284, WIRE['trig'])
    d.hvh(c['IO26 ECHO'], jr['ECHO'], 1292, WIRE['echo'])
    d.hvh(c['IO27 BUMP'], sw['A'], 1300, WIRE['sig'])

    # ---- sorting-board peripherals ----
    srv = servo(d, 1810, 380, 'MG996R gate servo')
    d.wire([s3['SERVO'], (1650, s3['SERVO'][1]), (1650, srv['SIG'][1]), srv['SIG']], WIRE['pwm'], 'PWM', lpos=(1720, srv['SIG'][1] - 6))
    d.rail(srv['V+'], '5V', 'l', text='5 V servo'); d.rail(srv['GND'], 'GND', 'l')
    q = mosfet(d, 1810, 520, 'Logic-level MOSFET')
    d.wire([s3['LED GATE'], (1630, s3['LED GATE'][1]), (1630, 680), (q['G'][0], 680), q['G']], WIRE['gate'], 'LED gate', lpos=(1730, 674))
    strip = led_strip(d, 2000, 640, 130, '12 V LED strip (hood)')
    d.wire([q['D'], (q['D'][0], 700), (1975, 700), (1975, strip['-'][1]), strip['-']], BLK)
    d.rail(strip['+'], '12V', 'u', text='12 V · F4')
    d.rail(q['S'], 'GND', 'd', stub=24)
    rtc, _ = sensor(d, 1810, 820, 'DS3231 clock (optional)', ['VCC', 'GND', 'SCL', 'SDA'], '#1abc9c', 'DS3231')
    d.wire([s3['SDA'], (1610, s3['SDA'][1]), (1610, rtc['SDA'][1]), rtc['SDA']], WIRE['sda'])
    d.wire([s3['SCL'], (1590, s3['SCL'][1]), (1590, rtc['SCL'][1]), rtc['SCL']], WIRE['scl'])
    d.rail(rtc['VCC'], '3V3', 'l'); d.rail(rtc['GND'], 'GND', 'l')

    legend(d, 40, 1150, 640, 300, [
        'Pins are drawn in a convenient order, not the physical board order.',
        'Lines that cross are NOT connected unless there is a black dot.',
        'Left out to keep it readable (all in the KiCad schematic): pull-down',
        'resistors, 1k current-sense resistors, echo dividers, bulk capacitors,',
        'and the 100k/33k battery divider behind the "12 V ÷" tag.',
        'Each BTS7960 shows its tied pairs as one pad: R_EN + L_EN = EN,',
        'R_IS + L_IS = IS. Thruster drivers tie LPWM to ground.',
        'Fuses: F1-F3 5 A (motors), F4 3 A (bucks, LED), 15 A main.',
    ])
    d.save('../SAGIP_Wiring_Boat.svg', '../SAGIP_Wiring_Boat.png', scale=1.0)
    return d


# ====================================================================== FLOOD NODE
def flood():
    d = Diagram(1900, 1000, 'SAGIP flood node wiring', 'On the bank, runs by itself. Wakes from deep sleep when a float switch closes, then tells the boat over ESP-NOW.')
    sp = solar(d, 60, 140, 190, 110, '2 W 5 V solar panel', cols=4, rows=3, fr=(0.3, 0.7))
    x, y, w, h = 420, 120, 250, 190
    d.rect(x, y, w, h, '#1f5fae', stroke='#0b2a55', sw=2, rx=8)
    d.rect(x + 80, y + 60, 56, 60, '#1b1b1b', stroke='#000', sw=1, rx=3)
    d.text(x + 108, y + 94, '4056', size=12, fill='white', anchor='middle')
    tp = {}
    for nm, px, py, side in (('IN+', x, y + 36, 'l'), ('IN-', x, y + h - 36, 'l'), ('OUT+', x + w, y + 36, 'r'), ('B+', x + w, y + 78, 'r'),
                             ('B-', x + w, y + 120, 'r'), ('OUT-', x + w, y + 162, 'r')):
        d.pad(px, py)
        d.text(px + (14 if side == 'l' else -14), py + 4, nm, size=12, fill='white', anchor='start' if side == 'l' else 'end', weight='bold')
        tp[nm] = (px, py)
    d.title_under(x + w / 2, y + h + 26, 'TP4056 charger module', 'the protected version (has a protection chip)')
    d.wire([sp['+'], (sp['+'][0], 280), (350, 280), (350, tp['IN+'][1]), tp['IN+']], RED)
    d.wire([sp['-'], (sp['-'][0], 300), (370, 300), (370, tp['IN-'][1]), tp['IN-']], BLK)
    cx, cy = 800, 150
    d.rect(cx, cy, 120, 210, '#2e8b57', stroke='#0b3d22', sw=2, rx=14)
    d.text(cx + 60, cy + 100, '18650', size=17, fill='white', anchor='middle', weight='bold')
    d.text(cx + 60, cy + 124, 'protected cell', size=12, fill='#d9f0e2', anchor='middle')
    d.text(cx + 60, cy + 144, 'in an IP67 box', size=12, fill='#d9f0e2', anchor='middle')
    cell = {'+': (cx - 0, cy + 60), '-': (cx, cy + 150)}
    d.pad(*cell['+']); d.pad(*cell['-'])
    d.text(cx + 12, cy + 64, '+', size=14, fill='white', weight='bold'); d.text(cx + 12, cy + 154, '-', size=14, fill='white', weight='bold')
    d.wire([tp['B+'], (730, tp['B+'][1]), (730, cell['+'][1]), cell['+']], RED)
    d.wire([tp['B-'], (715, tp['B-'][1]), (715, cell['-'][1]), cell['-']], BLK)
    mt = buck(d, 420, 520, 'MT3608 boost to 5 V', w=170, h=100)
    d.wire([tp['OUT+'], (700, tp['OUT+'][1]), (700, 440), (330, 440), (330, mt['IN+'][1]), mt['IN+']], RED)
    d.wire([tp['OUT-'], (685, tp['OUT-'][1]), (685, 460), (310, 460), (310, mt['IN-'][1]), mt['IN-']], BLK)
    d.rail(mt['OUT+'], '5V', 'r'); d.rail(mt['OUT-'], 'GND', 'r')
    L = ['VIN', 'GND', '3V3', 'IO32 WATCH', 'IO33 ALERT', 'IO25 DANGER', 'IO26 BUZZER', 'IO27 LED']
    k, kh = devkit(d, 1250, 140, 190, 'ESP32 DevKit (flood node)', L, [], sub='deep sleep, wakes on any float switch')
    d.rail(k['VIN'], '5V', 'l'); d.rail(k['GND'], 'GND', 'l'); d.rail(k['3V3'], '3V3', 'l')
    for nm, pin in (('Watch', 'IO32 WATCH'), ('Alert', 'IO33 ALERT'), ('Danger', 'IO25 DANGER')):
        py = k[pin][1]; fx = 1060
        d.rect(fx, py - 12, 76, 24, '#f4f4ee', stroke='#777', sw=1.4, rx=12, layer=d.tags)
        d.circle(fx + 14, py, 6, '#e74c3c', stroke='#600', sw=1, layer=d.tags)
        d.text(fx + 46, py + 4, nm, size=11, weight='bold', anchor='middle', layer=d.tags)
        d.wire([(fx + 76, py), k[pin]], WIRE['sig'])
        d.wire([(fx, py), (fx - 14, py)], WIRE['pwr'])
        d.pill(fx - 16, py, '3.3 V', RAIL['3V3'][0], 'right')
    d.text(1000, 112, 'Each float switch joins its pin to 3.3 V when water lifts it.', size=12, fill='#4d646b', layer=d.tags)
    d.text(1000, 128, 'A 100k pull-down on each pin (in KiCad) keeps it low when open.', size=12, fill='#4d646b', layer=d.tags)
    bz_x, bz_y = 1600, 330
    d.circle(bz_x + 50, bz_y + 40, 50, '#1b1b1b', stroke='#000', sw=2)
    d.circle(bz_x + 50, bz_y + 40, 10, '#444', stroke='#777', sw=1.4)
    d.text(bz_x + 28, bz_y + 30, '+', size=18, fill='#e74c3c', weight='bold')
    bz = {'+': (bz_x + 50, bz_y - 10), '-': (bz_x + 50, bz_y + 90)}
    d.pad(*bz['+']); d.pad(*bz['-'])
    d.title_under(bz_x + 50, bz_y + 120, 'Active buzzer 5 V')
    d.rail(bz['+'], '5V', 'u', stub=24)
    qx, qy = 1600, 580
    d.rect(qx + 8, qy, 72, 50, '#1b1b1b', stroke='#000', sw=1.6, rx=24)
    d.rect(qx + 8, qy + 30, 72, 20, '#1b1b1b', stroke='none', sw=0, rx=0)
    d.text(qx + 44, qy + 30, 'S8050', size=11, fill='white', anchor='middle', weight='bold')
    q = {}
    for i, nm in enumerate(('E', 'B', 'C')):
        px = qx + 20 + i * 24
        d.line(px, qy + 50, px, qy + 86, stroke='#c9ced3', sw=4)
        d.pad(px, qy + 86, 6.5); q[nm] = (px, qy + 86)
        d.text(px, qy + 106, nm, size=10, anchor='middle', layer=d.tags)
    d.title_under(qx + 44, qy + 150, 'NPN transistor (drives the buzzer)')
    d.wire([bz['-'], (bz['-'][0], 530), (q['C'][0] + 70, 530), (q['C'][0] + 70, q['C'][1] + 40), (q['C'][0], q['C'][1] + 40), q['C']], WIRE['sig'])
    d.rail(q['E'], 'GND', 'l', stub=50)
    r1, r2 = resistor(d, 1450, 700, '1k')
    d.wire([k['IO26 BUZZER'], (1220, k['IO26 BUZZER'][1]), (1220, 700), r1], WIRE['gate'], 'IO26', lpos=(1235, 694))
    d.wire([r2, (1530, 700), (1530, q['B'][1] + 24), (q['B'][0], q['B'][1] + 24), q['B']], WIRE['gate'])
    lx, ly = 1600, 800
    d.circle(lx + 30, ly + 24, 24, '#e74c3c', stroke='#600', sw=1.8)
    d.rect(lx + 6, ly + 24, 48, 22, '#e74c3c', stroke='#600', sw=1.8, rx=0)
    d.rect(lx + 2, ly + 44, 56, 6, '#c0392b', stroke='#600', sw=1.4, rx=1)
    la, lk = (lx + 20, ly + 84), (lx + 40, ly + 84)
    d.line(la[0], ly + 50, la[0], la[1], stroke='#c9ced3', sw=4); d.line(lk[0], ly + 50, lk[0], lk[1], stroke='#c9ced3', sw=4)
    d.pad(*la, 6.5); d.pad(*lk, 6.5)
    d.title_under(lx + 30, ly + 150, 'Status LED')
    r3, r4 = resistor(d, 1400, 880, '330')
    d.wire([k['IO27 LED'], (1200, k['IO27 LED'][1]), (1200, 880), r3], WIRE['gate'], 'IO27', lpos=(1215, 874))
    d.wire([r4, (1470, 880), (1470, 930), (la[0], 930), la], WIRE['gate'])
    d.rail(lk, 'GND', 'd', stub=14)
    legend(d, 40, 700, 520, 260, [
        'Lines that cross are NOT connected unless there is a black dot.',
        'The ESP32 wakes on any HIGH input, so the float switches connect',
        'to 3.3 V and each input has a 100k pull-down to ground.',
        'ESP-NOW is the radio inside the ESP32: nothing to wire. It sends',
        'the water level to the boat controller, which stays docked from',
        'the alert level.',
        'Sleep current depends on the boards, measure it before the pitch.',
    ])
    d.save('../SAGIP_Wiring_FloodNode.svg', '../SAGIP_Wiring_FloodNode.png', scale=1.0)
    return d


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    if which in ('boat', 'both'):
        boat(); print('boat saved')
    if which in ('flood', 'both'):
        flood(); print('flood saved')

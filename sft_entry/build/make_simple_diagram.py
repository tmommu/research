"""Simplified block diagram of the SAGIP electronics -> ../SAGIP_Simplified_Diagram.png (needs matplotlib)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(17, 10.8))
ax.set_xlim(0, 172); ax.set_ylim(-3, 107); ax.axis('off')
INK = '#1b2b34'
FILL = dict(power='#fde2d4', brain='#d7e8fb', sense='#e3f2e1', act='#fff0c2', node='#e8dff5')
RED, ORG, BLU, GRN = '#c0392b', '#e67e22', '#2471a3', '#1e8449'


def box(x, y, w, h, text, fc, fs=9.5, tag=None, tagc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.25,rounding_size=1.2', fc=fc, ec=INK, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, color=INK, linespacing=1.3)
    if tag:
        ax.text(x + w - 0.8, y + h + 0.1, tag, fontsize=7.5, color='white', fontweight='bold', ha='right', va='center',
                bbox=dict(boxstyle='round,pad=0.25', fc=tagc, ec='none'), zorder=5)
    return (x, y, w, h)


def arrow(p, q, color, lw=2.0, ls='-', both=False):
    ax.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='<|-|>' if both else '-|>', color=color, lw=lw, ls=ls,
                                                      shrinkA=0, shrinkB=0, mutation_scale=14))


def label(x, y, text, color, fs=8.3, ha='center', va='center'):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color=color, fontweight='bold', linespacing=1.25)


ax.text(2, 105, 'SAGIP electronics, simplified', fontsize=21, fontweight='bold', color='#0b5d8f', va='center')
ax.text(2, 101, 'Boat on the water, flood node on the bank. Full detail: kicad/SAGIP.kicad_sch', fontsize=10.5, color='#4d646b', va='center')

# ------------------------------------------------------------------ boat power chain
label(2, 97.3, 'BOAT POWER', RED, fs=11, ha='left')
xs = [2, 27, 52, 77, 104]
ws = [20, 20, 20, 22, 26]
txt = ['30 W solar\npanel', '20 A charge\ncontroller', '12 V 12 Ah\nlead-acid battery', '15 A fuse, master\nswitch, 4 branch\nfuses', '2 x 5 V buck\nconverters\n(logic, servo)']
bx = []
for x, w, t in zip(xs, ws, txt):
    bx.append(box(x, 85.5, w, 10, t, FILL['power'], fs=9))
for a, b in zip(bx, bx[1:]):
    arrow((a[0] + a[2], 90.5), (b[0], 90.5), RED)

# notes in the free space
notes = ['How to read this',
         '',
         'Red tag = 12 V from a branch fuse.',
         'Orange tag = 5 V from a buck converter.',
         '',
         'One buck feeds every board and sensor.',
         'A second buck feeds only the gate servo,',
         'so servo current spikes cannot reset a board.',
         '',
         'All three motor drivers start OFF: the enable',
         'line is pulled to ground until the controller',
         'raises it.',
         '',
         'The camera boards have too few free pins, so',
         'a third ESP32 (the boat controller) runs the',
         'motors, sensors and safety checks.']
for i, t in enumerate(notes):
    ax.text(2, 79 - i * 2.55, t, fontsize=9.2, color=INK, fontweight='bold' if i == 0 else 'normal', va='center')

# ------------------------------------------------------------------ boat brains (stacked so every link is one short arrow)
bow = box(96, 58, 32, 11, 'ESP32-CAM Type C\nBOW camera\nobject detector (navigation)', FILL['brain'], tag='5 V', tagc=ORG)
ctl = box(96, 34, 32, 16, 'ESP32 DevKit\nBOAT CONTROLLER\nmotors, safety, sensors,\nESP-NOW to the bank', FILL['brain'], tag='5 V', tagc=ORG)
s3 = box(96, 12, 32, 14, 'ESP32-S3 N16R8 CAM\nBELT camera + CNN\nsorting, phone Wi-Fi page', FILL['brain'], tag='5 V', tagc=ORG)
sd = box(96, 0.5, 32, 7.5, 'microSD log + DS3231\nclock (optional)', FILL['sense'], fs=9)
arrow((112, 58), (112, 50.4), BLU, both=True); label(110.5, 54.2, 'UART: plastic position', BLU, ha='right')
arrow((112, 34), (112, 26.4), BLU, both=True); label(110.5, 30.2, 'UART: counts, status', BLU, ha='right')
arrow((112, 12), (112, 8.4), BLU, both=True)

# sensors in
sen = box(52, 41, 38, 12, 'Tilt MPU6050, compass (optional)\n2 x JSN-SR04T side sonar\nbump switches, battery voltage', FILL['sense'], fs=9, tag='3.3 / 5 V', tagc=ORG)
arrow((90, 47), (96, 47), BLU)
label(71, 55.2, 'I2C, echo pulses, switch inputs', BLU, fs=8)

# drivers and motors
drv = box(52, 28, 38, 9.5, '3 x BTS7960 motor drivers\n(PWM, enable, current sense)', FILL['act'], fs=9, tag='12 V', tagc=RED)
arrow((90, 36), (96, 36), BLU, both=True)
mot = box(2, 28, 36, 9.5, 'Left and right thrusters\n+ conveyor belt motor', FILL['act'], fs=9, tag='12 V', tagc=RED)
arrow((52, 32.8), (38, 32.8), RED)

# sorting-side actuators
srv = box(52, 17, 38, 8, 'MG996R gate servo', FILL['act'], fs=9, tag='5 V servo rail', tagc=ORG)
arrow((96, 21), (90, 21), BLU); label(93, 22.6, 'PWM', BLU, fs=7.5)
hl = box(52, 6, 38, 8, 'Hood LED strip via MOSFET', FILL['act'], fs=9, tag='12 V', tagc=RED)
arrow((96, 13.5), (90, 11), BLU)

# ------------------------------------------------------------------ flood node column
label(140, 97.3, 'FLOOD NODE ON THE BANK', '#6c3483', fs=11, ha='left')
n = []
n.append(box(140, 85.5, 28, 10, '2 W 5 V solar panel', FILL['node'], fs=9))
n.append(box(140, 72, 28, 10, 'TP4056 charger\nwith protection', FILL['node'], fs=9))
n.append(box(140, 58.5, 28, 10, 'Protected 18650\nin an IP67 box', FILL['node'], fs=9))
n.append(box(140, 48, 28, 7.5, 'MT3608 boost to 5 V', FILL['node'], fs=9))
n.append(box(140, 36, 28, 10, 'ESP32 DevKit\ndeep sleep, float-switch wake', FILL['node'], fs=8.6))
n.append(box(140, 22.5, 28, 9, '3 float switches\n(watch, alert, danger)', FILL['sense'], fs=9))
n.append(box(140, 9.5, 28, 9, 'Buzzer + status LED', FILL['act'], fs=9))
for a, b in zip(n[:4], n[1:5]):
    arrow((154, a[1]), (154, b[1] + b[3]), ORG)
arrow((154, n[5][1] + n[5][3]), (154, n[4][1]), BLU)
ax.plot([168, 170.6, 170.6], [39.5, 39.5, 14], color=BLU, lw=2.0)
arrow((170.6, 14), (168, 14), BLU)
arrow((128, 42), (140, 41), GRN, lw=2.4, ls=(0, (5, 3)), both=True)
label(134, 46.2, 'ESP-NOW', GRN, fs=8.2)

# ------------------------------------------------------------------ legend
ly = -1.2
ax.plot([2, 10], [ly, ly], color=BLU, lw=2.2); ax.text(11.5, ly, 'signal or serial', fontsize=8.8, va='center', color=INK)
ax.plot([36, 44], [ly, ly], color=GRN, lw=2.4, ls=(0, (5, 3))); ax.text(45.5, ly, 'wireless (ESP-NOW)', fontsize=8.8, va='center', color=INK)
ax.plot([76, 84], [ly, ly], color=RED, lw=2.2); ax.text(85.5, ly, '12 V power', fontsize=8.8, va='center', color=INK)
ax.plot([103, 111], [ly, ly], color=ORG, lw=2.2); ax.text(112.5, ly, '5 V power', fontsize=8.8, va='center', color=INK)
ax.text(135, ly, 'Planning design, confirm against the parts bought.', fontsize=8.2, va='center', color='#4d646b')
fig.savefig('../SAGIP_Simplified_Diagram.png', dpi=150, bbox_inches='tight', facecolor='white')
print('saved')

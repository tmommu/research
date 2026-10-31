import re, sys
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_COLOR_INDEX, WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

d = docx.Document("tplproto.docx")
body = d.element.body
for el in list(body):
    if el.tag != qn('w:sectPr'):
        body.remove(el)
BLUE = RGBColor(0x0B, 0x5D, 0x8F)
TOK = re.compile(r'(\*\*.+?\*\*|\[[^\]]+\])')

def add_text(p, text, size=None, bold=None, italic=None):
    for part in TOK.split(text):
        if not part: continue
        if part.startswith('**'):
            r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith('['):
            r = p.add_run(part); r.font.highlight_color = WD_COLOR_INDEX.YELLOW
            if bold: r.bold = True
        else:
            r = p.add_run(part)
            if bold: r.bold = True
        if size: r.font.size = Pt(size)
        if italic: r.italic = True

def title(t):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(17); r.font.color.rgb = BLUE
def h(t):
    p = d.add_paragraph(); p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3); p.paragraph_format.keep_with_next = True
    r = p.add_run(t); r.bold = True; r.font.size = Pt(13); r.font.color.rgb = BLUE
def para(t, **k):
    p = d.add_paragraph(); add_text(p, t, **k); return p
def bullet(label, t):
    p = d.add_paragraph(style='List Bullet'); p.paragraph_format.space_after = Pt(1)
    r = p.add_run(label); r.bold = True
    add_text(p, t)
def fig(path, w, cap):
    d.add_picture(path, width=Inches(w)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(cap); r.italic = True; r.font.size = Pt(8.5)
def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr(); s = OxmlElement('w:shd')
    s.set(qn('w:val'), 'clear'); s.set(qn('w:color'), 'auto'); s.set(qn('w:fill'), fill); tcPr.append(s)
def table(rows, widths, bold_rows=()):
    t = d.add_table(rows=len(rows), cols=len(widths)); t.style = 'Table Grid'; t.autofit = False
    for ci, w in enumerate(widths): t.columns[ci].width = Inches(w)
    for ri, row in enumerate(rows):
        for ci, v in enumerate(row):
            c = t.cell(ri, ci); c.width = Inches(widths[ci])
            p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(1); p.paragraph_format.space_before = Pt(1)
            add_text(p, v, size=9.5, bold=(ri == 0 or ri in bold_rows))
            if ri == 0: shade(c, 'DCEBF5')
            if ci == len(widths) - 1 and re.fullmatch(r'[+\d,]+( to [\d,]+)?( \(.*\))?', v or ''): p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    d.add_paragraph().paragraph_format.space_after = Pt(0)

title("SAGIP: Autonomous Solar Skimmer Boat with On-Chip AI (Prototype Design)")
para("Quick visual of what we will build and buy. Quezon City Science High School, Grade 10 team. Adviser: Skjoukje U. Jemoya. All costs and sizes are planning estimates.")

h("1. What it is")
para("A solar-powered robot boat, about 1.5 m long, patrols a creek between two floating barriers. A bow camera spots floating debris, the boat steers to it, and a scoop lifts it onto a "
     "conveyor. A second camera under a hood names each item with a small 2D convolutional neural network (CNN), and a servo gate sorts plastic and plants into two bins. "
     "A weekly offline report goes to the barangay. A separate float-switch node on the bank sounds a flood alarm.")
fig("fig_boat_side.png", 6.6, "Side view of the SAGIP boat (schematic).")
fig("fig_patrol.png", 6.6, "Patrol, detect, scoop and dock (top view, schematic).")

h("2. Parts and what each does")
table([("No.", "Part", "What it does"),
       ("1", "Bow camera (ESP32-CAM)", "Spots floating debris ahead so the boat can steer to it"),
       ("2", "Scoop", "Lifts debris onto the belt"),
       ("3", "Cleated conveyor belt", "Carries items up in a single layer"),
       ("4", "Belt camera and CNN (ESP32-S3)", "Names each item under a lit hood"),
       ("5", "Servo gate and two bins", "Plastic to Bin A, plants or unsure items to Bin B"),
       ("6", "Electronics box", "Two ESP32 boards, drivers, converters"),
       ("7", "30 W solar panel", "Flat roof over the deck, charges the battery"),
       ("8", "12 V 12 Ah battery", "Powers thrusters, belt and boards, kept low between the floats"),
       ("9", "Two thrusters", "Steer by differential thrust"),
       ("10", "Side sensors and compass", "Follow the bank, turn at the barriers, tilt cut-off"),
       ("11", "Twin 6-inch PVC floats and deck", "Keep it afloat and stable"),
       ("12", "Flood node on the bank", "Three float switches and a buzzer, boat stays docked from the alert level")],
      [0.5, 2.3, 3.6])

h("3. Why it is built this way")
bullet("Hyacinth: ", "water hyacinth mats carried most of the floating plastic counted in a Saigon River study (Schreyers et al., 2021), so the detector separates plants and the propellers are shrouded.")
bullet("Rain pulses: ", "floating plastic transport rose up to six times at peak river flow (van Emmerik et al., 2022), so the boat logs every item with time and the flood node logs the water level.")
bullet("On-chip AI: ", "INT8 quantization shrinks a model about fourfold (Gholami et al., 2021) and TensorFlow Lite for Microcontrollers runs it on an ESP32 (David et al., 2021).")
bullet("Set patrol, no GPS: ", "the creek banks and two barriers define the route, so the boat needs only side sensors, a compass and bump switches.")
bullet("Stability: ", "twin floats with a wide beam, the battery low between them, foam fill, and a tilt cut-off. Float and tilt tests come first.")

h("4. How it works")
bullet("Patrol: ", "follows the bank, turns at the upstream barrier, returns to the dock when the bins are full or the battery is low. Staff can take over with a phone remote.")
bullet("Detect and scoop: ", "a tiny detector boxes debris and separates plastic from plants. The boat steers toward plastic and the scoop lifts it onto the belt.")
bullet("Count and sort: ", "the CNN names each item. Plastic goes to Bin A, plants and low-confidence items go to Bin B. Weekly hand counts check accuracy.")
bullet("Protect: ", "belt and thruster current is monitored. A jam triggers a short reverse, up to three retries, then a stop. Drivers default to off.")
bullet("Plastic accounting: ", "counts become estimated kilograms and recovery value, corrected by a weekly weigh-in, in an evidence sheet for the barangay and the DENR.")
bullet("Flood warning: ", "three float switches on a staff gauge set watch, alert and danger levels. A buzzer and beacon sound, and the level is logged.")

h("5. Power and wiring")
fig("fig_wiring.png", 6.6, "Block schematic of the boat and the flood node (schematic).")
bullet("Planning figures: ", "a 30 W panel yields about 54 Wh a day. A 20-minute patrol uses about 25 Wh. The 12 V 12 Ah battery stores about 144 Wh, with about 72 Wh usable. We will measure these on the bench.")
bullet("Protection: ", "each motor has its own fuse and driver, the master switch cuts everything, and a low-battery rule skips patrols.")

h("6. Materials and cost (estimated online-shop prices, to be confirmed)")
table([("Item", "PHP"),
       ("Two 6-inch PVC floats with foam fill, frame and deck", "2,300"),
       ("Two 12 V thrusters and dual driver", "1,800"),
       ("Short cleated conveyor, gear motor and driver", "2,000"),
       ("ESP32-S3 camera board, hood, LED, enclosure", "1,850"),
       ("ESP32-CAM bow detector", "600"),
       ("Compass with tilt sensor, three waterproof ultrasonic sensors, bump switches", "900"),
       ("Gate servo and reused bins", "300"),
       ("12 V 12 Ah battery, converters, fuses, wiring", "2,400"),
       ("30 W solar panel and 20 A controller (Shopee listing at about 1,084)", "1,100"),
       ("Waterproofing and hardware", "500"),
       ("Flood node with three float switches, buzzer, mini panel, cell, staff gauge", "1,000"),
       ("Bank dock and two barriers (rope, floats, post from the barangay)", "600"),
       ("Subtotal", "15,350"), ("Contingency", "650"), ("Pilot total", "16,000")],
      [5.2, 1.2], bold_rows=(13, 14, 15))
para("Materials: PVC floats and deck, PVC or plastic stock for the scoop and belt frame, stainless fasteners, an IP65 box for the electronics. These are pilot-grade and should last months. "
     "At scale we would standardize to HDPE pipe floats and sturdier belts. Tools to borrow: soldering iron, multimeter, drill, saw, pliers, kitchen scale.")

h("7. What we expect (to be tested, not promised)")
para("Removal: at least 50% of the floating debris entering a 30 m patrol stretch against a baseline week, at least 20 kg lifted in 8 weeks and at least 1,000 classified items. "
     "Counting: weekly counts within 15% of a trained hand audit, and at least 85% precision and recall on photographs from unseen places. Flood alarm: sounds at all three marks in a bucket test.")
para("Limits: people must still empty the bins, clear snags and wipe the lenses, and we will log those hours. The boat covers one creek stretch and cannot lift heavy or tangled items.", size=10)

h("8. Build plan")
para("Nov 2: entry due. Nov 9 to 13: screening. If shortlisted, Nov 16 to Dec 5: finish Stage 1 on a bench (conveyor, camera, CNN, battery, panel), build a scaled boat mock-up and the flood node, and a 3D model and wiring schematic. "
     "Dec 7: 30-minute pitch with a bench demo. Creek pilot January to February 2027 if supported. Stage gates: model reaches 85% on held-out photos, float and tilt tests pass, the boat reaches and scoops at least 70% of 20 floating items in a pond, "
     "and the flood alarm sounds at all three marks.")
para("Sources: David et al. (2021), Proceedings of Machine Learning and Systems 3. Gholami et al. (2021), arXiv:2103.13630. Schreyers et al. (2021), Frontiers in Environmental Science 9, 686334. van Emmerik et al. (2022), Earth's Future 10, e2022EF002811. Full list in the written entry.", size=9)
d.save("SAGIP_SFT2026_Prototype_Design.docx")
print("saved")

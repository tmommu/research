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

title("SAGIP: Floating Solar-Powered Estero Guardian with On-Chip AI (Prototype Design)")
para("Quick visual of what we will build and buy. Quezon City Science High School, Grade 10 team. Adviser: Skjoukje U. Jemoya.")

h("1. What it is")
para("One floating, moored, solar-powered raft in the estero. A boom and a filter catch plastic, a small arm lifts it up a ramp, a camera on a mast names each item "
     "with a 2D convolutional neural network (CNN) on the chip, and a servo gate sorts it into two bins. A weekly offline report goes to the barangay. "
     "The same chip also watches the water level for blockages.")
fig("fig_cut.png", 6.6, "Cutaway of the floating SAGIP unit, with the electronics box opened (schematic).")

h("2. Why it is built this way")
bullet("Hyacinth: ", "water hyacinth mats carried most of the floating plastic counted in a Saigon River study (Schreyers et al., 2021), so the boom has a deflector and mats go to Bin B.")
bullet("Rain pulses: ", "floating plastic transport rose up to six times at peak river flow (van Emmerik et al., 2022), so the device logs every item with time and water level.")
bullet("On-chip AI: ", "INT8 quantization shrinks a model about fourfold (Gholami et al., 2021) and TensorFlow Lite for Microcontrollers runs it on an ESP32-S3 (David et al., 2021).")
bullet("Floating: ", "the raft rides the water level on its mooring lines, so the intake always sits at the surface. A haul line lets adults pull it ashore to empty the bins and to shelter from storms. It takes one side of the channel only.")

h("3. How it works")
bullet("Catch: ", "a boom of reused PET bottles with a net skirt guides plastic to the raft's bow. A wide-gapped deflector upstream lets hyacinth mats pass.")
bullet("Filter: ", "coarse bars, then a fine mesh basket at the bow, both sloped to shed leaves and mud.")
bullet("Lift: ", "a worm-gear motor on the deck turns a short rake arm in bursts. A shear pin protects the gearbox.")
bullet("Protect and adapt: ", "the chip reads motor current. It slows the motor under heavy load and speeds it up under light load. A jam triggers a short reverse, up to three retries, then a lockout and an alert. The driver defaults to off.")
bullet("Count and sort: ", "a hooded, LED-lit camera looks at a landing plate. The CNN names the item. A servo gate drops plastic into Bin A and plants or unsure items into Bin B. Every week students hand-count both bins to check it.")
bullet("Report: ", "an offline Wi-Fi page gives the weekly report and an anonymized open dataset, with time from a clock module. Counts are plotted against rainfall.")
bullet("Warn (secondary): ", "an ultrasonic sensor reads the water level against a painted staff gauge and alerts before a channel blocks.")

h("4. The electronics box")
bullet("Brain: ", "ESP32-S3 camera board with PSRAM, microSD card and clock module.")
bullet("Power: ", "a 10 W solar panel, a charge controller and two 18650 cells (about 18 Wh), with a fuse and master switch. The camera runs only when an item is present. Planning figures: about 6 Wh a day used and about 18 Wh a day produced.")
bullet("Safety: ", "low-voltage wiring in a sealed box with desiccant, a guarded arm with a stop switch and lockout, a motor driver that is off by default, and no student on the raft or in the water.")

h("5. Materials and cost (estimated local prices, to be confirmed)")
table([("Item", "Qty", "PHP"),
       ("ESP32-S3 camera board with PSRAM", "1", "1,300"), ("microSD card", "1", "150"), ("Clock module", "1", "100"),
       ("Sealed enclosure, glands, desiccant, light hood", "1", "300"), ("Waterproof ultrasonic level sensor", "1", "350"),
       ("10 W solar panel", "1", "800"), ("Charge controller, two 18650 cells, holder, converter", "1 set", "600"),
       ("Wiring, fuse, switch, connectors", "1 set", "250"), ("Two reused bins and painted staff gauge", "1 set", "150"),
       ("Worm-gear DC motor, motor driver", "2", "650"), ("Current and Hall sensing", "1 set", "150"), ("Servo with metal gears (sorter gate)", "1", "200"),
       ("Ramp, rake arm, coarse bars, fine mesh, shear pins", "1 set", "500"),
       ("Pontoons: four reused 200 L drums with sealed caps", "4", "2,000"),
       ("Deck frame and guard rails (marine plywood, aluminum angle or PVC)", "1 set", "1,900"),
       ("Boom arms, net skirt, bottle floats, rope", "1 set", "600"),
       ("Mooring: two anchors, swivels, rope, quick release, haul line, bank cleat", "1 set", "900"),
       ("Stainless hardware, sealant, waterproofing", "1 set", "600"),
       ("Subtotal", "", "11,500"), ("Contingency", "", "500"), ("Pilot total", "", "12,000")],
      [4.4, 0.8, 1.2], bold_rows=(19, 20, 21))
para("Materials: four sealed drums, a deck frame, PVC or plastic stock for the ramp and arm, stainless fasteners, UV-stable rope and an IP65 box. These are pilot-grade and should last months. "
     "Upgrades: HDPE pipe pontoons and stainless mesh. We will ask the barangay for drums, rope and bins in kind.")
para("Add-ons, only when a measured trigger fires:")
table([("Add-on or alternative", "PHP"),
       ("Bank-mounted version with a hinged float foot instead of the raft", "about 6,800 in total"),
       ("Belt conveyor in place of the rake arm (frame, belt, rollers, larger motor)", "+4,000 to 10,000 (unconfirmed)"),
       ("Second camera angle", "+1,300"),
       ("Larger battery for cloudy weeks", "+2,500 to 4,000 (unconfirmed)")], [4.4, 2.0])
para("Tools to borrow: soldering iron, multimeter or USB power meter, drill, saw, pliers, kitchen scale.")

h("6. What we expect (to be tested, not promised)")
para("Capture: we aim to capture at least 50% of the floating debris that reaches the boom against a baseline week, lift at least 20 kg in 8 weeks and log at least 1,000 classified items. "
     "Counting: weekly device counts within 15% of a trained hand audit, and at least 85% precision and recall on photographs from unseen places.")
para("Measurement details: Capture rate is kilograms lifted divided by kilograms lifted plus kilograms that pass the boom, estimated by downstream hand-net sampling. "
     "A baseline week before installation records the hand-net count, hyacinth cover and flow. The hand audit uses the same categories as NGO brand audits. "
     "If the arm cannot lift on solar power alone, the passive boom and bins continue and the camera still counts. Limits: people must still empty both bins weekly, "
     "clear the screen after storms, wipe the lens and check the battery. We will log those hours.", size=10)

h("7. Build steps")
para("Oct 30 to Nov 2: site visit, barangay letter, photographs and labels, bench power test. Nov 3 to 20: Stage 1 bench build with the CNN on the "
     "ESP32-S3, and a baseline week at the creek. Stage 2 raft and passive trap after a pond test with a 60 kg dummy load, then Stage 3 arm and sorter after a wet bench test with hyacinth, silt and a little "
     "cooking oil. Pilot December to February: weekly haul-in, emptying, hand count and report to the barangay.")
para("Sources: David et al. (2021), Proceedings of Machine Learning and Systems 3. Gholami et al. (2021), arXiv:2103.13630. Schreyers et al. (2021), Frontiers in Environmental Science 9, 686334. van Emmerik et al. (2022), Earth's Future 10, e2022EF002811. Full list in the written entry.", size=9)
d.save("SAGIP_SFT2026_Prototype_Design.docx")
print("saved")

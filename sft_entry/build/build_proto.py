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

title("SAGIP: Solar-Powered Estero Guardian with On-Chip AI (Prototype Design)")
para("Quick visual of what we will build and buy. Quezon City Science High School, Grade 10 team. Adviser: Skjoukje U. Jemoya.")

h("1. What it is")
para("One solar-powered unit on a creek bank. A floating boom guides plastic to a ramp, a small arm lifts it into a bin, and a camera on a post counts "
     "every item on the chip and triggers the arm. A weekly offline report goes to the barangay. The same chip also watches the water level for blockages.")
fig("fig_dev.png", 6.3, "The SAGIP unit at the creek bank (schematic).")

h("2. Why it is built this way")
bullet("Hyacinth: ", "water hyacinth mats carried most of the floating plastic counted in a Saigon River study (Schreyers et al., 2021), so the boom needs a deflector and the arm must tell plastic from vegetation.")
bullet("Rain pulses: ", "debris release in Greater Jakarta rose in the rainy season (Cordova & Nurhati, 2019), so the device logs every item with time and water level and we compare counts with rainfall.")
bullet("On-chip AI: ", "INT8 quantization shrinks a model about fourfold (Jacob et al., 2018) and TensorFlow Lite for Microcontrollers runs it on an ESP32-S3 (David et al., 2021), so no internet is needed.")

h("3. How it works")
bullet("Trap: ", "a boom of reused PET bottles and bamboo guides surface plastic to a bar screen at the foot of a ramp. A wide-gapped deflector upstream lets hyacinth mats pass.")
bullet("Lift: ", "a geared DC motor, mounted above the flood line, turns a rake arm that sweeps debris into a covered bin in short bursts, only when the camera sees plastic and not vegetation.")
bullet("Protect: ", "a shear pin protects the gearbox. Current and Hall sensing stop jams and slipping, with at most three retries and a driver that defaults to off.")
bullet("Count: ", "an ESP32-S3 camera looks down at the water only. An INT8 model classifies each item on the chip, and every week students hand-count the bin to check it.")
bullet("Report: ", "an offline Wi-Fi page gives the weekly report and an anonymized open dataset. Counts are plotted against rainfall to see whether plastic arrives in pulses.")
bullet("Warn (secondary): ", "an ultrasonic sensor reads the water level against a painted gauge and alerts before a channel blocks.")

h("4. The electronics box")
fig("fig_box.png", 6.0, "Electronics box, cover off (schematic).")
bullet("Brain: ", "ESP32-S3 camera board with PSRAM.")
bullet("Power: ", "a 6 to 10 W solar panel, a charge controller and two 18650 cells (about 18 Wh), with a fuse and master switch. Electronics draw about 6 Wh a day as a planning figure.")
bullet("Safety: ", "low-voltage wiring in a sealed box with desiccant, a guarded arm with a stop switch and lockout, a motor driver that is off by default, and no student in the water.")

h("5. Materials and cost (estimated local prices, to be confirmed)")
table([("Item", "Qty", "PHP"),
       ("ESP32-S3 camera board with PSRAM", "1", "1,300"), ("microSD card", "1", "200"),
       ("Sealed enclosure, glands, desiccant", "1", "300"), ("Waterproof ultrasonic level sensor", "1", "350"),
       ("Solar panel (about 6 to 10 W)", "1", "600"), ("Charge controller, two 18650 cells, holder, converter", "1 set", "700"),
       ("Rope, net, zip ties (bottles and bamboo reused)", "1 set", "450"), ("Anchor, post, clamps, concrete", "1 set", "350"),
       ("Bin (reused) and painted staff gauge", "1", "150"), ("Wiring, fuse, switch, connectors", "1 set", "250"),
       ("Small geared DC motor (6 to 7.4 V)", "1", "500"), ("Motor driver", "1", "200"),
       ("Current and motion sensing", "1 set", "150"), ("Ramp, rake arm, shaft, bar screen, spare shear pins", "1 set", "150"),
       ("Subtotal", "", "5,650"), ("Contingency", "", "350"), ("Pilot total", "", "6,000")],
      [4.4, 0.8, 1.2], bold_rows=(15, 16, 17))
para("Add-ons, only when a measured trigger fires:")
table([("Add-on", "PHP"),
       ("Belt conveyor in place of the rake arm (frame, belt, rollers, larger motor)", "+4,000 to 10,000 (unconfirmed)"),
       ("Second camera angle", "+1,300"),
       ("Larger solar panel and 12 V battery", "+2,500 to 4,000 (unconfirmed)")], [4.4, 2.0])
para("Tools to borrow: soldering iron, multimeter or USB power meter, drill, saw, pliers.")

h("6. What we expect (to be tested, not promised)")
para("Capture: we aim to lift at least [TARGET] kg of floating debris in 8 weeks and capture at least [X]% of what reaches the boom. Counting: weekly "
     "device counts within 15% of a trained hand audit, and at least 85% precision and recall on photographs from unseen places.")
para("**Measurement details: Capture rate is kilograms lifted divided by kilograms lifted plus kilograms that pass the boom, estimated by downstream "
     "hand-net sampling. A baseline week before installation records the hand-net count, hyacinth cover and flow. The hand audit uses the same categories "
     "as NGO brand audits. If the arm cannot lift on solar power alone, the passive boom and bin continue and the camera still counts.**")

h("7. Build steps")
para("Oct 28 to Nov 2: site visit, barangay letter, photographs and labels, bench power test. Nov 3 to 20: Stage 1 bench build with the model on the "
     "ESP32-S3, and a baseline week at the creek. Stage 2 passive trap, then Stage 3 arm and sensor after a wet bench test with hyacinth, silt and a little "
     "cooking oil. Pilot December to February: weekly emptying, hand count and report to the barangay.")
para("Sources: Cordova & Nurhati (2019), Scientific Reports 9, 18730. David et al. (2021), Proceedings of Machine Learning and Systems 3. Jacob et al. (2018), CVPR. Schreyers et al. (2021), Frontiers in Environmental Science 9, 686334. Full list in the written entry.", size=9)
d.save("SAGIP_SFT2026_Prototype_Design.docx")
print("saved")

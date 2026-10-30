import copy, sys
sys.path.insert(0, '.')
from pptx import Presentation
from lxml import etree
import content as C

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
def q(t): return '{%s}%s' % (A, t)

prs = Presentation('off.pptx')
S = list(prs.slides)
def shp(slide, idx): return [s for s in slide.shapes if s.name.startswith('Google Shape;%d;' % idx)][0]

def runs_of(p): return p.findall(q('r'))

class Shape:
    def __init__(self, sh):
        self.tb = sh.text_frame._txBody
        self.ps = self.tb.findall(q('p'))
        self.BOLD = copy.deepcopy(next(r for p in self.ps for r in runs_of(p) if r.find(q('rPr')).get('b') == '1'))
        self.NORM = copy.deepcopy(next(r for p in self.ps for r in runs_of(p) if r.find(q('rPr')).get('b') != '1'))
    def set(self, p, parts):
        """Replace the runs of template paragraph p with (bold, text) parts, keeping its own pPr."""
        for r in runs_of(p): p.remove(r)
        end = p.find(q('endParaRPr'))
        for bold, text in parts:
            r = copy.deepcopy(self.BOLD if bold else self.NORM)
            r.find(q('t')).text = text
            if end is not None: end.addprevious(r)
            else: p.append(r)
        return p
    def clone_after(self, src, ref, parts):
        p = copy.deepcopy(src); ref.addnext(p)
        return self.set(p, parts)

# ---------------- slide 1 ----------------
s1 = S[0]
title = shp(s1, 55).text_frame.paragraphs
title[0].runs[0].text = C.TITLE
title[1].runs[0].text = C.SCHOOL
th = shp(s1, 56).text_frame
ps = th.paragraphs
for r in ps[0].runs[1:]: r._r.getparent().remove(r._r)       # "(choose 1 and remove others)"
for p in ps[2:4]: p._p.getparent().remove(p._p)               # the other two themes
ps[1].runs[0].text = '- ' + C.THEME
tm = shp(s1, 54).text_frame.paragraphs
for i, name in enumerate(C.TEAM):
    for r in tm[i + 1].runs[1:]: r._r.getparent().remove(r._r)
    tm[i + 1].runs[0].text = name
adv = tm[6]
adv.runs[2].text = C.ADVISER
for r in (adv.runs[1], adv.runs[3]): r._r.getparent().remove(r._r)
adv.runs[1]._r.find(q('rPr')).attrib.pop('i', None)
adv.runs[1].text = ' ' + C.ADVISER
d0 = shp(s1, 57).text_frame.paragraphs[0]
d0.runs[0].text = C.DESC
for el in list(d0._p):
    if el.tag == q('br') or (el.tag == q('r') and el is not d0.runs[0]._r): d0._p.remove(el)

# ---------------- slide 2 ----------------
sh = Shape(shp(S[1], 62)); p = sh.ps
sh.set(p[1], [(False, "Philippine rivers rank first among countries for river plastic emissions (Meijer et al., 2021). "
                      "Cleanups weigh bulk waste and record nothing about it. Brand audits are periodic and mostly land-based (Break Free From Plastic, 2021), "
                      "and RA 11898 needs proof of which packaging reaches waterways. The gap is a continuous, low-cost record taken at the creek itself.")])
sh.set(p[3], [(True, "Goal: "), (False, "make creek plastic measurable evidence instead of invisible waste, with cleaner creeks and community-owned data.")])
sh.set(p[4], [(True, "Objectives"), (False, ": (1) In an 8-week pilot from December 2026, capture at least 50% of the floating debris that reaches the boom, lift at least 20 kg "
                      "and log at least 1,000 classified items. (2) By November 20, reach 85% precision and recall on unseen photos, with weekly counts within 15% "
                      "of a hand audit. (3) By March 2027, publish an open dataset and build guide and help 2 more barangays or schools build a PHP 6,800 unit.")])
sh.set(p[5], [(True, "Who will benefit from this project?")])
sh.set(p[6], [(True, "Primary: "), (False, "the [N] households of [barangay and purok] along [estero site] in Quezon City and the barangay sanitation officers. "),
              (True, "Secondary: "), (False, "the city solid-waste office and DENR, 2 more barangays or schools, and downstream fisherfolk.")])

# ---------------- slide 3 ----------------
sh = Shape(shp(S[2], 67)); p = sh.ps
sh.set(p[1], [(True, "Select. "), (False, "We scored five community problems on significance, feasibility, STEM depth, replicability and originality. Creek plastic won, "
                                          "and we fitted the design to PHP 6,800. [Edit to match your process.]")])
q2 = sh.clone_after(p[1], p[1], [(True, "What exists. "), (False, "Cameras detect floating plastic but remove nothing (Kataoka et al., 2024). Solar Interceptor barriers and AI boats "
        "are planned or piloted on large Pasig-area rivers (The Ocean Cleanup, 2026, Manila Bulletin, 2025). Trash traps remove plastic in bulk and record only weight "
        "(Philstar, 2022). Brand audits name companies but are manual (Break Free From Plastic, 2021).")])
q3 = sh.clone_after(p[1], q2, [(True, "Gap we test. "), (False, "No system we found lifts, counts and shares open data at barangay cost. Can a PHP 6,800 on-chip counter match a hand audit "
        "within 15%, and does continuous counting show rain-driven pulses of plastic (van Emmerik et al., 2022) that weekly audits miss?")])
sh.clone_after(p[1], q3, [(True, "Sources: "), (False, "Break Free From Plastic 2021, David et al. 2021, Gholami et al. 2021, Kataoka et al. 2024, Manila Bulletin 2025, "
        "Meijer et al. 2021, Philstar 2022, RA 11898, The Ocean Cleanup 2026, van Emmerik et al. 2022.")])
# ---------------- slide 4 ----------------
sh = Shape(shp(S[3], 72)); p = sh.ps
sh.set(p[1], [(True, "Summary. "), (False, "A floating boom and hyacinth deflector guide plastic to coarse bars and a fine mesh basket. A rake arm lifts it up a ramp whose foot floats on bottles, a hooded camera runs a small "
        "2D CNN on the chip (Gholami et al., 2021, David et al., 2021), and a servo gate drops plastic into Bin A and plants or unsure items into Bin B. "
        "An offline Wi-Fi page gives a weekly report and an open dataset, and an ultrasonic sensor warns of rising water.")])
q2 = sh.clone_after(p[1], p[1], [(True, "STEM. "), (False, "Physics sets buoyancy, torque and the solar budget. Mathematics defines precision, recall and count error. Computer science supplies "
        "the quantized CNN. The motor slows under load, and a shear pin, current sensing and three retries stop jams.")])
sh.clone_after(p[1], q2, [(True, "Key message. "), (False, "Proof of what plastic reaches a creek can be continuous, cheap and community-owned, and one chip delivers cleanup and evidence together.")])

for sl, idx in ((S[2], 67), (S[3], 72)):
    ps_ = shp(sl, idx).text_frame._txBody.findall(q('p'))
    for p_ in ps_[1:-1]:
        aft = p_.find(q('pPr')).find(q('spcAft'))
        if aft is not None: aft.find(q('spcPts')).set('val', '0')

# ---------------- slide 5 ----------------
sh = Shape(shp(S[4], 77)); p = sh.ps
sh.set(p[1], [(False, "A pilot unit costs about PHP 6,800, built in three stages that are each bought only after the previous test passes.")])
sh.set(p[2], [(True, "Resources:"), (False, " ESP32-S3 camera, microSD, clock and enclosure 1,850, solar panel, charger and cells 1,200, boom, post, bins and wiring 1,100, "
        "level sensor 350, motor, driver, sensing and servo 1,000, ramp, arm and filters 350, hinged float foot and chute 600, contingency 350. "
        "Stages: bench 1,850, passive trap 3,250, arm and sorter 1,350. Timeline: model by Nov 20, results Dec 7, pilot Dec to Feb, guide by March.")])
sh.set(p[3], [(True, "Stakeholders:"), (False, " barangay captain and sanitation officers (site approval, weekly emptying, one-page agreement), city solid-waste office and DENR "
        "(use the data), adviser and school head (supervision, safety), and residents (consent).")])
sh.set(p[4], [(True, "Risks & Mitigation:"), (False, " Manual labor: weekly emptying, screen clearing and lens wiping, logged in hours. Hyacinth: deflector and a plant class. "
        "Jams: shear pin, current sensing, three retries. Water level: hinged floating ramp foot with a flexible chute. Model errors: unsure items go to Bin B and a hand count checks. "
        "Safety and privacy: no one enters the water and the camera sees water only.")])

# ---------------- slide 6 ----------------
sh = Shape(shp(S[5], 82)); p = sh.ps
sh.set(p[1], [(False, "Success means plastic lifted from a real creek and a trustworthy weekly record of what it was.")])
sh.set(p[2], [(True, "Measurable Outcomes:"), (False, " (1) At least 50% capture against a baseline week and 20 kg lifted in 8 weeks. "
        "(2) At least 1,000 classified items, weekly counts within 15% of the hand audit and 85% precision and recall on unseen places. "
        "(3) At least 2 more sites by March 2027 at about PHP 6,800 each, with weekly labor hours reported.")])
sh.set(p[3], [(True, "Long-Term Vision:"), (False, " a student-built, barangay-owned network of units along connected creeks, feeding one open dataset that shows where plastic enters, "
        "which products dominate and whether EPR commitments change what the water carries. Planned upgrades are a belt conveyor and a second camera angle.")])
sh.set(p[4], [(True, "Key Takeaway:"), (False, " the Philippines already knows who makes much of its plastic. SAGIP makes the proof continuous, cheap and community-owned, "
        "and lifts some of the plastic out along the way.")])

# ---------------- delete reminders slide ----------------
lst = prs.slides._sldIdLst
last = lst[-1]
prs.part.drop_rel(last.rId)
lst.remove(last)

prs.save(sys.argv[1] if len(sys.argv) > 1 else 'SAGIP_SFT2026_Entry_PPT.pptx')
print('saved')

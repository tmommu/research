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
sh.set(p[1], [(False, "Philippine rivers rank among the largest sources of ocean plastic (Jambeck et al., 2015, Lebreton et al., 2017, Meijer et al., 2021), "
                      "and small urban esteros feed them. Cleanups weigh bulk waste and record nothing about it. Brand audits are periodic and mostly land-based "
                      "(Break Free From Plastic, 2019), and RA 11898 needs proof of which packaging reaches waterways. The gap is a continuous, low-cost record "
                      "taken at the creek itself.")])
sh.set(p[3], [(True, "Goal: "), (False, "make creek plastic measurable evidence instead of invisible waste, with cleaner creeks and community-owned data.")])
sh.set(p[4], [(True, "Objectives"), (False, ": (1) In an 8-week pilot from December 2026, lift at least [TARGET] kg of floating debris and capture at least [X]% of what "
                      "reaches the boom. (2) By November 20, reach 85% precision and recall on unseen photos, with weekly counts within 15% of a hand audit. "
                      "(3) By March 2027, publish an open dataset and build guide and help [2] more barangays or schools build a PHP 6,000 unit.")])
sh.set(p[5], [(True, "Who will benefit from this project?")])
sh.set(p[6], [(True, "Primary: "), (False, "the [N] households of [barangay and purok] along [estero] and the barangay sanitation officers. "),
              (True, "Secondary: "), (False, "the city solid-waste office and DENR, [2] more barangays or schools, and downstream fisherfolk.")])

# ---------------- slide 3 ----------------
sh = Shape(shp(S[2], 67)); p = sh.ps
sh.set(p[1], [(True, "Select. "), (False, "We scored five community problems on significance, feasibility, STEM depth, replicability and originality. Creek plastic won. "
                                          "[Edit to match your process.]")])
q2 = sh.clone_after(p[1], p[1], [(True, "What exists. "), (False, "Cameras count floating plastic but remove nothing (van Lieshout et al., 2020). Robotic boats collect it but need "
        "radio and an operator (HydroSentinel, 2026). Trash traps and interceptors remove it in bulk with little item-level data (Manila Bulletin, 2026, Schmaltz et al., 2020). "
        "Brand audits name companies but are manual (Break Free From Plastic, 2019).")])
q3 = sh.clone_after(p[1], q2, [(True, "Gap we test. "), (False, "No system we found lifts, counts and shares open data at barangay cost. Can a PHP 6,000 on-chip counter match a hand audit "
        "within 15%, and does continuous counting show rain-driven pulses of plastic (Cordova & Nurhati, 2019) that weekly audits miss?")])
sh.clone_after(p[1], q3, [(True, "Sources: "), (False, "Break Free From Plastic and GAIA 2019, Cordova & Nurhati 2019, David et al. 2021, HydroSentinel 2026, Jacob et al. 2018, "
        "Jambeck et al. 2015, Lebreton et al. 2017, Manila Bulletin 2026, Meijer et al. 2021, RA 11898, Schmaltz et al. 2020, van Lieshout et al. 2020.")])

# ---------------- slide 4 ----------------
sh = Shape(shp(S[3], 72)); p = sh.ps
sh.set(p[1], [(True, "Summary. "), (False, "A floating boom guides plastic to a bar screen, a camera-triggered arm lifts it into a bin, and an ESP32-S3 camera counts each item "
        "on the chip with an INT8 model (Jacob et al., 2018, David et al., 2021). An offline Wi-Fi page gives the barangay a weekly report and an open dataset. "
        "An ultrasonic sensor warns of rising water as a secondary function. A shear pin, current and Hall sensing and a three-retry lockout protect against jams.")])
q2 = sh.clone_after(p[1], p[1], [(True, "STEM. "), (False, "Physics sets buoyancy, torque and the solar budget. Mathematics defines precision, recall and count error. Computer science supplies "
        "the quantized model. Engineering joins them in a weatherproof floating structure.")])
sh.clone_after(p[1], q2, [(True, "Key message. "), (False, "Proof of what plastic reaches a creek can be continuous, cheap and community-owned, and one chip delivers cleanup and evidence together.")])

for sl, idx in ((S[2], 67), (S[3], 72)):
    ps_ = shp(sl, idx).text_frame._txBody.findall(q('p'))
    for p_ in ps_[1:-1]:
        aft = p_.find(q('pPr')).find(q('spcAft'))
        if aft is not None: aft.find(q('spcPts')).set('val', '0')

# ---------------- slide 5 ----------------
sh = Shape(shp(S[4], 77)); p = sh.ps
sh.set(p[1], [(False, "A pilot unit costs about PHP 6,000, built in three stages that are each bought only after the previous test passes.")])
sh.set(p[2], [(True, "Resources:"), (False, " ESP32-S3 camera board 1,300, microSD 200, box 300, solar panel 600, charger and cells 700, boom and post 800, bin and gauge 150, "
        "wiring 250, level sensor 350, motor and driver 700, sensing 150, ramp and arm 150, contingency 350. Stages: bench 1,800, passive trap 2,500, arm and sensor 1,350. "
        "Timeline: model by Nov 20, results Dec 7, pilot Dec to Feb, guide by March.")])
sh.set(p[3], [(True, "Stakeholders:"), (False, " barangay captain and sanitation officers (site approval, weekly emptying, one-page agreement), city solid-waste office and DENR "
        "(use the data), adviser and school head (supervision, safety), and residents (consent).")])
sh.set(p[4], [(True, "Risks & Mitigation:"), (False, " Hyacinth mats: deflector and a vegetation class that stops the arm. Jams: shear pin, current and Hall sensing, three retries. "
        "Oil and silt: motor mounted high, sealed bearings. Model errors: test on unseen places and keep the hand count. Arm failure: boom, bin and camera still work. "
        "Safety and privacy: no one enters the water and the camera sees water only.")])

# ---------------- slide 6 ----------------
sh = Shape(shp(S[5], 82)); p = sh.ps
sh.set(p[1], [(False, "Success means plastic lifted from a real creek and a trustworthy weekly record of what it was.")])
sh.set(p[2], [(True, "Measurable Outcomes:"), (False, " (1) At least [TARGET] kg lifted in 8 weeks, with a capture rate of at least [X]% against a baseline week. "
        "(2) Weekly counts within 15% of the hand audit, and 85% precision and recall on unseen places. "
        "(3) At least [2] more sites by March 2027 at about PHP 6,000 each, sharing one open data format.")])
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

# SFT 2026 — Winning-Oriented Proposal (rewrite of the team's heat entry)

Built from the team's "SFT 2026 - Proposal (Word)" draft. Facts, citations and costs come from that draft and **must be re-verified against the sources before submission**. Items in `[BRACKETS]` are blanks only the team can fill. Target length is under the 3,000-word / 7-page limit. Export as PDF under 40 MB, deadline **Nov 2, 2026, 11:59 PM**.

---

**Entrant's school:** Quezon City Science High School  **Adviser:** Skjoukje U. Jemoya
**Team:** Raya Kalayaan R. Amparo, Aaron Jed E. Campo, Ayeza Leigh F. Delos Santos, Sophia Laureen A. Tado (all Grade 10)
**Theme:** Environmental Sustainability through Technology

## Entry title

**LAMIG: A Low-Cost, Predictive Cooling System that Gives Public-School Classrooms a 30-Minute Heat Warning and Cools Them Before the Heat Peaks**

*(LAMIG = "cool" in Filipino. Rename if the team prefers; the entry form needs a real project name, not "[Project name]".)*

## Project description (exactly three sentences, for official write-ups)

LAMIG is a low-cost, solar-ready classroom device that predicts the room's heat index 30 minutes ahead and uses that lead time to start cooling before students feel the peak. It combines a reflective shade net, a humidity-aware exhaust fan, targeted personal fans and an optional dry-season wet wick, with a screen that gives teachers one clear action at a time. Built from local and upcycled parts, tested against a control classroom, it needs no internet, collects no personal data and targets a 2 to 5 °C lower felt temperature.

## 1. What problem are you trying to solve?

El Niño does not create classroom heat; it makes it worse. PAGASA says El Niño is still strengthening and that record-high temperatures are possible into the 2027 warm and dry season (GMA News, 2026). Most Philippine public classrooms have little beyond open windows and electric fans: in a March 2023 survey of 11,706 public-school teachers, about 67% reported intolerable heat, 97% had electric fans and 0.9% had air conditioners (Philstar, 2023).

Heat costs learning. A 2025 review of seven studies covering about 14.5 million students found accumulated heat lowers learning, with low-income students bearing roughly three times the effect (Vasilakopoulou & Santamouris, 2025). One included study found each extra school day above 26.7 °C over the prior three years lowered exam scores (Park et al., 2021). Most of this work uses outdoor temperature; we found none measuring Philippine classrooms.

DepEd already treats heat as a school risk. In April 2024, hundreds of schools suspended in-person classes (AFP, 2024), and on October 6, 2026, DepEd NCR formed a Technical Working Group on El Niño impact (Regional Memorandum No. 806, s. 2026). **What is missing is measurement of heat inside the classroom, and a warning early enough to act.** The problem returns every March to May, not only in El Niño years.

## 2. What do you want to achieve?

**Goal:** reduce the effects of El Niño heat in public-school classrooms, and every dry season after, with low-cost, water-wise, solar-ready methods other schools can copy. (We act on classroom conditions, not on El Niño itself.)

**Objectives**

1. **Reduce heat.** In an 8-week pilot with ON and OFF days and a control classroom on the same floor and side, lower the 1–3 p.m. felt temperature by at least 2 °C (stretch 5 °C on dry, sunny days), cut minutes above a 38 °C heat index by 30%, and raise student comfort by at least 1 point.
2. **Predict early.** By Nov 20, 2026, predict the heat index 30 minutes ahead within a mean absolute error of 1.5 °C on days the model has not seen, beating a straight-line baseline.
3. **Replicate cheaply.** By March 2027, publish a free English/Filipino build guide and help at least 2 more classrooms build a Core unit for no more than PHP 4,000 in local parts, with any wick within 5 L of water a day.

## 3. Who will benefit?

- **Primary:** the [NUMBER] students and [NUMBER] teachers of our 2nd-floor Grade [GRADE] pilot classroom at Quezon City Science High School, who spend about [HOURS] hours a day in a sun-heated room.
- **Secondary:** at least 2 more classrooms by March 2027; school heads, the Schools Division Office and the DepEd NCR El Niño working group, who get measured, low-cost, replicable data.
- **Wider reach:** the 97% of public classrooms the survey found relying on fans alone.

## 4. How did you come up with the proposal?

We scored five community problems on significance, feasibility, STEM depth, replicability and originality (heat, food waste, flooding, street accessibility, and one more of the team's choice). Heat won: everyone feels it, we can measure it at our school, and DepEd's October 2026 memorandum makes it a priority.

We then reviewed evidence from 2021 onward layer by layer. External shading cut discomfort hours by 44% in a simulated Nigerian classroom (Alegbe et al., 2023), though window films cost daylight in Taiwan (Huang et al., 2024). Singapore's education ministry favoured faster fans, cool paint and shading over air conditioning (MOE Singapore, 2025). A scale-model evaporative cooler in Malaysia cut air temperature by up to 3.9 °C but raised humidity to 91% (Moh et al., 2023), so our wick runs only in dry air.

**The gap we found:** no measured study from 2021 onward isolates exhaust or night ventilation in tropical classrooms, tests all four layers together, takes place in a Philippine classroom, or forecasts classroom temperature on a chip (TinyML forecasting exists, but not for classrooms: Alati et al., 2022). Our tests are built to probe the least-supported layers.

## 5. How will your tech solution work?

> **STEM map for judges:** *Physics* (heat transfer, radiant vs. convective heat, airflow) · *Math/Statistics* (heat index, mean absolute error, ON/OFF comparison) · *Computer Science* (TinyML, 8-bit quantization) · *Engineering* (sensing, control, safe low-voltage design) · *Technology* (ESP32 microcontroller, OLED, MOSFET drivers).

LAMIG **senses, predicts, acts and informs.**

**Sense (Physics, Engineering).** Four sensors log every minute: two SHT31 temperature-humidity sensors (about ±0.3 °C) at desk level and at the jalousie intake; a DS18B20 near the ceiling for the hot layer; and a **black globe** (a painted ball with a DS18B20 probe) that measures radiant heat from roofs and walls. Students calibrate every sensor in an ice bath and compare logs with nearby PAGASA readings.

**Predict (Computer Science, Math).** A neural network of a few hundred numbers takes the current heat index, its recent change, the ceiling-minus-desk gap, the intake reading, the radiant-heat difference and the time of day, and predicts the heat index 30 minutes ahead. It is **quantized to 8-bit** and runs on the chip with TensorFlow Lite for Microcontrollers.

> **Why this beats a thermostat or timer (Design Innovation).** A threshold timer reacts only after the room is already hot. A classroom has *thermal inertia*: walls and roof store heat, so by the time the air reads hot, cooling is too late and too weak. LAMIG's 30-minute lead lets it **pre-cool** (open the intake, run the exhaust, aim fans) *before* the sun-facing wall peaks, and the ceiling-minus-desk gap and black-globe reading tell it *why* the room is heating, not only how hot it is. The hardware is off-the-shelf; the novelty is fusing multi-sensor readings with a prediction small enough to run on a PHP 4,000 unit. If the model cannot beat a straight-line guess on unseen days, the rule-based method stays.

**Act (Engineering).** Four layers work together:
- **Block:** a reflective exterior shade net on sun-facing windows cuts the sunlight that heats the room.
- **Flush:** a 140 mm exhaust fan high on the sun side pulls out the hottest air while the shaded-side jalousies stay open. It runs only when incoming air is cooler and not more humid.
- **Feel:** the screen tells teachers when to run existing fans and how to aim them; 6–8 recycled PC fans on chair arms add about 0.5–1 m/s airflow on rows the wall fans miss.
- **Cool:** an optional dry-season wet wick, within a 5 L daily limit. In hot, humid air the box only warns.

**Inform (Design).** A 2.42-inch OLED on the teacher's desk shows live temperature and humidity, current and forecast heat index, a level (OK / Watch / Act now) and one tip from a one-page **heat playbook**: at Watch, open jalousies and run fans; at Act now, call a water break and move the class to shade. A flash plus one chime marks each rise, so a hearing-impaired teacher still gets the alert; a button silences it for 30 minutes. A QR code opens an offline page, and a free browser tool ranks rooms by heat exposure and prints a report for school heads. A **heat timetable** of the room's hottest hours lets PE and tests move to cooler periods.

**Power resilience (Feasibility).** Brownouts are likely on the hottest days, so the control layer is separated from the fans:
- The **ESP32, sensors and OLED draw well under 1 W** and run from a USB power bank, which should hold the controller for more than a day (the team must measure this on the bench and report the real figure).
- On power loss the fans stop safely, the box keeps logging and warning, and the **playbook still works with no electricity** (open jalousies, move to shade, water break).
- The same design takes a small solar panel and battery, so it also works where the grid is unreliable.

**Safety.** A reused, certified 12 V adapter (about 29 W) in the pilot. Fans switch through logic-level MOSFETs with flyback diodes behind a 5 A fuse, every fan has a finger grill, cables stay off the aisles, and any wick drips into a covered, draining tray. Staff do all installation at low voltage.

**How the tiny AI works, in plain words.** Picture a veteran teacher who knows that when the sun hits the windows at 10 a.m., the room will be unbearable by 10:30. The model is that instinct, saved as a file of numbers. Quantization rounds the numbers to whole 8-bit values, like a gradebook recording 87 rather than 87.3416, so the file fits in the chip's flash memory. No internet is needed and no data leaves the classroom.

*Figure 1: sense → predict → act → inform flow.* *Figure 2: schematic of the installed prototype, labelled.* (Include both; add a photo of the real build if possible.)

## 6. How will you implement this?

**Budget (estimated local prices, to be confirmed).**
- Pilot unit about PHP 5,400: ESP32, sensors, clock module, OLED, one 140 mm PWM fan, drivers and power parts, reflective net and frame (~900), 8 PC fans (1,200, or ~500 recycled).
- Control-room logging unit PHP 1,200; contingency about PHP 650. **Pilot total about PHP 7,200** (about 6,400 with recycled fans).
- **Core unit for other schools: about PHP 4,000.** Add-ons only when a measured trigger fires (extra wall fans, wick, second exhaust fan, solar, reflective foil).

**Tools:** Arduino IDE, Python with TensorFlow Lite for Microcontrollers, soldering iron, multimeter, reference thermometer, anemometer.

**Timeline.**
| Dates | Milestone |
|---|---|
| Oct 12 – Nov 2 | Build, calibrate, install; baseline week and air-speed map of existing fans |
| From Nov 3 | 8-week ON/OFF pilot; two weeks testing one layer at a time |
| Nov 16 – Dec 5 | Refine with Samsung coaches (if selected) |
| Dec 7 | Early results from about 5 weeks of data; full 8 weeks finish late December |
| By Mar 2027 | Build guide published; 2 more classrooms equipped |

**Stakeholders:** school head (installation), adviser and teachers (build and use), students and parents (anonymous survey), maintenance staff (safety), Schools Division Office and DepEd NCR working group (use of results).

**Maintenance without technical burden (Feasibility, Sustainability).**
- A **one-page monthly checklist** (wipe sensors, check fan grills and fuse, verify the display against a thermometer) that a named staff member or the science club can do in 15 minutes.
- Students keep the calibration and data roles; spare fans and sensors stay on site.
- Parts are common (PC fans, ESP32, standard sensors), so replacement fits a PTA or school budget, and **upcycled computer fans** cut cost and e-waste.
- **Rule-based fallback:** if the AI or a sensor fails, the box falls back to simple heat-index thresholds, so nothing breaks the class's routine.

**Risks and mitigation.**
- *Weather varies:* ON/OFF days, a control classroom, one-layer-at-a-time tests.
- *Target missed:* report the measured result and each layer's contribution honestly.
- *Less daylight from shading:* measure light levels and choose a light tint (Huang et al., 2024).
- *Hot, humid air and water:* fan stays off if incoming air is hotter; wick only in dry air within 5 L.
- *Sensor drift, cloudy days, AI error:* monthly calibration and the rule-based fallback.
- *Mounting, noise, privacy:* guarded panel, staff-installed low-voltage wiring, capped fan voltage, record only temperature, humidity and radiant heat.

## 7. Impact and long-term vision

Success means teachers know when heat is coming and have a low-water way to reduce it, judged against our own logged data. The system mitigates the effects of El Niño heat on a room; it does not change El Niño.

**Measurable outcomes**
1. **Cooler room:** at least 2 °C lower felt temperature on ON than OFF days (stretch 5 °C), at least 30% fewer minutes above a 38 °C heat index, and comfort up by at least 1 point, with each layer's contribution reported.
2. **Early warnings:** error of 1.5 °C or less at 30 minutes, below a straight-line baseline, on unseen days.
3. **Replication:** free English/Filipino build guide; at least 2 more classrooms by March 2027 at no more than PHP 4,000 each; any wick within 5 L a day.

**Sustainability beyond El Niño.** The device keeps working every annual **March–May warm-dry season**, so the equipment pays back year after year; open-source electronics and upcycled fans keep replacement cheap.

**Long-term vision.** Two identical units in side-by-side rooms, one ON and one OFF, swapping halfway to cancel out weather; then the 3rd and 4th floors, closest to the roof, and a school-wide dashboard.

**Key takeaway.** Classroom heat can be seen coming and partly offset. LAMIG gives schools a 30-minute warning and four low-cost ways to reduce the heat students feel.

## References

AFP (2024). Hundreds of Philippine schools suspend classes over heat danger. Phys.org.
Alati et al. (2022). Temperature forecasting using TinyML. IEEE CCNC.
Alegbe et al. (2023). Solar shading in classrooms. Dimensi 50(2).
Alliance of Concerned Teachers survey (2023), via Philstar.
DepEd NCR (2026). Regional Memorandum No. 806, s. 2026.
Faraj et al. (2023). Ventilation in Malaysian classrooms. IJSDP 18(7).
GMA News (2026). PAGASA statements on El Niño.
Huang et al. (2024). Window films. Energies 17(6).
MOE Singapore (2025). Parliamentary reply on cooling in schools.
Moh et al. (2023). Evaporative cooling for tropical climates. Front. Mech. Eng. 9.
Park et al. (2021). Nature Human Behaviour 5, 19-27.
Vasilakopoulou & Santamouris (2025). PLOS Climate.

---

## What changed from the team's draft, and why

| Rubric criterion (weight) | Change |
|---|---|
| Design Innovation (20%) | Added the explicit "why not a thermostat" argument: thermal inertia and **pre-cooling** with the 30-minute lead; fusion novelty stated plainly. |
| Relevance to the Community (20%) | Anchored on the 97%-fans-only finding and DepEd's own El Niño working group; added wider-reach line. |
| Feasibility (20%) | Added brownout design (controller on power bank, playbook works with no power), a 15-minute maintenance checklist and a rule-based fallback. |
| STEM Integration (15%) | Added an explicit STEM map and labelled each technical section with its discipline. |
| Sustainability (15%) | Stated reuse every March–May, upcycled fans, open-source parts, PTA-affordable replacement. |
| Clarity (10%) | Named the project, tightened the three-sentence description, filled placeholders as `[BRACKETS]`, one idea per section. |

## Before you submit — checklist

- [ ] Fill every `[BRACKET]`, and put the project name on the title and the entry form.
- [ ] Re-verify every citation and number against its source; correct any that don't match.
- [ ] Measure the real power-bank runtime and put the number in the brownout paragraph.
- [ ] Add one photo of the actual prototype and the baseline-week data table, if available; judges favour working, measured builds.
- [ ] Do not claim the 2 °C result until the pilot data supports it; state targets as targets.
- [ ] Check against the official entry templates in the Drive folder (the connector could not list their contents).
- [ ] Export to PDF under 40 MB; submit before Nov 2, 11:59 PM.

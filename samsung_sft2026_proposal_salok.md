# SFT 2026 — Proposal: SALOK (PHP 6,000 build)

**Theme:** Environmental Sustainability through Technology
**Deadline:** Nov 2, 2026, 11:59 PM. Format: Word (≤3,000 words / 7 pages) or PPT (≤6 slides), exported as a PDF under 40 MB.

Facts marked **[VERIFY]** are from memory of public sources and must be checked against the primary source before submission. Items in `[BRACKETS]` are blanks only the team can fill. Prices are estimates to confirm locally. Nothing here is a measured result; targets are labelled as targets.

---

**Entrant's school:** Quezon City Science High School  **Adviser:** [NAME]
**Team (max 4):** [NAMES, Grade 10]

## Entry title

**SALOK: A PHP 6,000 Solar-Powered Estero Guardian that Traps Plastic, Warns Barangays Before Clogged Waterways Flood, and Builds the First Open, Brand-Level Plastic Data Commons Needed to Hold Producers Accountable**

*(Salok = "to scoop" in Filipino. Rename if the team prefers.)*

## Project description (three sentences, for official write-ups)

SALOK is a low-cost, solar-powered estero guardian: a floating boom guides surface plastic to the bank where a small camera-triggered sweeper arm lifts it into a bin, an ESP32 camera with an on-device AI model counts and classifies each item by type and, where legible, by brand, and a water-level sensor warns the barangay when debris and rising water threaten to block the channel. Barangay officials get a weekly report of what was removed and who made it, plus a flood-risk alert, without internet and without recording faces. Built for PHP 6,000 from local and upcycled parts, every barangay's anonymized results join an open dataset, so one unit protects one creek and many units build the evidence to hold producers accountable.

## 1. What problem are you trying to solve?

Plastic reaches the sea through creeks and esteros. Published river-emission studies rank Philippine rivers among the largest sources of ocean plastic **[VERIFY: Meijer et al., 2021, Science Advances]**, and Metro Manila's esteros and the Pasig and Tullahan river systems carry much of it. Single-use sachets, bags and cups are dominant items in cleanups **[VERIFY: local cleanup audits]**.

Three gaps keep the problem going:

1. **Removal is manual and invisible.** Cleanups happen on schedule and the trash is weighed in bulk. Nobody records what was in it, so the same items return.
2. **There is no brand-level data.** The Extended Producer Responsibility Act of 2022 (RA 11898) makes large companies responsible for recovering plastic packaging **[VERIFY: scope and thresholds]**, but enforcement needs evidence of *which* packaging ends up in waterways. Barangays have no cheap way to produce it.
3. **Clogged waterways flood neighbourhoods.** Plastic and other debris choke drainage and esteros, worsening flooding in low-lying communities **[VERIFY: MMDA/DPWH reports and flood studies]**, and standing, trash-filled water also breeds mosquitoes. Barangays learn a channel is blocked only when it floods.

**The problem is therefore three-part: catching the plastic, proving what it is, and seeing the blockage before it floods people's homes.** One device addresses pollution, accountability and safety at once.

**Scale of the opportunity.** The Philippines has tens of thousands of barangays **[VERIFY: PSA count, about 42,000]**, and esteros run through a large share of urban ones. Each is a data point nobody is collecting. A design that costs PHP 6,000 and shares its data openly can add up to the first nationwide picture of what plastic is in our waterways.

## 2. What do you want to achieve?

**Goal:** remove floating plastic from one estero in our community, warn of blockages, and generate the first student-collected, brand-level waste data that a barangay can hand to the LGU, using a design any barangay can copy for about PHP 6,000.

**Objectives (SMART)**

1. **Clean.** In an [8]-week pilot at [ESTERO SITE], keep the boom and sweeper arm operating through [N] rain events and lift at least [TARGET] kg of floating debris out of the water, logged by weekly weigh-in, with a measured **capture rate** of at least [X]% of the floating debris reaching the boom (checked with downstream hand-net sampling), the arm running on solar power alone, and fewer than [N] jam stops a week.
2. **Classify.** By Nov 20, 2026, train an on-device model to detect [5] classes (PET bottle, sachet/foil pouch, plastic bag, foam container, cup/other) with at least [0.85] precision and recall on photos from locations *not used in training*.
3. **Count accurately.** In the pilot, the device's item counts should be within ±15% of a weekly hand count of the same pocket contents.
4. **Report.** Produce a one-page weekly barangay report (items, types, estimated weight, top legible brands) with no internet.
5. **Warn.** An ultrasonic water-level sensor logs level against rainfall and pocket fullness and triggers a "channel nearly blocked" alert; success is the alert firing at least [N] minutes before the nearest known flood point is reached in at least [N] observed events (we report whatever we measure).
6. **Open data.** Publish anonymized weekly counts (type, brand tallies, estimated kg, level readings, no images of people) as an open CSV with a data dictionary.
7. **Replicate.** By March 2027, publish a free English/Filipino build guide and help [1–2] other barangays or schools build one for no more than PHP 6,000, each contributing to the same open dataset.

## 3. Who will benefit?

- **Primary:** residents of [BARANGAY/PUROK] along [ESTERO] and the barangay's environmental/sanitation officers, who get a cleaner waterway, flood warnings and data they have never had.
- **Secondary:** the LGU/DENR offices handling solid waste, who can use brand-level evidence; neighbouring barangays who can copy the design; students, who become the community's citizen scientists.
- **Wider:** downstream communities and fisherfolk affected by plastic reaching Manila Bay.

## 4. How did you come up with your proposal?

We scored five community problems on significance, feasibility, STEM depth, replicability and originality. Plastic in esteros won because we can reach one, measure it weekly, and RA 11898 has just made the data useful.

We reviewed existing approaches and found two camps. Passive trash booms catch plastic but record nothing beyond bulk weight. Research systems that use cameras and AI to detect river plastic exist **[VERIFY: published river-plastic computer-vision monitoring]**, but typically need powerful hardware, a stable connection or an expert to run. **We found no low-cost design that combines a physical collection boom, a power-frugal on-device classifier and a flood-warning sensor that a barangay can operate.** SALOK sits in that gap.

## 5. How will your tech solution work?

> **STEM map:** *Physics* (buoyancy, flow, solar power budget, ultrasonic ranging) · *Math/Statistics* (precision, recall, count error, sampling) · *Computer Science* (object detection, INT8 quantization) · *Engineering* (floating structure, mounting, weatherproofing) · *Environmental Science* (waterway pollution, EPR policy).

SALOK **traps, sees, counts, warns and reports.**

**Trap (Physics, Engineering).** A V-shaped boom of reused PET bottles and bamboo floats, joined with rope and net, guides surface debris toward the bank at the apex, where it collects against a bar screen at the foot of a sloped mesh ramp anchored to the bank or a bridge post. The estero's own current does the herding, so the boom needs no energy. A float-and-time test sets the boom angle for the estero's flow.

**Lift (Engineering, Computer Science).** A small geared DC motor, driven from the battery pack through a motor driver, turns a rake arm that sweeps debris up the ramp into a covered bin above the waterline. The arm does not run constantly: when the camera sees debris in the pocket, the ESP32 runs the arm for a few seconds, then idles. The ESP32 reads the motor's current, so a spike (a jam) makes the arm reverse and retry, and a full bin stops it and alerts the barangay. This is what lets a small solar panel power active cleaning. Adults empty the bin weekly with gloves; students never enter the water, and the arm is guarded and locked out during emptying.

**See (Computer Science).** An ESP32-S3 camera board on a post above the pocket looks *down at the water surface only*, so no faces or houses are in frame. A compact object-detection model, **quantized to INT8** and run with TensorFlow Lite for Microcontrollers, classifies each item entering the pocket. Training photos come from our own collections of real trash on the estero bank, labelled by students and checked by the adviser. To save power, the camera captures on a timer or when motion is detected.

**Count and weigh (Math).** Each detection increments a class counter stored on the microSD card. Weekly, students hand-count and weigh the pocket's contents; a per-class average weight turns counts into estimated kilograms, and the hand count becomes our accuracy test.

**Warn (Physics, Engineering).** A waterproof ultrasonic sensor on the same post measures the distance to the water surface. The ESP32 logs level, compares it to a marked staff gauge, and raises an alert (status LED and report flag) when the level rises fast or the pocket is nearly full.

**Report (Design).** A small status display or LED and an offline Wi-Fi page the ESP32 hosts for a phone (no cellular needed) show running counts and alerts. A script produces the one-page weekly barangay report and a CSV for the LGU. Legible brand names are tallied by a student volunteer from stored photos; the AI's job is to flag and crop likely labels, because automated brand reading is not yet reliable.

**Power (Feasibility).** The ESP32 camera averages well under a watt when duty-cycled. A small solar panel, a charge-controller module and two 18650 cells (through a boost converter) cover it, sized from bench measurements the team will report. On cloudy days the device lengthens its capture interval instead of shutting down.

**Safety.** Low-voltage wiring in a sealed enclosure with desiccant; fuse and switch; the arm guarded, with a stop switch and a lockout during emptying; the boom away from boat routes; barangay and school sign-off on the site; adult-only emptying; no cameras on people.

**What it will and will not clean.** SALOK removes **light floating and near-surface debris** that reaches the boom and ramp: bottles, sachets, bags, foam and cups, in small batches. It does not lift heavy or large items or tangled debris (a bar screen keeps those out and a person removes them), and it does not remove sunken waste, sediment, oil or dissolved pollutants, and it cannot clean the whole estero, only the stretch upstream of the boom. We report the measured capture rate rather than claiming the estero is "clean".

**Phase 2 (not in the PHP 6,000 pilot).** A full motorized conveyor belt with a larger panel and battery for higher debris volumes. We keep it as a funded next step so that the pilot is honest about what the budget can build. If the arm fails, the boom and pocket still trap debris passively and the camera still counts, so the data pilot is not at risk.

**Honest limits.** Detection will degrade in rain, glare and murky water; we report that rather than hide it.

*Figure 1: boom and pocket layout. Figure 2: system block diagram (boom → pocket → camera → model → counts → report, level sensor → alert). Figure 3: sample detections.*

**How the tiny AI works, in plain words.** A model that has seen thousands of photos of bottles, sachets and bags learns what each looks like. Quantization stores its numbers as small whole numbers so it fits on a PHP 1,300 chip that runs on a fraction of a watt from the sun, with no internet and nothing leaving the estero.

## 6. How will you implement this?

**Budget: PHP 6,000 (estimates; confirm local prices).**

| Item | PHP |
|---|---|
| ESP32-S3 camera board | 1,300 |
| microSD card | 200 |
| Waterproof sealed enclosure, glands, desiccant | 300 |
| Waterproof ultrasonic level sensor | 350 |
| Small solar panel (about 6–10 W) | 600 |
| Charge controller, 2× 18650 cells, holder, boost converter | 700 |
| Rope, net, zip ties for the boom (bottles and bamboo reused, free) | 450 |
| Anchor, post, clamps, concrete | 350 |
| Collection bin (reused) and painted staff gauge | 150 |
| Wiring, fuse, switch, connectors | 250 |
| Small geared DC motor (6–7.4 V) | 500 |
| Motor driver | 200 |
| Current sensing for jam detection | 150 |
| Ramp, rake arm, shaft and bar screen (recycled plastic, bolts) | 150 |
| **Subtotal** | **5,650** |
| Contingency (about 6%) | 350 |
| **Total** | **6,000** |

**Tools:** Arduino IDE or PlatformIO, Python with TensorFlow Lite for Microcontrollers, a borrowed soldering iron and multimeter, and phones the team already owns for photos.

**Timeline**
| Dates | Milestone |
|---|---|
| Oct 28 – Nov 2 | Site visit and barangay approval; photograph and label a starter dataset; draft and submit the proposal |
| Nov 3 – Nov 20 | Train and quantize the first model; build and float-test the boom; bench-test power |
| Nov 16 – Dec 5 | Refine with Samsung coaches (if shortlisted) |
| Dec 7 | Present early results: model metrics and first pocket weights |
| Dec – Feb | Full pilot, weekly hand-count validation, barangay reports |
| By Mar 2027 | Build guide published; 1–2 more sites; Phase 2 conveyor if funded |

**Stakeholders:** barangay captain and sanitation/environment officers (site, emptying, using reports), the LGU solid-waste office (data), our adviser and school head (supervision), students (build, label, count, report), residents (consent and awareness).

**Maintenance and handover.** A one-page weekly checklist: empty the bin, clear the bar screen, check the arm and ramp for wear, wipe the lens, check the mooring, read the battery, upload the CSV. The barangay names a focal person; students own the data and model updates. Parts are common and repairable locally.

**Risks and mitigation**
- *Flood or storm damages the boom:* secure mooring, a quick-release line, and a plan to retrieve electronics before a typhoon.
- *Arm jams or the battery drains:* bar screen ahead of the ramp, motor-current jam detection with auto-reverse, short bursts only when debris is seen, and a bench test of how many lifts a day the panel supports.
- *Model fails in new light or water:* collect across times of day and weather, report held-out-location scores, keep a manual fallback count.
- *Biofouling or theft:* lens-cleaning schedule, discreet mounting, barangay tanod awareness.
- *Power shortfall:* longer capture interval on cloudy days; spare 18650 cells.
- *Safety:* no student enters the water; adult emptying with gloves; barangay and school approval first.
- *Over-claiming:* targets stated as targets; we report the measured result and what failed.

## 7. Impact and long-term vision

**Success means** floating plastic physically removed from a real estero, a weekly, trustworthy record of what it was, and a flood warning for the people who live beside it, all for PHP 6,000.

**Measurable outcomes**
1. [TARGET] kg of floating debris lifted out of the water over the pilot, with weekly weigh-ins, a measured capture rate and a solar-powered arm.
2. Model precision and recall ≥ [0.85] on held-out locations; weekly count error within ±15% of hand counts.
3. A weekly barangay report series, a first brand-level audit of the estero, and a logged record of level alerts.
4. A build guide and at least [1–2] additional sites by March 2027, each at no more than PHP 6,000.

**Sustainability.** The barangay runs it with local parts, solar power and a one-page checklist; no subscription, server or internet is needed; the dataset and model are open so other barangays can retrain on their own waste.

**Long-term vision.** A student-built, barangay-owned network of low-cost SALOK units along connected esteros, feeding an open dataset that shows where plastic enters the waterway, which products dominate, which channels clog first, and whether EPR commitments are changing what the water carries. Each added barangay makes every other unit's data more valuable, so impact grows faster than cost.

**Key takeaway.** Catching plastic is not enough; proving what it is makes producers accountable, and a flood warning protects the people nearby. SALOK does all three for the price of one cheap trap.

## References **[VERIFY each; add the exact citations]**

Meijer et al. (2021). More than 1,000 rivers account for 80% of global riverine plastic emissions into the ocean. *Science Advances*.
Republic Act 11898, Extended Producer Responsibility Act of 2022.
[Local cleanup/brand audit source].
[A published river-plastic computer-vision monitoring study].
[A TinyML or object-detection source on low-power microcontrollers].

---

## How this maps to the rubric

| Criterion (weight) | How SALOK earns it |
|---|---|
| Design Innovation (20%) | Boom + on-device AI + brand-level audit + flood early warning in one PHP 6,000 unit; links physical cleanup to policy evidence and disaster prevention; open data commons. |
| Relevance to the Community (20%) | A real estero, a named barangay partner, a current law, and a problem the community sees daily. |
| Feasibility (20%) | Common parts, solar, one-page upkeep, a fully itemized PHP 6,000 budget, a safety plan, and a realistic pilot. |
| STEM Integration (15%) | Explicit STEM map; physics, statistics, computer science, engineering and environmental science all used. |
| Sustainability (15%) | Solar, upcycled floats, no server, open model, replicable by any barangay for PHP 6,000. |
| Clarity (10%) | One problem, one device, one measured outcome, plus the report the community can act on. |

## Pre-submission checklist

- [ ] Choose the real estero and get written barangay/LGU approval; fill in `[SITE]`, `[BARANGAY]`.
- [ ] Spend this week photographing and labelling real trash to show a starter dataset and sample detections.
- [ ] Verify every **[VERIFY]** fact and add exact citations.
- [ ] Confirm the ESP32-S3 board can run your model (RAM/PSRAM) and bench-measure power draw; report the real number.
- [ ] Replace budget estimates with real local prices; keep the total within PHP 6,000.
- [ ] Add photos or a labelled drawing of the boom and a sample detection image.
- [ ] Check against the official entry templates (the Drive connector could not list them) and export to PDF under 40 MB.

# SFT 2026 — Proposal: SALOK (PHP 6,000 build)

**Theme:** Environmental Sustainability through Technology
**Deadline:** Nov 2, 2026, 11:59 PM. Format: Word (≤3,000 words / 7 pages) or PPT (≤6 slides), exported as a PDF under 40 MB.

**How to read this draft.** `[BRACKETS]` are blanks only the team can fill. **[VERIFY]** marks facts from memory of public sources that must be checked against the primary source. Prices are estimates to confirm locally. Targets are targets, not results. The "Power budget" arithmetic uses stated assumptions that bench tests must replace.

---

**Entrant's school:** Quezon City Science High School  **Adviser:** [NAME]
**Team (max 4):** [NAMES, Grade 10]

## Entry title

**SALOK: A PHP 6,000 Solar-Powered Estero Guardian that Lifts Plastic Out of the Water and Counts Every Item as Evidence for Producer Accountability**

*(Salok = "to scoop" in Filipino. Rename if the team prefers.)*

**One-sentence pitch.** SALOK removes floating plastic from a creek and counts every item with a camera, giving the barangay the evidence the law needs to hold packaging makers accountable, and, as a bonus, warns when the channel is about to block.

## Project description (three sentences, for official write-ups)

SALOK is a low-cost, solar-powered unit in which a floating boom guides surface plastic to the bank, a small camera-triggered sweeper arm lifts it into a bin, and an ESP32 camera with an on-device AI model counts every item by plastic type and, where legible, by brand. Barangay officials get a weekly report of what was removed and who made it, with no internet and no images of people, and a secondary water-level alert warns when debris and rising water threaten to block the channel. Built for PHP 6,000 from local and upcycled parts, its anonymized results join an open dataset so that many barangays can build the evidence to hold producers accountable.

## 1. What problem are you trying to solve?

Plastic reaches the sea through creeks and esteros. Published river-emission studies rank Philippine rivers among the largest sources of ocean plastic **[VERIFY: Meijer et al., 2021, Science Advances]**, and Metro Manila's waterways, including the Pasig and Tullahan systems, carry much of it. Single-use sachets, bags and cups are dominant items in cleanups **[VERIFY: local cleanup audits]**.

Two gaps keep the problem going:

1. **Removal is manual and invisible.** Cleanups happen on schedule and the trash is weighed in bulk. Nobody records what was in it, so the same items return.
2. **There is no brand-level data.** The Extended Producer Responsibility Act of 2022 (RA 11898) makes large companies responsible for recovering plastic packaging **[VERIFY: scope and thresholds]**, but enforcement needs evidence of *which* packaging ends up in waterways. Barangays have no cheap way to produce it.

A secondary problem sits on the same creek: debris-choked channels flood neighbourhoods **[VERIFY: MMDA/DPWH reports]**, and barangays learn a channel is blocked only when it floods.

**The Philippines has tens of thousands of barangays [VERIFY: PSA count, about 42,000], and esteros run through many urban ones. Each is a data point nobody is collecting.** A design that costs PHP 6,000 and shares its data openly can add up to the first nationwide, community-collected picture of what plastic is in our waterways.

## 2. What do you want to achieve?

**Goal:** lift floating plastic out of one estero in our community and generate the first student-collected, brand-level waste data that a barangay can hand to the LGU, with a design any barangay can copy for about PHP 6,000.

**Core objectives (SMART)**

1. **Clean.** In an [8]-week pilot at [ESTERO SITE], lift at least [TARGET] kg of floating debris out of the water, with a measured **capture rate** of at least [X]% of the floating debris reaching the boom, compared against a **baseline week** before installation.
2. **Classify.** By Nov 20, 2026, train an on-device model for [5] classes (PET bottle, sachet/foil pouch, plastic bag, foam container, cup/other) with at least [0.85] precision and recall on photos from locations *not used in training*.
3. **Count accurately.** Weekly device counts within ±15% of a hand count of the bin's contents.
4. **Report and open data.** A one-page weekly barangay report (items, types, estimated weight, top legible brands) and an anonymized open CSV with a data dictionary.
5. **Replicate.** By March 2027, publish a free English/Filipino build guide and help [1–2] other barangays or schools build one for no more than PHP 6,000.

**Secondary objective**

6. **Warn.** An ultrasonic level sensor logs level against rainfall and bin fullness and raises a "channel nearly blocked" alert; we report how many minutes of warning it gave in the [N] events we observe, whatever the result.

## 3. Who will benefit?

- **Primary:** residents of [BARANGAY/PUROK] along [ESTERO] and its environmental/sanitation officers, who get a cleaner waterway and data they have never had.
- **Secondary:** the LGU/DENR solid-waste offices, who can use brand-level evidence; neighbouring barangays who can copy the design; students, who become the community's citizen scientists.
- **Wider:** downstream communities and fisherfolk affected by plastic reaching Manila Bay.

## 4. How did you come up with your proposal?

We scored five community problems on significance, feasibility, STEM depth, replicability and originality. Plastic in esteros won because we can reach one, measure it weekly, and RA 11898 has just made the data useful.

We reviewed existing approaches and found two camps. Passive trash booms catch plastic but record nothing beyond bulk weight. Research systems that use cameras and AI to detect river plastic exist **[VERIFY: published river-plastic computer-vision monitoring]**, but they typically need powerful hardware, a connection or an expert. **We found no low-cost design that physically lifts plastic out, counts it by type and brand on a chip, and a barangay can run.** SALOK sits in that gap.

**What is new.** The parts are common; the combination is not. The camera is both the *counter* and the *trigger* for the arm, so the AI saves energy and produces evidence with the same hardware, and the data is built to be open and comparable across barangays.

## 5. How will your tech solution work?

> **STEM map:** *Physics* (buoyancy, flow, solar energy budget, ultrasonic ranging) · *Math/Statistics* (precision, recall, count error, sampling) · *Computer Science* (object detection, INT8 quantization) · *Engineering* (floating structure, lever arm, jam detection, weatherproofing) · *Environmental Science* (waterway pollution, EPR policy).

SALOK **traps, lifts, counts and reports.**

**Trap (Physics, Engineering).** A V-shaped boom of reused PET bottles and bamboo guides surface debris toward the bank, where it meets a bar screen at the foot of a sloped mesh ramp anchored to the bank or a bridge post. The estero's own current does the herding, so the boom needs no energy. A float-and-time test sets the boom angle for the estero's flow.

**Lift (Engineering).** A small geared DC motor turns a rake arm that sweeps debris up the ramp into a covered bin above the waterline. It runs only when the camera sees debris, for a few seconds at a time. The ESP32 reads the motor current, so a spike (a jam) makes the arm reverse and retry, and a full bin stops it and alerts the barangay. The arm is guarded, with a stop switch and a lockout during emptying; students never enter the water, and adults empty the bin weekly.

**See and count (Computer Science, Math).** An ESP32-S3 camera on a post looks *down at the water surface only*, so no faces or houses are in frame. A compact object-detection model, **quantized to INT8** and run with TensorFlow Lite for Microcontrollers, classifies each item. Training photos come from our own collections of real trash on the estero bank, labelled by students and checked by the adviser. Detections increment class counters stored on a microSD card. Each week students hand-count and weigh the bin's contents; a per-class average weight converts counts to kilograms, and the hand count is our accuracy test.

**Report (Design).** The ESP32 hosts an offline Wi-Fi page a phone can read, with no cellular needed. A script produces the weekly barangay report and the CSV. Brand names that a person can read from stored photos are tallied by a student volunteer; the AI flags and crops likely labels, because automated brand reading is not yet reliable.

**Secondary: warn (Physics).** A waterproof ultrasonic sensor on the same post measures the distance to the water surface, logs it against a painted staff gauge, and raises an alert (LED and report flag) when the level rises fast or the bin is nearly full.

**Power budget (Physics, Math).** *Planning arithmetic with stated assumptions, to be replaced by bench measurements:*
- Electronics, duty-cycled: about 0.3 W average, about 7 Wh/day.
- Arm: about 5 W for 10 s per lift, 20 lifts/day, about 0.3 Wh/day.
- Solar: a 6 W panel at about 3 effective sun-hours and 60% system efficiency, about 11 Wh/day.
- Storage: two 18650 cells, about 18 Wh.

This is a thin margin on cloudy days, so the device lengthens its capture interval when the battery is low; we report the measured numbers and size the panel to them.

**What it will and will not clean.** SALOK lifts **light floating and near-surface debris** that reaches the boom: bottles, sachets, bags, foam and cups, in small batches. It does not lift heavy or tangled items (the bar screen stops them and a person removes them), sunken waste, sediment, oil or dissolved pollution, and it cleans only the stretch upstream of the boom. We report the measured capture rate rather than claiming the estero is "clean".

*Figure 1: boom, ramp and arm layout. Figure 2: block diagram (boom → ramp and arm → bin; camera → model → counts → report; level sensor → alert). Figure 3: sample detections.*

**How the tiny AI works, in plain words.** A model that has seen thousands of photos of bottles, sachets and bags learns what each looks like. Quantization stores its numbers as small whole numbers so it fits on a PHP 1,300 chip that runs on a fraction of a watt from the sun, with no internet and nothing leaving the estero.

## 6. How will you implement this?

**Staged build with decision gates.** We never commit the whole budget before the previous stage works.
1. **Stage 1 (about PHP 1,600): bench.** ESP32-S3 camera, microSD and enclosure; train and test the model on our photos; measure real power draw. *Gate: held-out precision and recall meet the target.*
2. **Stage 2 (about PHP 2,500): passive trap.** Boom, bar screen, ramp, bin, post and solar power installed at the estero. *Gate: the boom holds through [N] rain events and weekly counts are within ±15% of hand counts.*
3. **Stage 3 (about PHP 1,550): arm and sensor.** Motor, driver, jam sensing and the level sensor. *Gate: the arm lifts debris on solar power alone with the target jam rate.*
4. Contingency PHP 350.

**Budget: PHP 6,000 (estimates; confirm local prices).**

| Item | PHP |
|---|---|
| ESP32-S3 camera board | 1,300 |
| microSD card | 200 |
| Sealed enclosure, glands, desiccant | 300 |
| Waterproof ultrasonic level sensor | 350 |
| Small solar panel (about 6–10 W) | 600 |
| Charge controller, 2× 18650 cells, holder, boost converter | 700 |
| Rope, net, zip ties (bottles and bamboo reused) | 450 |
| Anchor, post, clamps, concrete | 350 |
| Reused bin and painted staff gauge | 150 |
| Wiring, fuse, switch, connectors | 250 |
| Small geared DC motor (6–7.4 V) | 500 |
| Motor driver | 200 |
| Current sensing for jam detection | 150 |
| Ramp, rake arm, shaft, bar screen (recycled plastic, bolts) | 150 |
| **Subtotal** | **5,650** |
| Contingency | 350 |
| **Total** | **6,000** |

**Evidence we will show before Nov 2:** [N] labelled trash photos and a first detection screenshot; a photo of the bench prototype; one measured power figure; and the barangay's signed approval letter. *(Fill in only what exists.)*

**Timeline**
| Dates | Milestone |
|---|---|
| Oct 28 – Nov 2 | Site visit and barangay letter; photograph and label starter dataset; bench power test; submit |
| Nov 3 – Nov 20 | Stage 1 gate: train, quantize and test the model; baseline week at the estero |
| Nov 16 – Dec 5 | Refine with Samsung coaches (if shortlisted) |
| Dec 7 | Present model metrics, baseline data and Stage 2 progress |
| Dec – Feb | Stages 2 and 3; full pilot with weekly hand-count validation and barangay reports |
| By Mar 2027 | Build guide published; 1–2 more sites; Phase 2 conveyor if funded |

**Maintenance agreement.** A one-page memorandum names the barangay focal person who empties the bin weekly, the student team that clears jams, cleans the lens and uploads the data, and the school adviser who signs off the checklist: empty the bin, clear the bar screen, check the arm and ramp, wipe the lens, check the mooring, read the battery, upload the CSV. *[Confirm with the barangay before submission.]*

**Typhoon and theft plan.** A quick-release line and a rule to retrieve the electronics before a typhoon signal; the camera and controller mounted discreetly high on the post; barangay tanod informed.

**Stakeholders:** barangay captain and sanitation/environment officers (site, emptying, using reports), the LGU solid-waste office (data), our adviser and school head (supervision), students (build, label, count, report), residents (consent and awareness).

**Risks and mitigation**
- *Model fails in new light or water:* collect across times of day and weather, report held-out-location scores, keep the manual fallback count.
- *Arm jams or the battery drains:* bar screen, motor-current jam detection with auto-reverse, short bursts only when debris is seen, bench-tested lifts per day.
- *Arm fails entirely:* the boom, bar screen and bin still trap passively and the camera still counts, so the data pilot is not at risk.
- *Safety:* no student enters the water; guarded arm with lockout; adult-only emptying; barangay and school approval first.
- *Over-claiming:* targets stated as targets; we report what was measured and what failed.

## 7. Impact and long-term vision

**Success means** floating plastic physically lifted from a real estero and a weekly, trustworthy record of what it was, all for PHP 6,000.

**Measurable outcomes**
1. [TARGET] kg lifted over the pilot, with weekly weigh-ins, a measured capture rate and a baseline comparison.
2. Model precision and recall ≥ [0.85] on held-out locations; weekly count error within ±15% of hand counts.
3. A weekly barangay report series and a first brand-level audit of the estero.
4. A build guide and at least [1–2] additional sites by March 2027, each no more than PHP 6,000.
5. A logged record of level alerts (secondary).

**Sustainability.** The barangay runs it with local parts, solar power and a one-page checklist under a named maintenance agreement; no subscription, server or internet is needed; the dataset and model are open so other barangays can retrain on their own waste. Reused floats and bamboo keep replacement cheap.

**Long-term vision.** A student-built, barangay-owned network of low-cost SALOK units along connected esteros, feeding an open dataset that shows where plastic enters the waterway, which products dominate, and whether EPR commitments are changing what the water carries. Each added barangay makes every other unit's data more valuable, so impact grows faster than cost.

**Key takeaway.** Lifting plastic is not enough; proving what it is makes producers accountable. SALOK does both for the price of one cheap trap.

## References **[VERIFY each; add exact citations]**

Meijer et al. (2021). More than 1,000 rivers account for 80% of global riverine plastic emissions into the ocean. *Science Advances*.
Republic Act 11898, Extended Producer Responsibility Act of 2022.
[Local cleanup/brand audit source].
[A published river-plastic computer-vision monitoring study].
[A TinyML or object-detection source on low-power microcontrollers].

---

## How this maps to the rubric (self-assessment, not official)

| Criterion (weight) | How SALOK earns it |
|---|---|
| Design Innovation (20%) | The camera is both counter and trigger, so one chip lifts plastic and produces brand-level evidence; open, comparable community data. |
| Relevance to the Community (20%) | A real estero, a named barangay partner and letter, a current law, a problem residents see daily. |
| Feasibility (20%) | Staged build with decision gates, an itemized PHP 6,000 budget, power arithmetic, a passive fallback, and pre-submission evidence. |
| STEM Integration (15%) | Explicit STEM map; physics, statistics, computer science, engineering and environmental science all used. |
| Sustainability (15%) | Solar, reused parts, a written maintenance agreement, a typhoon plan, an open replicable design. |
| Clarity (10%) | One pitch sentence, two core jobs (lift and prove), flood warning clearly secondary. |

## Pre-submission checklist

- [ ] Choose the real estero; get the **signed barangay approval and maintenance memorandum**; fill `[SITE]` and `[BARANGAY]`.
- [ ] Photograph and label real trash (the more the better) and capture a sample detection image.
- [ ] Bench-measure the real power draw and replace the planning arithmetic.
- [ ] Take a photo of the bench prototype; list in "Evidence" only what exists.
- [ ] Verify every **[VERIFY]** fact and add exact citations.
- [ ] Confirm the ESP32-S3 board can run your model (RAM/PSRAM) before buying.
- [ ] Replace budget estimates with real local prices; keep the total within PHP 6,000.
- [ ] Trim to under 3,000 words, check against the official entry templates (the Drive connector could not list them) and export a PDF under 40 MB.
